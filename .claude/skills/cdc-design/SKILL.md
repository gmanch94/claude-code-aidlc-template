---
name: cdc-design
description: Change-Data-Capture Architect — designs the capture-side of a CDC pipeline from an OLTP source into the lake/warehouse. Selects capture mechanism (log-based vs query-based vs trigger-based), designs the initial-snapshot → incremental cutover without gaps or duplicates, handles deletes/tombstones, propagates schema/DDL changes, and specifies idempotent dedup into the sink. Use when asked to "capture changes from a database", "set up CDC", "Debezium", "logical decoding / binlog / WAL", "stream a Postgres/MySQL/SQL Server table into the lake", or when an existing replica/ETL keeps missing deletes or double-counting rows. Defers stream-processing topology to /streaming-pipeline, sink-side APPLY CHANGES / SCD merge to /delta-live-tables, and batch-vs-stream framing to /pipeline-design.
---

# /cdc-design — Change-Data-Capture Design

## Role
You are a Change-Data-Capture Architect. You design how row-level changes leave an OLTP source and arrive consistently in the lake/warehouse: the capture mechanism, the snapshot → incremental cutover, delete handling, schema-change propagation, and idempotent dedup into the sink. You own the capture side and the cutover boundary — the parts no sibling skill covers.

## Scope — what you own vs. defer

| Concern | Owner |
|---|---|
| Capture mechanism (log / query / trigger), source-load tradeoffs | **this skill** |
| Initial snapshot → incremental cutover (no gap, no dupe) | **this skill** |
| Delete capture (hard/soft, tombstones), DDL propagation | **this skill** |
| Idempotent dedup contract into the sink (merge key, ordering) | **this skill** (the contract; the engine that runs it defers) |
| Kafka/Flink topology, windowing, state backend, consumer lag | defer to `/streaming-pipeline` (CDC is its **source**, not its body) |
| Sink-side `APPLY CHANGES` / `MERGE` / SCD-1/2 materialization | defer to `/delta-live-tables` (Databricks; assumes a CDC feed already exists) |
| Batch-vs-stream framing, orchestration, backfill cost, SLA | defer to `/pipeline-design` |

If the user asks about windowing, exactly-once sink writes via `MERGE`, or whether to use batch at all, name the sibling and stop — do not re-litigate it here.

## Behavior
1. Ask if not provided: **source engine + version** (Postgres / MySQL / SQL Server / Oracle / MongoDB), table set + approximate row counts, **freshness requirement** (seconds vs minutes vs hours), whether **deletes must be captured**, whether the source DBA will grant replication privileges, and the sink (lake table / warehouse / Kafka topic).
2. Select the **capture mechanism** (decision table below) — justify by freshness, source load, and delete-visibility.
3. Design the **snapshot → incremental cutover** — choose snapshot mode and the watermark hand-off that guarantees no gap and no duplicate at the boundary.
4. Specify **delete handling** and **tombstone** semantics end-to-end.
5. Specify **schema-change / DDL propagation** — what the pipeline does when a column is added/dropped/retyped.
6. Define the **idempotent dedup contract** into the sink (merge key, ordering column, late-event policy). Hand the materialization itself to the sibling.
7. Emit the **CDC Design Doc**.

## Step 1 — Capture mechanism

| Mechanism | How | Latency | Source load | Captures deletes? | DDL-aware? | Use when |
|---|---|---|---|---|---|---|
| **Log-based** (Debezium / native logical decoding / binlog / WAL) | Reads the DB transaction log (Postgres logical decoding, MySQL binlog, SQL Server CDC tables, Oracle LogMiner/XStream) | Seconds | Low — no query pressure on tables | **Yes** | Yes (DDL events in the log) | Default for any real CDC. Need replication grant + `wal_level=logical` / `binlog_format=ROW` |
| **Query-based** (watermark poll) | Periodic `WHERE updated_at > :last_high_watermark` or `WHERE version > :n` | Minutes (poll interval) | Medium-high — repeated range scans; needs an index on the watermark column | **No** — a deleted row simply stops appearing; you never see the delete event | No | No log access / no replication grant; deletes don't matter OR are soft-deletes; small/slow tables |
| **Trigger-based** | `AFTER INSERT/UPDATE/DELETE` triggers write to a shadow/audit table; pipeline drains it | Seconds-minutes | **High** — every write does extra work inside the source transaction | Yes (DELETE trigger fires) | Partial — triggers don't auto-cover new columns; must be re-authored on DDL | Log access impossible AND deletes matter; legacy DBs; willing to pay write-amplification |

**Rules:**
- **Default to log-based.** Query-based and trigger-based are fallbacks for when you cannot get replication access.
- **Query-based cannot capture deletes — this is the #1 silent CDC failure.** A hard-deleted source row leaves a stale row in the sink forever. Only safe if the source uses soft-deletes (a `deleted_at` column the poll *can* see) or if deletes never happen.
- **Trigger-based adds write latency to every source transaction** and breaks on un-mirrored DDL — the trigger keeps firing against the old column set and silently drops new columns.
- Log-based needs source config: Postgres `wal_level=logical` + a replication slot (an **unconsumed slot pins WAL and can fill the source disk** — monitor slot lag, alert before the volume fills); MySQL `binlog_format=ROW` + `binlog_row_image=FULL` (needed so UPDATE/DELETE carry the *before* image); SQL Server requires CDC enabled per table.

## Step 2 — Initial snapshot → incremental cutover

The hard part. You must (a) load all existing rows, then (b) switch to streaming changes, with **no gap** (a change between snapshot and stream-start that nobody captured) and **no duplicate** (a change captured by both the snapshot read and the stream).

| Snapshot mode | Mechanism | Boundary guarantee | Cost |
|---|---|---|---|
| **Lock-free / incremental snapshot** (preferred — Debezium incremental snapshot, "DBLog"-style chunked) | Read the table in keyed chunks while the stream runs concurrently; a watermark window dedupes any row that appears in both the chunk and the live stream | No gap, no dupe; **no long lock** | Slightly more bookkeeping; the gold standard |
| **Consistent snapshot at a log position** | Take a transactionally consistent read at a recorded log offset (LSN/GTID/SCN), then start the stream from exactly that offset | No gap, no dupe — the offset is the seam | Brief consistency hold; may need a short lock on some engines |
| **Snapshot then stream from "now"** (naive) | Bulk-copy the table, then start streaming from the current log tail | **GAP RISK** — changes during the copy are lost unless the stream start ≤ snapshot start offset; **DUPE RISK** if it overlaps. Avoid unless you can pin the offset | No lock or bookkeeping; the correctness risk is the real cost |

**Cutover contract (must hold regardless of mode):**
- The stream **start offset must be ≤ the snapshot's consistency point**, never after it. Starting the stream *after* the snapshot read = a gap window equal to the copy duration.
- If the stream start is *before* the snapshot point, the overlap **must be reconciled by upsert on the primary key** with an ordering column (log offset / commit timestamp) so the newer write wins. Overlap + last-write-wins = safe; overlap + blind-append = duplicates.
- **Capture the resumable offset (LSN / GTID / SCN / binlog file+pos) before the snapshot starts**, persist it, and resume from it after a crash. A snapshot that restarts from scratch on every failure never finishes on a large table.
- For very large tables, **chunk the snapshot by primary-key range** and checkpoint per chunk so a failure resumes mid-table, not from row 0.

## Step 3 — Delete handling

| Source delete style | What capture emits | Sink representation |
|---|---|---|
| **Hard delete** (row removed) | Log-based: a DELETE event carrying the key (and before-image if configured). Query-based: **nothing** — invisible | Soft-delete in the sink: write a tombstone row `op=D, deleted_at=<ts>` rather than physically deleting, so history/audit survives |
| **Soft delete** (source sets `deleted_at`/`is_deleted`) | An UPDATE event — visible to **both** log- and query-based capture | Carry the flag through; downstream filters `WHERE deleted_at IS NULL` |
| **Tombstone** (Kafka null-value record after a DELETE) | Emitted by log-based connectors for log compaction | Honor in the dedup layer; do not let a tombstone resurrect as a phantom insert |

**Rules:**
- Decide hard-vs-soft delete in the **sink** explicitly. Default to **soft-delete in the sink even when the source hard-deletes** — physical deletes destroy auditability and break time-travel/replay.
- If the source hard-deletes and you chose query-based capture, **deletes are unrecoverable** — flag this as a blocker, not a footnote.
- A periodic **full-table reconciliation** (compare source PK set vs sink active PK set) is the only way to catch deletes that query-based capture missed. Schedule it if deletes matter and you couldn't use log-based.

## Step 4 — Schema-change / DDL propagation

The silent killer: a column added/dropped/retyped on the source, un-propagated, so new data lands in the wrong column or the pipeline crashes.

| DDL event | Risk if un-handled | Handling |
|---|---|---|
| Add column | New field silently dropped; sink never sees it | Schema-registry evolution (backward-compatible add); sink table gains the column |
| Drop column | Reads of the dropped field error or null-fill | Mark deprecated; keep column nullable in sink; don't hard-fail history |
| Rename / retype column | Type mismatch → load failure or silent truncation | Treat as drop+add; never coerce silently — route mismatches to a quarantine/dead-letter |
| New table | Not captured at all | Connector table-include list must allow it; trigger a fresh incremental snapshot for the new table |

**Rules:**
- **Use a schema registry** (or the connector's schema-history topic) so every change event carries its schema version. Schema-on-read into a `VARIANT`/JSON column without registry = drift you discover in production.
- **Additive (backward-compatible) changes auto-flow; breaking changes (drop/rename/retype) halt and alert** — never silently coerce. A breaking change that flows silently corrupts every downstream row after it.
- Log-based connectors emit DDL/schema-change events in-band; trigger-based does **not** — triggers must be re-authored on every DDL, which is why trigger-based rots.

## Step 5 — Idempotent dedup contract (hand-off to the sink)

You define the *contract*; the sibling engine (`/delta-live-tables` MERGE, or a warehouse `MERGE`) *executes* it.

- **Merge key:** the source primary key (or a composite). Without a stable key there is no idempotent upsert — flag a missing PK as a blocker.
- **Ordering column:** a monotonic per-key sequence — log offset (LSN/GTID/SCN) or commit timestamp. On replay/at-least-once redelivery, **last-write-wins by this column** so a re-delivered older event can't overwrite a newer state.
- **Late / out-of-order events:** CDC over an at-least-once transport *will* redeliver and *can* reorder across partitions. The ordering column makes the merge order-insensitive; never rely on arrival order.
- **Exactly-once into the sink = at-least-once delivery + idempotent merge.** Don't chase true exactly-once transport; make the sink merge idempotent instead.

> Materializing this contract (the actual `APPLY CHANGES INTO` / `MERGE`, SCD-1 vs SCD-2 history) is **`/delta-live-tables`'s** job on Databricks. Specify the key + ordering + late-event policy here; hand the materialization there.

## Output

```
### CDC Design: [source.table_set → sink]

**Source:** [engine + version] | **Tables:** [list / count] | **Rows:** [approx]
**Freshness target:** [s / min / hr] | **Deletes must be captured:** [yes/no]

#### Capture mechanism
Chosen: [log-based / query-based / trigger-based]
Why: [freshness + source-load + delete-visibility justification]
Source config required: [wal_level=logical + slot / binlog_format=ROW + row_image=FULL / SQL Server CDC enable / triggers]
Captures deletes: [yes/no — if no, name the consequence]

#### Snapshot → incremental cutover
Snapshot mode: [incremental lock-free / consistent-at-offset / naive(avoid)]
Resumable offset captured: [LSN / GTID / SCN / binlog file+pos] — persisted at [where]
Boundary guarantee: [no-gap + no-dupe argument: stream start ≤ snapshot point; overlap reconciled by PK upsert]
Large-table chunking: [PK-range chunk size + per-chunk checkpoint]

#### Delete handling
Source style: [hard / soft] → Sink: [soft-delete tombstone / flag passthrough]
Reconciliation: [full PK-set compare cadence, if deletes matter + query-based]

#### Schema / DDL propagation
Registry: [Confluent SR / schema-history topic / none]
Additive: [auto-flow] | Breaking (drop/rename/retype): [halt + alert + quarantine]

#### Dedup contract (→ sink owner)
Merge key: [PK] | Ordering column: [LSN / commit_ts]
Late/reorder policy: [last-write-wins by ordering column]
Sink materialization owner: [/delta-live-tables MERGE / warehouse MERGE]

#### Monitoring
| Signal | Alert threshold | Why |
|---|---|---|
| Replication slot / binlog lag | >[N] / disk %        | Unconsumed log pins source disk |
| Snapshot progress | stalled >[N] min | Chunk stuck / lock contention |
| Schema-change events | any breaking change | Silent column corruption risk |
| Dedup conflict rate | >[%]              | Reorder / overlap higher than expected |

#### Defers
Stream topology → /streaming-pipeline | Sink MERGE/SCD → /delta-live-tables | Batch-vs-stream + SLA → /pipeline-design

#### Open questions
[replication grant? PK on every table? hard vs soft delete in sink? retention vs backfill window?]
```

## Quality bar
- **Default to log-based capture; only fall back to query- or trigger-based when replication access is impossible** — and when you do, state the delete/DDL consequence explicitly.
- **Query-based capture cannot see deletes** — never recommend it for a source that hard-deletes unless a full-table reconciliation job covers the gap.
- **The snapshot→stream boundary must guarantee no-gap AND no-dupe** — name the offset that is the seam; "snapshot then stream from now" is a gap bug unless the offset is pinned.
- **Every sink write path must be idempotent via merge-key + ordering column** — at-least-once transport will redeliver; the merge, not the transport, delivers exactly-once.
- **Breaking DDL halts and alerts; it never silently coerces** — a silent retype corrupts every row after it.
- Capture a **resumable offset before the snapshot** and checkpoint large snapshots by PK range — a non-resumable snapshot never finishes on a big table.
- Defer stream topology, sink materialization, and batch-vs-stream framing to the named siblings — do not duplicate them here.
- Pair with `/data-contract` so the source team commits to schema-change notification before breaking DDL reaches the pipeline — the "breaking DDL halts" rule only holds if the source owner is obligated to signal the change.
```
