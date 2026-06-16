# Thinking in Python: build and verification targets.
# Tooling is managed by uv, so targets run through `uv run`. Override with
# `make PY=python ...` to use a plain interpreter. On Windows without `make`,
# run the underlying `uv run python ...` commands directly (see tools/README.md).

PY ?= uv run python
TY ?= uv run ty
PYTEST ?= uv run pytest
RUFF ?= uv run ruff

.PHONY: help check extract run examples site serve local ty lint test clean-examples clean-site ci

help:
	@echo "Targets:"
	@echo "  check     - verify book examples match the committed Examples/ tree"
	@echo "  extract   - write ExtractedExamples/ from the Markdown"
	@echo "  run       - run every extracted .py and report failures"
	@echo "  examples  - extract then run (the full verification pass)"
	@echo "  site      - render Markdown/ into build/site/ with pandoc"
	@echo "  serve     - serve build/site/ at http://localhost:8000"
	@echo "  local     - build the site, then serve it locally"
	@echo "  ty        - type-check the extracted examples (must be clean)"
	@echo "  lint      - PEP8-lint the extracted examples with ruff (must be clean)"
	@echo "  test      - run the book's pytest examples (test_*.py)"
	@echo "  ci        - what CI runs: check, run, pytest, ty, ruff, site"
	@echo "  clean-examples - remove ExtractedExamples/"
	@echo "  clean-site     - remove build/site/"

check:
	$(PY) tools/extract_examples.py

extract:
	$(PY) tools/extract_examples.py --write

run:
	$(PY) tools/run_examples.py

examples: extract run

site:
	$(PY) tools/build_site.py

serve:
	$(PY) -m http.server --directory build/site

local: site
	$(PY) -m http.server --directory build/site

ty:
	$(TY) check ExtractedExamples

lint:
	$(RUFF) check ExtractedExamples

test:
	$(PYTEST) ExtractedExamples

# Mirrors the GitHub Actions gate: drift check, the example run, the book's
# pytest examples, and a clean site build. All hard gates.
ci:
	$(PY) tools/extract_examples.py
	$(PY) tools/extract_examples.py --write
	$(PY) tools/run_examples.py
	$(PYTEST) ExtractedExamples
	$(TY) check ExtractedExamples
	$(RUFF) check ExtractedExamples
	$(PY) tools/build_site.py

clean-examples:
	$(PY) -c "import shutil; shutil.rmtree('ExtractedExamples', ignore_errors=True)"

clean-site:
	$(PY) -c "import shutil; shutil.rmtree('build/site', ignore_errors=True)"
