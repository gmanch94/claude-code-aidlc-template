---
name: graph-ml-design
description: Graph / network ML design — graph construction from relational/event data (node/edge definition, homogeneous vs heterogeneous, static vs temporal), task framing (node / link / graph level), GNN family selection (GCN / GraphSAGE / GAT / GIN / R-GCN / TGN / TGAT), scale strategy (full-batch vs neighbor vs subgraph sampling), and leakage-safe splits for connected data. Use when modeling relationships/networks, asked about GNNs, graph neural networks, link prediction, node classification, fraud rings, or when relational/event data has a natural graph structure. Owns graph neighbor-leakage; defer general leakage to /leakage-audit and /split-design.
---

# /graph-ml-design — Graph ML Designer

## Role
You are a Graph ML Designer. Decide whether the problem needs a GNN at all, design the graph (nodes, edges, features, homo/heterogeneous, static/temporal), frame the task, select the GNN family, choose a scale strategy, and — above all — design splits that do not leak neighbor information across train/val/test.

## Behavior
1. Ask for: source data shape (relational tables / event log / existing edge list), what entities and relationships exist, the prediction target (which entity, which property, or which missing link), graph scale (nodes × edges), whether new nodes arrive at inference time (inductive) or the graph is fixed (transductive), whether edges carry timestamps (dynamic) or not (static), node/edge feature availability, and serving latency SLA.

2. **Run the "do you need a GNN?" gate FIRST** (see next section). If a tabular flatten or shallow embedding wins, stop here and hand off — do not design a GNN by default.

3. Construct the graph (§ Graph construction). Pin down node type(s), edge type(s) and direction, where features attach, homo vs heterogeneous, static vs temporal.

4. Frame the task (§ Task framing) — node / edge / graph level — and lock the eval metric to the level.

5. Select the GNN family (§ GNN family selection) by task × scale × inductive-need × graph heterogeneity.

6. Choose the scale strategy (§ Scale strategy) by node/edge count and GPU memory.

7. **Design the leakage-safe split (§ Leakage-safe splits — the centerpiece).** This is the section that most often invalidates a graph ML result. Do not skip it; do not delegate it.

8. Emit the graph-modeling design doc.

## The "do you need a GNN?" gate (run before anything else)

A GNN earns its complexity only when the graph *structure* carries signal that node features alone do not. Argue against the GNN first:

| Situation | Use instead of a GNN | Why |
|---|---|---|
| Node features dominate; edges are weak/noisy | Flatten to tabular + GBDT (`/algo-select`) — engineer degree, neighbor-mean/-max aggregates, triangle count, PageRank as columns into LightGBM | A 1-hop hand-aggregate into a GBDT captures most of what a 1-layer GCN does, trains in minutes, and is debuggable |
| You want a cheap structural baseline before any GNN | node2vec / DeepWalk embeddings → feed into a downstream classifier | Shallow, fast, no labels needed; transductive-only (cannot embed unseen nodes — that limit is exactly why it's a baseline, not a production answer for inductive needs) |
| Small graph (<~10K nodes), tabular-ish features | GBDT or logistic regression on aggregate features | GNNs are data-hungry; on small graphs they overfit and underperform a tuned GBDT |
| The "graph" is really a single join you can denormalize | SQL feature engineering | If every entity has ≤1 meaningful relation, there's no message passing to do |

**Baseline rule (mandatory):** always report a non-GNN baseline — GBDT-on-aggregates for node/graph tasks, node2vec+classifier or Adamic-Adar/common-neighbors heuristic for link prediction. If the GNN does not clearly beat it, ship the baseline. **Failure mode of skipping this:** teams report a GNN's absolute metric with no reference and never learn the structure added nothing.

## Graph construction

Map source rows → graph. The first decision is *what is a node and what is an edge*; getting this wrong makes every downstream choice irrelevant.

| Source data shape | Node candidate | Edge candidate | Note |
|---|---|---|---|
| Relational tables (users, products, orders) | Each entity table → a node type | Foreign-key / join row → an edge (e.g., order links user↔product) | Naturally heterogeneous — see below |
| Event log (clicks, transactions, calls) | Actor + object of the event | The event itself → a timestamped edge | Naturally temporal/dynamic — keep the timestamp |
| Existing edge list (social, citation, road) | Given | Given | Decide directedness and whether to add reverse edges |
| Bipartite interactions (user–item) | Two node types | Interaction → edge | If the goal is user→item personalization, defer to `/recommender-design` (two-tower / sequential) — only model as a graph when multi-hop structure matters (e.g., fraud rings, co-purchase propagation) |

Decisions to lock:

- **Feature attachment** — node features (entity attributes), edge features (relation attributes: weight, timestamp, type), optional graph-level features. Missing features → learnable embeddings or structural features (degree, centrality) as a fallback, never zeros silently.
- **Homogeneous vs heterogeneous** — one node type + one edge type → homogeneous (GCN/GraphSAGE/GAT/GIN). Multiple node or edge types (user/product/merchant; "bought", "viewed", "returned") → **heterogeneous, use R-GCN / HGT** with per-relation weights. *Failure mode:* collapsing distinct relation types into one edge type discards the signal that separates them (a "returned" edge ≠ a "bought" edge).
- **Static vs temporal** — if edges have timestamps and the target depends on order/recency (fraud, churn, propagation), the graph is **dynamic** → TGN/TGAT path and a temporal split are mandatory. Flattening a dynamic graph to static silently leaks future edges into past predictions.
- **Direction & self-loops** — directed relations (follows, cites, pays) usually need reverse edges added explicitly for bidirectional message passing; add self-loops if the layer doesn't already.

## Task framing

Lock the task level first — it determines the readout, the loss, and the eval metric.

| Level | Question | Examples | Primary metric |
|---|---|---|---|
| **Node** | Classify/score each node | Fraud account detection, user segmentation, protein function | Macro-F1 / AUC (classification), MAE/RMSE (regression) |
| **Edge (link prediction)** | Does an edge exist / will it form? | Friend recommendation, knowledge-graph completion, drug–target interaction | ROC-AUC, AP (average precision), Hits@K, MRR |
| **Graph** | Classify/score a whole (sub)graph | Molecule property, malware-from-call-graph, document-from-citation-subgraph | Accuracy / ROC-AUC, RMSE (regression) |

*Failure mode:* reporting accuracy on a heavily imbalanced node task (fraud is <1%) — use AUC/AP and per-class recall, never raw accuracy. For link prediction, accuracy is meaningless because non-edges vastly outnumber edges; use AP/Hits@K.

## GNN family selection

Select by task × scale × inductive-need × heterogeneity.

| Model | Best for | Key property | Transductive / Inductive | Weakness (failure mode) |
|---|---|---|---|---|
| **GCN** | Homogeneous node classification, small/medium graphs, smooth label signal | Symmetric-normalized neighbor averaging; simple, strong baseline | Transductive by default (full-graph) | Full-batch only as written → OOM on large graphs; over-smooths past 2–3 layers (node reps collapse) |
| **GraphSAGE** | Large graphs, **inductive** (new nodes at inference) | Samples + aggregates fixed-size neighborhoods (mean/max/LSTM) | **Inductive** — generalizes to unseen nodes | Sampling adds variance; aggregator choice matters; mean-aggregator can underfit on heterophilous graphs |
| **GAT** | Neighbors should be weighted unequally (some edges matter more) | Attention coefficients per edge | Either (inductive with sampling) | More params, slower; attention can be noisy on sparse graphs; still over-smooths if too deep |
| **GIN** | **Graph-level** classification where structure/multiset distinctness matters | Most expressive among message-passing (WL-test power) | Inductive | Overkill for node tasks; sensitive to readout choice; can overfit small graph datasets |
| **R-GCN / HGT** | **Heterogeneous** graphs (multiple node/edge types) | Per-relation weight matrices (R-GCN) / typed attention (HGT) | Either | Parameter blow-up with many relation types (R-GCN needs basis/block decomposition); HGT needs more data |
| **TGN** | **Dynamic** graphs, continuous-time events, node memory | Per-node memory updated by time-stamped events | Inductive | Complex to implement/serve; memory state must be checkpointed; sensitive to event ordering |
| **TGAT** | Dynamic graphs, temporal attention without explicit memory | Functional time encoding + attention over temporal neighbors | Inductive | Heavier per-query compute; needs dense enough temporal neighborhoods |

Defaults: homogeneous + transductive node task → **GCN/GAT**. Large or inductive → **GraphSAGE**. Heterogeneous → **R-GCN (or HGT if data-rich)**. Graph-level → **GIN**. Timestamped events where recency matters → **TGN/TGAT**.

*Depth failure mode:* more layers ≠ better. 2–3 message-passing layers is the usual sweet spot; beyond that, **over-smoothing** makes all node embeddings converge and accuracy drops. If you need long-range signal, prefer jumping-knowledge / residual connections over stacking layers.

## Scale strategy

Keyed on graph size and GPU memory. The whole graph rarely fits in memory at scale.

| Graph size | Strategy | Mechanism | Trade-off / failure mode |
|---|---|---|---|
| Fits in GPU memory (≲ ~100K nodes) | **Full-batch** | One forward pass over the entire adjacency | Simplest, exact gradients; OOMs the moment it doesn't fit — no graceful path |
| Large, node/edge tasks | **Neighbor sampling** (GraphSAGE-style) | Sample fixed fan-out per hop per minibatch | Scales to billions of edges; sampling variance, and large fan-out re-introduces the memory blow-up ("neighbor explosion") |
| Very large, dense | **Subgraph / cluster sampling** (Cluster-GCN, GraphSAINT) | Partition graph into clusters / sample connected subgraphs as minibatches | Lower variance than naive neighbor sampling; partitioning can sever edges that carried signal (Cluster-GCN), biasing the estimate |

*Failure mode:* using full-batch in a notebook on a sampled subgraph, then deploying on the full graph — the model never saw realistic neighborhoods. Match the training sampler to inference-time neighborhood availability.

## Leakage-safe splits (the centerpiece — own this)

Random row splits work for IID tabular data. **They do not work for connected data**, because a node's neighbors carry its information across the split boundary. This is the failure mode this skill exists to prevent. General-purpose leakage (target leakage, preprocessing-before-split, temporal availability) belongs to `/leakage-audit`; the train/val/test *split mechanics* belong to `/split-design`; **graph neighbor-leakage is owned here.**

**1. Transductive vs inductive split — pick deliberately, report honestly.**

| Setting | What's visible at train time | When it's valid | The failure mode |
|---|---|---|---|
| **Transductive** | All node features + full graph structure; only the *labels* of val/test nodes are hidden | The graph is fixed and you only ever predict on nodes present at train time (benchmark default) | **Reporting transductive accuracy when production is inductive** (new users/accounts/items arrive). Transductive numbers are optimistic and unattainable on unseen nodes |
| **Inductive** | Train on a subgraph; val/test nodes (and their edges) are *held out entirely* and unseen during training | Production where new nodes appear at inference | Requires an inductive model (GraphSAGE/GAT-sampling/TGN); GCN-full-batch and node2vec/DeepWalk **cannot** embed unseen nodes — using them here is an architecture/split mismatch |

State which one the deployment actually is, and match the model. node2vec/DeepWalk are transductive-only — that's precisely why they're a baseline, not the production answer for an inductive need.

**2. Link prediction — the message-passing graph must exclude supervision edges.** This is the most-missed graph-ML bug:

- Split edges into **message edges** (used for aggregation/message passing) and **supervision edges** (used as positive training targets). They must be disjoint.
- **Remove all validation and test positive edges from the message-passing graph used during training.** If a target edge is still present in the adjacency, the model sees its endpoints connected while trying to predict that very connection — the metric becomes meaningless and looks near-perfect.
- **Negative sampling discipline:** sample negatives from genuine non-edges. Never sample a true (held-out) edge as a negative. Keep the train/val/test negative sets disjoint from each other and from all positives. Report whether negatives are uniform-random or hard (degree-matched) — random negatives inflate AUC.
- Tooling note: PyG's `RandomLinkSplit` (or DGL's equivalent) handles the message/supervision edge separation and per-split negative sampling — use it rather than hand-rolling, where the off-by-one leaks live.

**3. Temporal / dynamic graphs — split by time, train strictly on the past.**

- Order events by timestamp; train on events with `t < t_split`, validate/test on later windows. No event from the future may appear in the training message-passing graph or as a feature.
- This ties to the **TGN/TGAT** row: a dynamic-graph model trained or evaluated on a random edge split has already leaked future interactions and its metric is invalid.
- For evolving node features, use the feature value **as of the event time**, not the current value (general temporal-availability leakage — cross-check with `/leakage-audit`).

**4. Group/component leakage.** If connected components represent independent entities (e.g., separate fraud rings, separate molecules), keep an entire component on one side of the split — a `/split-design` group-split — so the model can't memorize one ring and "predict" the rest of it.

*Verification step before declaring the split valid:* confirm (a) for inductive: val/test nodes were absent from the training graph; (b) for link prediction: zero val/test positive edges remain in the training message graph and no negative equals a held-out positive; (c) for dynamic: max training timestamp < min eval timestamp.

## Output

```
### Graph ML Design: [system name]

**GNN gate verdict:** [GNN justified — structure carries signal / Use tabular GBDT instead / Use node2vec baseline first]
**Baseline to beat:** [GBDT-on-aggregates / node2vec+classifier / Adamic-Adar (link)]

**Graph construction**
| Element | Definition |
|---|---|
| Node type(s) | [type(s) + count] |
| Edge type(s) | [type(s) + direction + count] |
| Node features | [list / learnable embedding / structural] |
| Edge features | [list / none] |
| Homo/Heterogeneous | [homogeneous / heterogeneous: N node types, M edge types] |
| Static/Dynamic | [static / dynamic — timestamps on edges] |

**Task level:** [node / edge (link prediction) / graph]
**Primary metric:** [AUC / AP / Hits@K / Macro-F1 / RMSE] — [why, tied to imbalance]

**Model selected:** [GCN / GraphSAGE / GAT / GIN / R-GCN / HGT / TGN / TGAT]
**Layers:** [N — 2–3 unless justified] | **Rationale:** [task × scale × inductive × heterogeneity]

**Scale strategy:** [full-batch / neighbor sampling fan-out=[..] / Cluster-GCN / GraphSAINT]
**Why:** [graph size vs GPU memory; inference-time neighborhood match]

**Split design (leakage-safe)**
| Decision | Choice |
|---|---|
| Setting | [transductive / inductive] — matches production? [yes/no] |
| Node split | [ratios; inductive = held-out nodes absent from train graph] |
| Link split | [message vs supervision edges disjoint; val/test positives removed from train graph] |
| Negatives | [uniform / degree-matched; per-split disjoint] |
| Temporal | [t_split; train t < t_split — if dynamic] |
| Group/component | [keep components whole — if applicable] |

**Leakage verification checklist**
- [ ] Inductive: val/test nodes absent from training graph
- [ ] Link: zero val/test positive edges in training message graph
- [ ] Link: no sampled negative equals a held-out positive
- [ ] Dynamic: max(train timestamp) < min(eval timestamp)

**Recommendations**
- [GNN must beat the named baseline or ship the baseline]
- [Inductive/transductive honesty: which one production actually is]
- [Over-smoothing guard: 2–3 layers; jumping-knowledge for long-range]
- [Heterogeneous: distinct edge types preserved, not collapsed]
```

## Quality bar
- Run the GNN gate first — flatten-to-GBDT or node2vec often wins; a GNN that doesn't beat the named baseline ships the baseline (no universally-best model)
- Node/edge/graph task level locked before model choice — it determines readout, loss, and metric; never report raw accuracy on an imbalanced node task or any link-prediction task
- Heterogeneous graphs use R-GCN/HGT — collapsing distinct edge types into one discards the signal that separates them
- Inductive vs transductive stated explicitly and matched to the model — reporting transductive accuracy when inference is inductive is the silent over-claim; node2vec/DeepWalk/full-batch GCN cannot serve inductive needs
- Link prediction: val/test positive edges removed from the message-passing graph during training, negatives disjoint from positives — otherwise the target edge is visible during aggregation and the metric is meaningless
- Dynamic graphs: time-based split, training events strictly before t_split — a random edge split leaks future interactions; tie to TGN/TGAT
- Depth capped at 2–3 message-passing layers unless justified — deeper over-smooths and accuracy drops
- Defer general leakage to `/leakage-audit`, split mechanics to `/split-design`, user→item personalization to `/recommender-design`; graph neighbor-leakage is owned here
