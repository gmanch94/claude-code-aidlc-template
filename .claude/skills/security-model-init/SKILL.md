---
name: security-model-init
description: Create a docs/SECURITY_MODEL.md template for the current project, customised to its detected stack. Forces upfront thinking about (1) auto-generated endpoint surfaces, (2) auth roles, (3) sensitive operations, (4) per-(op × role × surface) enforcement, (5) static CI checks. Use as commit #2 on new projects (after README, before any code) — converts the think-first protocol from "remember to apply" to "the doc gates the next commit". For existing projects: backfill it to surface gaps without needing the audit agent.
---

# security-model-init

Generates `docs/SECURITY_MODEL.md` (or `SECURITY.md` if conventions prefer that) in the current repo, pre-filled with stack-specific scaffolding. The user fills in the table — that's the work.

## When to invoke

- **New project, commit #2.** After README, before any code. Blocks coding until the table has no empty cells.
- **Existing project, backfill.** Run once per repo, fill the table from the current state. The act of filling will surface gaps — those become a security-hardening backlog.
- **After a stack change.** New auth provider, new ORM, switching from REST to GraphQL — re-run to capture the new attack surfaces.

## Steps

1. **Detect stack.** Look for: `supabase/migrations/`, `firebase.json`, `firestore.rules`, `hasura/metadata/`, `prisma/schema.prisma`, `amplify/backend/`, `package.json` deps (`@supabase/*`, `firebase`, `@hasura/*`, `@aws-amplify/*`, `@clerk/*`, `next-auth`, etc.). Default to "generic" if no signal.

2. **Detect target file path.** Convention: `docs/SECURITY_MODEL.md` if `docs/` exists; else `SECURITY_MODEL.md` at repo root.

3. **Refuse to overwrite.** If the file exists, surface to the user with the path and ask before clobbering. Offer "regenerate scaffold but preserve filled cells" as an option.

4. **Write the template** with stack-specific defaults pre-filled in the questions sections. The TABLE itself stays blank — the user fills it.

5. **Surface next steps:** "Fill the empty cells in §4. Each empty cell is a known gap. CRITICAL gaps must be closed before launch."


## Template source

Read [`templates/security-model/SECURITY_MODEL-TEMPLATE.md`](../../../templates/security-model/SECURITY_MODEL-TEMPLATE.md) and write its contents to the target file. The template includes commented stack-specific scaffolding blocks (`<!-- SUPABASE -->`, `<!-- FIREBASE -->`, `<!-- HASURA -->`, `<!-- EXPRESS-FASTAPI-FLASK -->`). Uncomment the block matching the detected stack; delete the others.

Replace `[PROJECT NAME]` with the actual project name (read from package.json, pyproject.toml, or root README's H1).

## Output

Write the file. Surface to user:

- File path written
- Detected stack and which scaffolding block was retained
- Reminder: "Fill §3, §4, §5 before next commit. Empty cells in §4 are known gaps — they must move to §6 with a target close date OR be filled."
- Suggest: "Run `/security-audit` after filling to verify the table matches reality."

## What this skill does NOT do

- Does NOT fill §3, §4, §5 for you. The act of filling is the work — an LLM-generated table will be plausible-sounding and wrong in the cells that matter.
- Does NOT overwrite an existing SECURITY_MODEL.md. If one exists, surface to user and offer "regenerate scaffold but preserve filled cells" as an explicit option.
