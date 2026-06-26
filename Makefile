# Thinking in Python: build and verification targets.
# Tooling is managed by uv, so targets run through `uv run`. Override with
# `make PY=python ...` to use a plain interpreter. On Windows the quickest way to
# get GNU Make is winget (pre-installed on modern Windows):
#   winget install ezwinports.make
# Restart the terminal, then `make --version` to confirm.

PY ?= uv run python
TY ?= uv run ty
PYTEST ?= uv run pytest
RUFF ?= uv run ruff
# Extra pytest args. The suite is tiny, so serial is fastest today; enable
# xdist as it grows with `make test PYTEST_N="-n auto"`.
PYTEST_N ?=
SPELL ?= uv run codespell
VALE ?= vale
DOCS ?= Markdown
# Files for spell/prose: all of DOCS, or one chapter via CH= (a number or stem
# prefix), e.g. `make prose CH=29` or `make prose CH=29_Visitor`.
PROSE_FILES = $(if $(CH),Markdown/$(CH)*.md,$(DOCS))

.PHONY: help reset verify sync-ci ci gate sync check site local serve examples run test ty lint extract output output-check fix-imports upgrade-python reflow reflow-check spell prose eol fix-eol listings fix-listings banned comment-periods fix-comment-periods comment-caps fix-comment-caps anchors clean-examples clean-site

help:
	@echo "Targets:"
	@echo "  verify    - sync Examples/, then run every gate except the site build"
	@echo "  sync-ci   - like verify, plus the site build (the full CI gate)"
	@echo "  ci        - run the full local gate: check, ty, ruff, run, pytest, site"
	@echo "  reset     - regenerate build/examples/ from the Markdown (fixes drift)"
	@echo "  upgrade-python - upgrade the dev Python (latest patch; TO=3.15 to repin a minor), resync, verify"
	@echo "  gate      - the gate without sync or site (check, ty, ruff, run, pytest)"
	@echo "  sync      - update the committed Examples/ tree from the Markdown"
	@echo "  check     - verify book examples match the committed Examples/ tree"
	@echo "  site      - render Markdown/ into build/site/ with pandoc"
	@echo "  local     - build the site, serve it, and open a browser"
	@echo "  serve     - serve build/site/ at http://localhost:8000"
	@echo "  examples  - extract then run (the full verification pass)"
	@echo "  run       - run every extracted .py and report failures"
	@echo "  output    - update the ## output markers in the book's listings"
	@echo "  output-check - verify the ## output markers without rewriting"
	@echo "  test      - run the book's pytest examples (test_*.py)"
	@echo "  ty        - type-check the extracted examples (must be clean)"
	@echo "  lint      - PEP8-lint the extracted examples with ruff (must be clean)"
	@echo "  fix-imports - sort imports and drop unused ones in the listings (ruff I,F401), in the Markdown"
	@echo "  extract   - write build/examples/ from the Markdown"
	@echo "  reflow    - rewrite prose to one sentence per line (CH=02 for one chapter)"
	@echo "  reflow-check - report which chapters would reflow, no write (CH=02 for one)"
	@echo "  spell     - codespell + prose_lint + full-dictionary spellcheck (CH=29 for one)"
	@echo "  prose     - house-style lint with Vale (CH=29 for one chapter; needs vale binary)"
	@echo "  eol       - check tracked text files for CRLF (fails the ci gate)"
	@echo "  fix-eol   - convert any CRLF in tracked text files to LF"
	@echo "  listings  - check python listings keep blank lines minimal"
	@echo "  fix-listings - remove the offending blank lines from listings"
	@echo "  banned    - fail if any tools/banned_phrases.txt phrase is in the book"
	@echo "  comment-periods - fail if a one-line listing comment ends with a period"
	@echo "  fix-comment-periods - remove those trailing periods"
	@echo "  comment-caps - fail if a prose comment is not capitalized (heuristic)"
	@echo "  fix-comment-caps - capitalize them"
	@echo "  anchors   - fail if a heading-anchor link points at no real heading"
	@echo "  clean-examples - remove build/examples/"
	@echo "  clean-site     - remove build/site/"

# Sync Examples/ from the Markdown, then run every gate except the site build.
# The everyday "is everything still good?" command after editing Markdown/.
verify: sync gate

# Same as verify, plus the site build at the end.
sync-ci: sync ci

# Write the extracted tree straight into Examples/, syncing the committed copy
# to the Markdown. Run after editing a code block so the drift check passes.
sync:
	$(PY) tools/extract_examples.py --write -o Examples

check:
	$(PY) tools/extract_examples.py

site:
	$(PY) tools/build_site.py

local: site
	$(PY) tools/serve.py --open

serve:
	$(PY) tools/serve.py

examples: extract run

# These all read build/examples/, so each depends on `extract` to rebuild it
# first. make builds `extract` once per invocation, so depending on it from
# several targets does not re-extract. This is what stops a stale tree (e.g. a
# gitignored build/examples/ left over from an older Markdown) from being
# checked. Use `make reset` to force a clean regeneration.
run: extract
	$(PY) tools/run_examples.py

# Rewrite the ## output markers inside the Markdown's ```python listings to the
# stdout each listing actually produces. Depends on extract so each listing runs
# from build/examples/<chapter>/, where its sibling imports and data files live.
output: extract
	$(PY) tools/validate_output.py --update Markdown

# Same, but report mismatches instead of rewriting (a gate-friendly check).
output-check: extract
	$(PY) tools/validate_output.py Markdown

test: extract
	$(PYTEST) $(PYTEST_N) build/examples

ty: extract
	$(TY) check build/examples

lint: extract
	$(RUFF) check build/examples

# Organize imports in the book's python listings (ruff's I rule), writing the
# result back into the Markdown. Depends on extract so ruff sees each listing's
# siblings and classifies imports the way the lint gate does.
fix-imports: extract
	$(PY) tools/fix_imports.py --fix

extract:
	$(PY) tools/extract_examples.py --write

# Rewrite prose paragraphs to one sentence per line (code, tables, lists, and
# headings are left untouched; a file is rewritten only if it round-trips).
# Target one chapter with CH=, e.g. `make reflow CH=02` or `make reflow CH=Tour`.
reflow:
	$(PY) tools/reflow_prose.py --write $(CH)

reflow-check:
	$(PY) tools/reflow_prose.py $(CH)

# Spell-check the book and lint it for small mechanical slips. codespell
# catches known misspellings (prose and code comments); prose_lint catches
# spacing/blank-line/punctuation slips; spellcheck.py is a full-dictionary check
# of the prose, with accepted terms in tools/wordlist.txt. Run one chapter with
# CH= (e.g. `make spell CH=29`) or a path with DOCS=.
spell:
	$(SPELL) $(PROSE_FILES)
	$(PY) tools/prose_lint.py $(PROSE_FILES)
	$(PY) tools/spellcheck.py $(PROSE_FILES)

# House-style lint with Vale: no em-dashes and no filler phrases. Run one
# chapter with CH= (e.g. `make prose CH=29`) or a path with DOCS=.
# Vale is a standalone binary (not uv-managed); see .vale.ini for install notes.
prose:
	$(VALE) $(PROSE_FILES)

# Fail if any tracked text file has CRLF in the working tree. .gitattributes
# keeps the committed blobs LF; this catches a drifted working copy. Run
# `$(PY) tools/check_line_endings.py --fix` to convert offenders.
eol:
	$(PY) tools/check_line_endings.py

fix-eol:
	$(PY) tools/check_line_endings.py --fix

# Fail if any ```python listing has more than one blank line in a row or a
# blank line between import groups. Run `make fix-listings` to remove them.
listings:
	$(PY) tools/listing_format.py

fix-listings:
	$(PY) tools/listing_format.py --fix

# Fail if any phrase in tools/banned_phrases.txt appears anywhere in the book.
banned:
	$(PY) tools/banned_phrases.py

# A one-line listing comment ends without a period; only multiline comments use
# periods. Run `make fix-comment-periods` to strip the offenders.
comment-periods:
	$(PY) tools/comment_periods.py

fix-comment-periods:
	$(PY) tools/comment_periods.py --fix

# A prose comment starts with a capital. Heuristic, so false positives are
# listed in tools/comment_caps_allow.txt. Run `make fix-comment-caps` to apply.
comment-caps:
	$(PY) tools/capitalize_comments.py

fix-comment-caps:
	$(PY) tools/capitalize_comments.py --write

# Fail if a heading-anchor link (file.md#id or #id) points at no real heading.
anchors:
	$(PY) tools/check_anchors.py

# The local gate without the site build: line endings, listing density, drift
# check, ty, ruff, run, pytest. `verify` runs `sync` first; `ci` adds the site.
gate:
	$(PY) tools/check_line_endings.py
	$(PY) tools/listing_format.py
	$(PY) tools/banned_phrases.py
	$(PY) tools/comment_periods.py
	$(PY) tools/capitalize_comments.py
	$(PY) tools/check_anchors.py
	$(PY) tools/extract_examples.py
	$(PY) tools/extract_examples.py --write
	$(TY) check build/examples
	$(RUFF) check build/examples
	$(PY) tools/run_examples.py
	$(PYTEST) $(PYTEST_N) build/examples

# Mirrors the GitHub Actions gates plus a site build, all run locally. The
# default GitHub Actions path only builds and publishes the site; these gates
# run in CI only on request (see tools/README.md).
ci: gate site

# Upgrade the development Python and re-check the book against it.
# `make upgrade-python` pulls the latest patch of the pinned minor (from
# .python-version); `make upgrade-python TO=3.15` repins to a new minor first
# (rewriting .python-version and the requires-python floor). Both resync the
# venv and run the gate. Run through `uv run --no-project` so the orchestrating
# interpreter is not the venv that `uv sync` rebuilds.
upgrade-python:
	uv run --no-project python tools/upgrade_python.py $(TO)
	$(MAKE) verify

# Throw away build/examples/ and rebuild it from the Markdown. Run this when
# a check reports drift you cannot explain (a stale tree from an older Markdown,
# or one carried over from another machine).
reset: clean-examples extract
	@echo "build/examples/ regenerated from the Markdown."

clean-examples:
	$(PY) -c "import shutil; shutil.rmtree('build/examples', ignore_errors=True)"

clean-site:
	$(PY) -c "import shutil; shutil.rmtree('build/site', ignore_errors=True)"
