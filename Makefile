# Thinking in Python: build and verification targets.
# Tooling is managed by uv, so targets run through `uv run`. Override with
# `make PY=python ...` to use a plain interpreter. On Windows without `make`,
# run the underlying `uv run python ...` commands directly (see tools/README.md).

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

.PHONY: help sync-ci ci sync check site local serve examples run test ty lint extract reflow reflow-check spell prose clean-examples clean-site

help:
	@echo "Targets:"
	@echo "  sync-ci   - update Examples/ from the Markdown, then run the full CI gate"
	@echo "  ci        - run the full local gate: check, ty, ruff, run, pytest, site"
	@echo "  sync      - update the committed Examples/ tree from the Markdown"
	@echo "  check     - verify book examples match the committed Examples/ tree"
	@echo "  site      - render Markdown/ into build/site/ with pandoc"
	@echo "  local     - build the site, serve it, and open a browser"
	@echo "  serve     - serve build/site/ at http://localhost:8000"
	@echo "  examples  - extract then run (the full verification pass)"
	@echo "  run       - run every extracted .py and report failures"
	@echo "  test      - run the book's pytest examples (test_*.py)"
	@echo "  ty        - type-check the extracted examples (must be clean)"
	@echo "  lint      - PEP8-lint the extracted examples with ruff (must be clean)"
	@echo "  extract   - write ExtractedExamples/ from the Markdown"
	@echo "  reflow    - rewrite prose to one sentence per line (CH=02 for one chapter)"
	@echo "  reflow-check - report which chapters would reflow, no write (CH=02 for one)"
	@echo "  spell     - spell-check prose/comments with codespell (CH=29 for one chapter)"
	@echo "  prose     - house-style lint with Vale (CH=29 for one chapter; needs vale binary)"
	@echo "  clean-examples - remove ExtractedExamples/"
	@echo "  clean-site     - remove build/site/"

# Update the committed Examples/ tree from the Markdown (the source of truth),
# then run the full local gate. Use this after editing code blocks in Markdown/.
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

run:
	$(PY) tools/run_examples.py

test:
	$(PYTEST) $(PYTEST_N) ExtractedExamples

ty:
	$(TY) check ExtractedExamples

lint:
	$(RUFF) check ExtractedExamples

extract:
	$(PY) tools/extract_examples.py --write

# Rewrite prose paragraphs to one sentence per line (code, tables, lists, and
# headings are left untouched; a file is rewritten only if it round-trips).
# Target one chapter with CH=, e.g. `make reflow CH=02` or `make reflow CH=Tour`.
reflow:
	$(PY) tools/reflow_prose.py --write $(CH)

reflow-check:
	$(PY) tools/reflow_prose.py $(CH)

# Spell-check the book prose and code comments. codespell config and the
# ignore list live in pyproject.toml and tools/codespell-ignore.txt. Run one
# chapter with CH= (e.g. `make spell CH=29`) or a path with DOCS=.
spell:
	$(SPELL) $(PROSE_FILES)

# House-style lint with Vale: no em-dashes and no filler phrases. Run one
# chapter with CH= (e.g. `make prose CH=29`) or a path with DOCS=.
# Vale is a standalone binary (not uv-managed); see .vale.ini for install notes.
prose:
	$(VALE) $(PROSE_FILES)

# Mirrors the GitHub Actions gates plus a site build, all run locally. The
# default GitHub Actions path only builds and publishes the site; these gates
# run in CI only on request (see tools/README.md).
ci:
	$(PY) tools/extract_examples.py
	$(PY) tools/extract_examples.py --write
	$(TY) check ExtractedExamples
	$(RUFF) check ExtractedExamples
	$(PY) tools/run_examples.py
	$(PYTEST) $(PYTEST_N) ExtractedExamples
	$(PY) tools/build_site.py

clean-examples:
	$(PY) -c "import shutil; shutil.rmtree('ExtractedExamples', ignore_errors=True)"

clean-site:
	$(PY) -c "import shutil; shutil.rmtree('build/site', ignore_errors=True)"
