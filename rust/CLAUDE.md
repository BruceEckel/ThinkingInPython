# Rust examples: rust/, isolated from the main build

Chapter 18's "Converting a Slow Function to Rust" section has real,
buildable PyO3/maturin crates under `rust/` (currently `rust/fastcount/`),
extracted from the same `Chapters/*.md` by `tools/extract_rust.py`, a
separate tool from `tools/extract_examples.py`. Two marker conventions,
both first-line comments in a fenced block:

- A ` ```rust ` block marked `// <crate>/src/<file>.rs` extracts to
  `rust/<crate>/src/<file>.rs`.
- A ` ```python ` block marked `# rust/<crate>/<name>.py` is the Python
  caller for that crate. The `rust/` prefix is what makes
  `tools/extract_examples.py` skip it entirely (never written to
  `Examples/`/`build/examples/`, never run by `pytest`/`ty`/`ruff`/
  `run_examples.py`), since the compiled module it imports does not exist
  in the main build's environment.

This is deliberate: the root `Makefile` never enters `rust/` and never
requires a Rust toolchain, so `verify`/`gate`/`all`/`ci` all work with no
Rust installed. Only `cd rust && make` (a separate `Makefile` there) syncs,
builds, and runs the crates for real; see `rust/README.md`. A crate
directory also holds real, hand-maintained project files
(`Cargo.toml`, `pyproject.toml`, `.python-version`, `.gitignore`,
scaffolded once by `maturin new --bindings pyo3 <name>`) that
`extract_rust.py` never touches, only `src/lib.rs` and the paired demo
file are book-generated.
