# Thinking in Python: working in this repo

This file is loaded every session. It captures how the repo is built and verified,
plus the traps that are easy to rediscover the hard way. Personal writing style
lives in the global `~/.claude/CLAUDE.md`; accrued facts live in project memory.

## Source of truth: Markdown, not Examples/

`Markdown/NN_*.md` is authoritative. Every fenced ```python block whose first line
is a `# path/slug.py` comment is an extractable example. `Examples/` is **generated
from the Markdown** by `tools/extract_examples.py`, so:

- Edit the code **in the Markdown block**, never in `Examples/` directly.
- After editing, sync the committed tree: `make sync`
  (= `python tools/extract_examples.py --write -o Examples`).
- `Examples/` also holds files with no Markdown block (hand-written helpers,
  `.idea/`, `__pycache__`). The drift check only flags book blocks that are missing
  or changed, not "extra" files, so a stray `Examples/` file can linger.

## The verify loop after editing a chapter

Fastest path is `make verify` (fix line endings, sync, then every gate but the
site build). When iterating on one chapter, the manual sequence is:

1. `python tools/extract_examples.py --write -o Examples`   # sync committed tree
2. `python tools/extract_examples.py`                       # drift check ("In sync")
3. `python tools/extract_examples.py --write`               # (re)build build/examples/
4. `python tools/validate_output.py Markdown/NN_*.md`       # `#:` markers match stdout
5. `(cd build/examples && ty check NN_Chapter)`             # types
6. `uv run ruff check build/examples/NN_Chapter`            # lint
7. `uv run pytest build/examples/NN_Chapter`                # tests
8. `python tools/run_examples.py NN_Chapter`                # runs scripts, honors norun.txt

Prose-only edits still need `check_anchors.py` (cross-references) and
`banned_phrases.py`; both are in `make verify`.

## Traps (learned the hard way)

- **Ruff line length is 70.** Long inline comments are the usual culprit; move the
  comment to its own line or wrap the statement. A scratch dir's `ruff` uses the
  default 88, so **line length must be verified against `build/examples`**, not a
  temp file.
- **Run `ty`/`ruff`/`pytest` against `build/examples/`** (via `uv run`), never a
  loose scratch file, or config/imports resolve differently.
- **`#:` output markers must equal stdout exactly.** For nondeterministic output,
  round floats (`f"{x:.6f}"`) or print `type(e).__name__` instead of a message.
- **`build/` is derived and gitignored.** `extract_examples.py --write` now wipes
  the target under `build/` first, so a fresh sync is the fix for weird drift or a
  stale tree. A stale `build/examples/` was behind "phantom" timeouts/import errors.
- **`run_examples.py`: never pass a relative `--tree`.** It goes on `PYTHONPATH`
  and breaks once an example changes cwd. GUI/interactive examples are skipped via
  `tools/norun.txt` (keep those paths current when chapters are renumbered).
- **Renumbering a chapter** touches: `Markdown/` and `Examples/` filenames, every
  `NN_*.md` cross-reference, `build_site.py` `PARTS`, `tools/norun.txt`, and the
  `README.md` tracking table. Appendices use letter prefixes (`A_...`); build_site
  labels them "Appendix X".
- **Anchors:** pandoc auto-slugs a heading (backticks/punctuation dropped, but `.`
  is kept). Give headings an explicit `{#id}` when the auto-slug would be ugly
  (e.g. anything containing `type[...]` or `__init__`). `check_anchors.py` gates it.

## Pointers

- `tools/*.py` all have thorough module docstrings; read them before guessing.
- The `Makefile` documents every gate and target (`make help`).
- Detailed conventions and decisions are in project memory (`MEMORY.md` index).
