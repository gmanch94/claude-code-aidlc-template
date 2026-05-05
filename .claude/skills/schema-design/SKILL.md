---
name: schema-design
description: Designs data schemas for analytical and operational systems — dimensional modeling, schema evolution strategy, partitioning, SCD types, and OLTP vs. OLAP trade-offs. Use when designing a new data model, planning a schema migration, or reviewing an existing schema for performance or maintainability issues.
---

# /schema-design — Data Schema Design

## Behavior
1. Identify use case: OLTP vs. OLAP vs. hybrid
2. Apply modeling pattern decision tree
3. Define schema evolution strategy
4. Specify partitioning and clustering
5. Flag SCD requirements per dimension

## Modeling pattern decision tree

```
Primary use case?
  Transactional (writes, row-level ops)    → 3NF / normalized relational
  Analytical (aggregations, wide reads)   →
    Query patterns known + predictable    → Star schema (fact + dims)
    Query patterns varied / exploratory   → Wide flat table / OBT (One Big Table)
    Hierarchical / graph relationships    → Nested / repeated fields (BigQuery/Parquet)
```

## Design checklist

**Structure**
- [ ] Surrogate keys used in DW — never use source system natural keys as PK (they change)
- [ ] Foreign key relationships explicit even if not enforced
- [ ] Nullable columns justified — null = "unknown," not "not applicable" or "zero"
- [ ] Constrained fields use lookup tables or CHECK constraints

**Evolution**
- [ ] Additive changes only — add columns; never rename/remove without deprecation period
- [ ] Schema migration tool in place (Flyway, Liquibase, dbt schema changes)
- [ ] Breaking change policy defined: approval owner, notice period, consumer migration plan

**Performance**
- [ ] Partition key matches the dominant filter in expected queries (date is most common)
- [ ] Clustering / sort key matches secondary filter or GROUP BY columns
- [ ] Tables > 50 columns: consider vertical partitioning by access frequency

**SCD handling** (see REFERENCE.md for type details)
- [ ] SCD type identified per slowly-changing dimension
- [ ] Effective date / expiry date columns present for Type 2
- [ ] "Current record" query pattern defined (is_current flag or MAX surrogate key)

## Output format

```
### Schema Design: [table / domain]

#### Model
[table name(s), columns, types, constraints, PK/FK]
Pattern: Star schema / 3NF / OBT / nested

#### Partitioning
Partition by: [column] — because [query pattern it serves]
Cluster by: [column(s)]

#### Schema evolution policy
Breaking changes: [approval process + notice period]
Tool: [Flyway / Liquibase / dbt]

#### SCD strategy
[per-dimension: Type 0/1/2/3 + rationale]

#### Open questions
[source keys, nullability decisions, enum lists, retention]
```

## Quality bar
- Never use a source system natural key as DW PK — they change and orphan foreign keys
- Partition key is the most important performance decision — wrong key = full table scans
- SCD Type 2 is the default; document explicitly when you choose a different type
- See REFERENCE.md for SCD comparison table and partitioning patterns
