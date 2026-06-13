# Thinking in Python: build and verification targets.
# On Windows without `make`, run the underlying python commands directly
# (see tools/README.md).

PY ?= python

.PHONY: help check extract run examples site clean-examples clean-site ci

help:
	@echo "Targets:"
	@echo "  check     - verify book examples match the committed Examples/ tree"
	@echo "  extract   - write ExtractedExamples/ from the Markdown"
	@echo "  run       - run every extracted .py and report failures"
	@echo "  examples  - extract then run (the full verification pass)"
	@echo "  site      - render Markdown/ into build/site/ with pandoc"
	@echo "  ci        - what CI runs: check, baseline run, site"
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

# Mirrors the GitHub Actions gate. Drift check is advisory for now (leading
# "-" ignores its exit); the regression run and site build are hard gates.
ci:
	-$(PY) tools/extract_examples.py
	-$(PY) tools/extract_examples.py --write
	$(PY) tools/run_examples.py --baseline
	$(PY) tools/build_site.py

clean-examples:
	$(PY) -c "import shutil; shutil.rmtree('ExtractedExamples', ignore_errors=True)"

clean-site:
	$(PY) -c "import shutil; shutil.rmtree('build/site', ignore_errors=True)"
