---
description: Capture durable knowledge from this session into CLAUDE.md and memory
---

Review this session for durable, non-obvious facts worth persisting, so a future
session does not start from zero.

Update, as appropriate:

- The project `CLAUDE.md` for workflow, conventions, and gotchas that apply to
  every session.
- Project memory (the `memory/` dir): one fact per file with frontmatter, plus a
  one-line pointer in `MEMORY.md`. Link related entries with `[[name]]`.

Rules:

- Capture only what is durable and non-obvious. Skip anything already recorded, or
  that the repo, git history, `tools/*.py` docstrings, or the `Makefile` already
  make clear.
- Prefer updating an existing file over creating a near-duplicate; delete entries
  that turn out to be wrong.
- Follow the global `~/.claude/CLAUDE.md` writing style (no em-dashes, short
  sentences).

When done, list exactly what you added or changed. Do not commit.
