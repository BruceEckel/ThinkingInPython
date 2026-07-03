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

.PHONY: help reset verify sync-ci ci gate sync check site local serve examples run test ty lint extract output output-check fix-imports upgrade-python reflow reflow-check spell spell-add prose eol fix-eol listings fix-listings banned comment-periods fix-comment-periods comment-caps fix-comment-caps anchors clean-examples clean-site check-tools check-tools-full upgrade-tools

# Self-documenting help: every target below carries an inline `## text` doc
# comment, and a `##@ Category` comment line starts a new section. Add a
# target's one-line doc on its own target line so `make help` and the recipe
# never drift apart; put anything longer in a plain `#` comment above it.
# Parsed by tools/make_help.py instead of grep/awk, so help has no dependency
# on a POSIX toolchain being on PATH (every other target already needs Python).
help:  ## Show this help
	$(PY) tools/make_help.py

##@ Setup

# What a reader needs for the everyday commands below: uv, plus the
# uv-managed dev tools (ty, ruff, pytest). make and git are checked too but
# assumed present, since you needed both to get this far.
check-tools:  ## Check the tools a reader needs (uv, ty, ruff, pytest)
	$(PY) tools/check_tools.py

# Adds the tools a book maintainer needs for the rest of `make help`:
# pandoc (site/local) and the standalone vale binary (prose).
check-tools-full:  ## Check every tool, including pandoc and vale (site/prose)
	$(PY) tools/check_tools.py --full

# Updates uv itself (when it was installed via its standalone installer),
# then upgrades every uv-managed dev tool (ty, ruff, pytest, ...) to the
# latest version pyproject.toml allows, rewriting uv.lock. pandoc and vale
# are updated best-effort through winget or Homebrew, whichever is on PATH.
# make/git are left alone. Review `git diff uv.lock` before committing.
# For the pinned Python version itself, use `make upgrade-python`.
upgrade-tools:  ## Update uv, the uv-managed dev tools, and (best-effort) pandoc/vale
	$(PY) tools/upgrade_tools.py
	$(MAKE) check-tools-full

##@ Everyday

# Fix any CRLF in the working tree, sync Examples/ from the Markdown, then run
# every gate except the site build. The everyday "is everything still good?"
# command after editing Markdown/. fix-eol runs first so the eol check inside
# gate sees an already-clean tree.
verify: fix-eol sync gate  ## Fix line endings, sync Examples/, then run every gate except the site build

# Same as verify, plus the site build at the end.
sync-ci: sync ci  ## Like verify, plus the site build (the full CI gate)

# The local gate without the site build: line endings, listing density, drift
# check, output markers, ty, ruff, run, pytest. `verify` runs `sync` first;
# `ci` adds the site.
gate:  ## The gate without sync or site (check, output, ty, ruff, run, pytest)
	$(PY) tools/check_line_endings.py
	$(PY) tools/listing_format.py
	$(PY) tools/banned_phrases.py
	$(PY) tools/comment_periods.py
	$(PY) tools/capitalize_comments.py
	$(PY) tools/check_anchors.py
	$(PY) tools/extract_examples.py
	$(PY) tools/extract_examples.py --write
	$(PY) tools/validate_output.py Markdown
	$(TY) check build/examples
	$(RUFF) check build/examples
	$(PY) tools/run_examples.py
	$(PYTEST) $(PYTEST_N) build/examples

# Mirrors the GitHub Actions gates plus a site build, all run locally. The
# default GitHub Actions path only builds and publishes the site; these gates
# run in CI only on request (see tools/README.md).
ci: gate site  ## Run the full local gate: check, ty, ruff, run, pytest, site

# Throw away build/examples/ and rebuild it from the Markdown. Run this when
# a check reports drift you cannot explain (a stale tree from an older Markdown,
# or one carried over from another machine).
reset: clean-examples extract  ## Regenerate build/examples/ from the Markdown (fixes drift)
	@echo "build/examples/ regenerated from the Markdown."

# Upgrade the development Python and re-check the book against it.
# `make upgrade-python` pulls the latest patch of the pinned minor (from
# .python-version); `make upgrade-python TO=3.15` repins to a new minor first
# (rewriting .python-version and the requires-python floor). Both resync the
# venv and run the gate. Run through `uv run --no-project` so the orchestrating
# interpreter is not the venv that `uv sync` rebuilds.
upgrade-python:  ## Upgrade the dev Python (latest patch; TO=3.15 to repin a minor), resync, verify
	uv run --no-project python tools/upgrade_python.py $(TO)
	$(MAKE) verify

##@ Build and site

# Write the extracted tree straight into Examples/, syncing the committed copy
# to the Markdown. Run after editing a code block so the drift check passes.
sync:  ## Update the committed Examples/ tree from the Markdown
	$(PY) tools/extract_examples.py --write -o Examples

check:  ## Verify book examples match the committed Examples/ tree
	$(PY) tools/extract_examples.py

site:  ## Render Markdown/ into build/site/ with pandoc
	$(PY) tools/build_site.py

local: site  ## Build the site, serve it, and open a browser
	$(PY) tools/serve.py --open

serve:  ## Serve build/site/ at http://localhost:8000
	$(PY) tools/serve.py

##@ Examples (build/examples/)

examples: extract run  ## Extract then run (the full verification pass)

# These all read build/examples/, so each depends on `extract` to rebuild it
# first. make builds `extract` once per invocation, so depending on it from
# several targets does not re-extract. This is what stops a stale tree (e.g. a
# gitignored build/examples/ left over from an older Markdown) from being
# checked. Use `make reset` to force a clean regeneration.
run: extract  ## Run every extracted .py and report failures
	$(PY) tools/run_examples.py

# Rewrite the #: output markers inside the Markdown's ```python listings to the
# stdout each listing actually produces. Depends on extract so each listing runs
# from build/examples/<chapter>/, where its sibling imports and data files live.
output: extract  ## Update the #: output markers in the book's listings
	$(PY) tools/validate_output.py --update Markdown

# Same, but report mismatches instead of rewriting (a gate-friendly check).
output-check: extract  ## Verify the #: output markers without rewriting
	$(PY) tools/validate_output.py Markdown

test: extract  ## Run the book's pytest examples (test_*.py)
	$(PYTEST) $(PYTEST_N) build/examples

ty: extract  ## Type-check the extracted examples (must be clean)
	$(TY) check build/examples

lint: extract  ## PEP8-lint the extracted examples with ruff (must be clean)
	$(RUFF) check build/examples

# Organize imports in the book's python listings (ruff's I rule), writing the
# result back into the Markdown. Depends on extract so ruff sees each listing's
# siblings and classifies imports the way the lint gate does.
fix-imports: extract  ## Sort imports and drop unused ones in the listings (ruff I,F401), in the Markdown
	$(PY) tools/fix_imports.py --fix

extract:  ## Write build/examples/ from the Markdown
	$(PY) tools/extract_examples.py --write

##@ Prose and spelling

# Rewrite prose paragraphs to one sentence per line (code, tables, lists, and
# headings are left untouched; a file is rewritten only if it round-trips).
# Target one chapter with CH=, e.g. `make reflow CH=02` or `make reflow CH=Tour`.
reflow:  ## Rewrite prose to one sentence per line (CH=02 for one chapter)
	$(PY) tools/reflow_prose.py --write $(CH)

reflow-check:  ## Report which chapters would reflow, no write (CH=02 for one)
	$(PY) tools/reflow_prose.py $(CH)

# Spell-check the book and lint it for small mechanical slips. codespell
# catches known misspellings (prose and code comments); prose_lint catches
# spacing/blank-line/punctuation slips; spellcheck.py is a full-dictionary check
# of the prose, with accepted terms in tools/wordlist.txt. Run one chapter with
# CH= (e.g. `make spell CH=29`) or a path with DOCS=.
spell:  ## codespell + prose_lint + full-dictionary spellcheck (CH=29 for one)
	$(SPELL) $(PROSE_FILES)
	$(PY) tools/prose_lint.py $(PROSE_FILES)
	$(PY) tools/spellcheck.py $(PROSE_FILES)

# Accept every word spellcheck.py doesn't recognize into tools/wordlist.txt
# (sorted, deduplicated) instead of failing. It cannot tell a real term from
# a typo, so always review the diff before committing; a real typo belongs
# in the prose, not the wordlist.
spell-add:  ## Accept every spellcheck-unknown word into wordlist.txt, sorted (review the diff!)
	$(PY) tools/spellcheck.py $(PROSE_FILES) --add

# House-style lint with Vale: no em-dashes and no filler phrases. Run one
# chapter with CH= (e.g. `make prose CH=29`) or a path with DOCS=.
# Vale is a standalone binary (not uv-managed); see .vale.ini for install notes.
prose:  ## House-style lint with Vale (CH=29 for one chapter; needs vale binary)
	$(VALE) $(PROSE_FILES)

##@ Style gates

# Fail if any tracked text file has CRLF in the working tree. .gitattributes
# keeps the committed blobs LF; this catches a drifted working copy. Run
# `$(PY) tools/check_line_endings.py --fix` to convert offenders.
eol:  ## Check tracked text files for CRLF (fails the ci gate)
	$(PY) tools/check_line_endings.py

fix-eol:  ## Convert any CRLF in tracked text files to LF
	$(PY) tools/check_line_endings.py --fix

# Fail if any ```python listing has more than one blank line in a row or a
# blank line between import groups. Run `make fix-listings` to remove them.
listings:  ## Check python listings keep blank lines minimal
	$(PY) tools/listing_format.py

fix-listings:  ## Remove the offending blank lines from listings
	$(PY) tools/listing_format.py --fix

# Fail if any phrase in tools/banned_phrases.txt appears anywhere in the book.
banned:  ## Fail if any tools/banned_phrases.txt phrase is in the book
	$(PY) tools/banned_phrases.py

# A one-line listing comment ends without a period; only multiline comments use
# periods. Run `make fix-comment-periods` to strip the offenders.
comment-periods:  ## Fail if a one-line listing comment ends with a period
	$(PY) tools/comment_periods.py

fix-comment-periods:  ## Remove those trailing periods
	$(PY) tools/comment_periods.py --fix

# A prose comment starts with a capital. Heuristic, so false positives are
# listed in tools/comment_caps_allow.txt. Run `make fix-comment-caps` to apply.
comment-caps:  ## Fail if a prose comment is not capitalized (heuristic)
	$(PY) tools/capitalize_comments.py

fix-comment-caps:  ## Capitalize them
	$(PY) tools/capitalize_comments.py --write

# Fail if a heading-anchor link (file.md#id or #id) points at no real heading.
anchors:  ## Fail if a heading-anchor link points at no real heading
	$(PY) tools/check_anchors.py

##@ Cleanup

clean-examples:  ## Remove build/examples/
	$(PY) -c "import shutil; shutil.rmtree('build/examples', ignore_errors=True)"

clean-site:  ## Remove build/site/
	$(PY) -c "import shutil; shutil.rmtree('build/site', ignore_errors=True)"
