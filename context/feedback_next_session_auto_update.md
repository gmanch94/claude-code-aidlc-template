---
name: Auto-update NEXT_SESSION.md after merging PRs
description: Update NEXT_SESSION.md immediately after every merged PR — do not wait for user to ask
type: feedback
---

Always update NEXT_SESSION.md after merging a PR without waiting for the user to ask. Commit and push it as part of the same work unit.

**Why:** User had to prompt for this multiple times in a session. It should be automatic.

**How to apply:** After every `gh pr merge`, immediately update HEAD, git log snapshot, and "what landed" in NEXT_SESSION.md, then commit + push.
