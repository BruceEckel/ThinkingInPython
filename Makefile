# Thinking in Python: build and verification targets.
# On Windows without `make`, run the underlying python commands directly
# (see tools/README.md).

PY ?= python

.PHONY: help check extract run examples clean-examples

help:
	@echo "Targets:"
	@echo "  check     - verify book examples match the committed Examples/ tree"
	@echo "  extract   - write ExtractedExamples/ from the Markdown"
	@echo "  run       - run every extracted .py and report failures"
	@echo "  examples  - extract then run (the full verification pass)"
	@echo "  clean-examples - remove ExtractedExamples/"

check:
	$(PY) tools/extract_examples.py

extract:
	$(PY) tools/extract_examples.py --write

run:
	$(PY) tools/run_examples.py

examples: extract run

clean-examples:
	$(PY) -c "import shutil; shutil.rmtree('ExtractedExamples', ignore_errors=True)"
