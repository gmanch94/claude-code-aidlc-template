# /skill-name — Reference
# OPTIONAL file. Use when SKILL.md would exceed ~60 lines due to checklists,
# tables, or template blocks that are needed at invocation time but would
# clutter the core behavior spec.
#
# No frontmatter — this file is loaded as supplementary context, not a
# standalone skill.
#
# Link from SKILL.md with:
#   See [REFERENCE.md](REFERENCE.md) for <what it contains>.

## [Checklist Section]
# Common use: production readiness gate, pre-deploy checklist, review checklist.

- [ ] [Checklist item]
- [ ] [Checklist item]
- [ ] [Checklist item]

## [Table Section]
# Common use: tool manifests, risk registers, decision matrices.

| Column A | Column B | Column C |
|----------|----------|----------|
| | | |

## [Template Block Section]
# Common use: output templates, structured formats the skill references.

```
[template content here]
```
