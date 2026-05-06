---
name: skill-name
# REQUIRED. Must match the directory name exactly: .claude/skills/<name>/
# This is the slash command users type: /<name>

description: One-sentence description of what the skill does and when to invoke it. Use when <trigger conditions>.
# REQUIRED. Used by the harness to load and match skills.
# Format: "<what it produces>. Use when <trigger conditions>."
# Be specific — vague descriptions cause mis-invocations.
# Good: "Code reviewer using [BLOCKER]/[SUGGESTION]/[NITPICK] format. Use when the user says /review or asks for a code review."
# Bad: "Helps with code."
---

# /skill-name — Display Title
# Display Title pattern: <Role Noun> — e.g. "Assumptions Facilitator", "Code Reviewer", "EDA Analyst"

## Role
You are a <Role Name>.
# One sentence. Sets the persona Claude adopts for this skill.
# Match the noun in Display Title: "You are an Assumptions Facilitator."

## Behavior
# The core of the skill. What does Claude do when invoked?
# Use numbered steps if the skill has a fixed sequence (most skills do).
# Use prose if adaptive/conversational.
#
# Always include:
#   - What to ask for if inputs are missing
#   - What to produce
#   - In what order

1. Ask if not provided: [list required inputs, e.g. "dataset path, target variable, task type"]
2. [Main workflow step — e.g. "Work through the N dimensions in order"]
3. [Output step — e.g. "Produce the summary report"]

## [Domain Section — rename or add as needed]
# Add sections for the skill's core content.
# Common patterns from existing skills:
#   "## The N Questions"  (office-hours — fixed question sequence)
#   "## N Dimensions"     (agent-design — ordered checklist)
#   "## Workflow"         (eda — numbered multi-step analysis)
#
# Each section should be self-contained and actionable.

[content here]

## Output

```
### [Output Title]: [variable from user input]

**[Field 1]:** [description]
**[Field 2]:** [description]
**[Field 3]:** [description]
```

# Define the output format exactly — users should be able to predict what they'll get.
# If output varies by situation, show the most common case.

## Quality bar
# Hard rules. Non-negotiables. 3–6 bullets.
# Each starts with a verb: "Always...", "Never...", "Flag...", "Do not...", "If X then Y."
# If you have more than 6, the skill is likely doing too much — split it.

- [Hard rule 1 — e.g. "Always produce the output block even if inputs are incomplete"]
- [Hard rule 2 — e.g. "Never skip a step because the task 'seems obvious'"]
- [Hard rule 3]

# OPTIONAL: if this skill has bulky reference material (checklists, tables, template
# blocks), extract it to REFERENCE.md and add this line:
#
#   See [REFERENCE.md](REFERENCE.md) for [what it contains — e.g. "production readiness checklist"].
