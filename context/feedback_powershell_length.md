---
name: PowerShell command length limit
description: Long PS commands (hashtables, multiline blocks) hit a parse limit and get rejected
type: feedback
---

Keep PowerShell commands short. Avoid large hashtables or long multiline blocks inline.

**Why:** PS command string hits ~948-byte parse limit — user rejects the tool call.

**How to apply:** Use regex/loops instead of explicit maps. Split into multiple short commands if needed. Same rule applies to commit messages — use inline `-m "..."` not here-strings.
