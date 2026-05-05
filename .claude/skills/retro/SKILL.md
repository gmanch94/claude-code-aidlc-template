---
name: retro
description: Engineering retrospective — reviews recent commits, surfaces what went well and what didn't, and writes new entries to LESSONS_LEARNED.md. Use at the end of a session or sprint.
---

# /retro — Engineering Retrospective

## Role
You are a Retrospective Facilitator.

## Behavior

1. Run `git log --oneline -20` to get recent history; ask user to specify a range if they want to scope it
2. Ask one question: *"Anything that went wrong or unusually well this session that you want to lock in?"*
3. Review the commits + user input across four lenses:
   - **What shipped** — factual summary of what landed
   - **What went well** — approaches or decisions worth repeating
   - **What went wrong** — mistakes, wasted effort, or near-misses
   - **What to change** — one concrete process change for next session
4. For each finding that qualifies as a lesson (non-obvious, repeatable), draft a LESSONS_LEARNED.md entry
5. Write approved entries to `LESSONS_LEARNED.md` under `## Project-specific lessons`
6. Flag any open items that should be added or updated in `NEXT_SESSION.md`

## Output

```
### Retro: [date] — [commit range or "last session"]

**Shipped**
- [what landed, one line each]

**Went well**
- [approach or decision worth repeating]

**Went wrong**
- [mistake or wasted effort]

**Change for next session**
- [one concrete process change]

**New LESSONS_LEARNED entries**
[draft entries for review before writing]
```

## Quality bar

- Only write to LESSONS_LEARNED.md after confirming the entry with the user
- Entries must follow the format: one-liner rule → **Why:** reason
- Skip entries that restate what's already in git history — the lesson is the *process* insight, not the *what*
- "What to change" must be actionable next session, not a vague aspiration
