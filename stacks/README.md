# stacks/ — Stack-Specific Add-ons

The base template is stack-agnostic. This directory contains drop-in additions for specific languages and frameworks.

## What's here

| Stack | Skills added | Settings snippet | CLAUDE.md addendum |
|---|---|---|---|
| [`python/`](python/) | `/test-gen`, `/type-fix`, `/deps-audit` | Python linting/type-check allowlist | Python conventions block |

## How to adopt a stack

**1. Copy the skills**

```bash
cp -r stacks/python/skills/* .claude/skills/
```

**2. Merge the settings snippet**

Add entries from `stacks/python/settings-snippet.json` into `.claude/settings.json` `permissions.allow`. De-duplicate as needed.

**3. Paste the CLAUDE.md addendum**

Copy `stacks/python/claude-md-addendum.md` content into your project's `CLAUDE.md`. Fill in the placeholders.

## How to add a new stack

1. Create `stacks/<stack>/`
2. Add `skills/<name>/SKILL.md` for each skill (frontmatter with `name` + `description`)
3. Add `settings-snippet.json` with read-only allowlist entries (no interpreter wildcards)
4. Add `claude-md-addendum.md` with stack-specific CLAUDE.md content
5. Update this README table
