# Rust examples for Thinking in Python

The [Converting a Slow Function to Rust](../Chapters/18_Performance.md#converting-a-slow-function-to-rust)
section shows moving a hot Python function into a compiled
[PyO3](https://pyo3.rs)/[maturin](https://www.maturin.rs) extension. This
directory holds real, buildable copies of those examples.

It is deliberately separate from the rest of the book's tooling.
The repository root's `Makefile` never enters this directory and never
requires a Rust toolchain: `make verify`, `make gate`, `make all`, and
`make ci` all work with no Rust installed. Building and running the code
here is an extra, opt-in step for a reader (or maintainer) who has Rust
and wants to reproduce the speedup numbers themselves.

## Setup

You need:

- [Rust](https://rustup.rs) (`cargo`/`rustc`) on PATH.
- [uv](https://docs.astral.sh/uv/), the same tool the rest of the book
  uses. `uv run` builds each crate through
  [maturin](https://www.maturin.rs) automatically, since each crate's
  `pyproject.toml` names it as the build backend, so **maturin itself
  does not need to be installed**.

## Running it

```
cd rust
make            # sync from the book, build every crate, run its demo
```

`make` runs three steps, also available separately:

```
make sync    # regenerate each crate's src/lib.rs and demo.py from ../Chapters/
make build   # build and install every crate (release mode), without running anything
make test    # build every crate and run its demo.py against the real extension
make clean   # remove every crate's target/ and .venv/ (never touches the book)
```

Each crate gets its own isolated `.venv/` (e.g. `fastcount/.venv/`),
separate from the repository root's `.venv/`, so the compiled extension
never touches the main Python environment the rest of the book uses.

## How a crate stays in sync with the book

`tools/extract_rust.py` (at the repository root) extracts two kinds of
fenced block from `Chapters/*.md`:

- A ` ```rust ` block whose first line is a Rust comment naming the file,
  relative to `rust/`:

  ```rust
  // fastcount/src/lib.rs
  ...
  ```

- A ` ```python ` block whose first line names a file with a `rust/`
  prefix, the Python caller for the module the crate builds:

  ```python
  # rust/fastcount/demo.py
  ...
  ```

  That `rust/` prefix is what tells `tools/extract_examples.py` (the
  book's normal extractor) to skip the block entirely: it is never
  written to `Examples/` or `build/examples/`, and the main build's
  `pytest`/`ty`/`ruff`/`run_examples.py` never see it, since the compiled
  `fastcount` module they would need to `import` does not exist there.

Only `src/lib.rs` and `demo.py` are generated this way. Everything else
in a crate directory (`Cargo.toml`, `pyproject.toml`, `.python-version`,
`.gitignore`) is a real, hand-maintained project file, exactly like any
other Rust project, scaffolded once by `maturin new --bindings pyo3
<name>` and committed. `tools/extract_rust.py` never reads, writes, or
otherwise touches those files.

If you edit the Rust or demo code directly in `Chapters/18_Performance.md`,
run `make sync` (or `cd .. && python tools/extract_rust.py --write`) to
pull the change into this tree before rebuilding.

## Adding another crate

1. `cd rust && maturin new --bindings pyo3 <name>` to scaffold it (needs
   maturin on PATH for this one-time step; `uv tool run maturin new
   --bindings pyo3 <name>` works without installing it).
2. Delete the scaffolded `.github/workflows/` directory (a template CI
   workflow for publishing to PyPI, not needed here).
3. In `Chapters/*.md`, add a ` ```rust ` block marked
   `// <name>/src/lib.rs` and a ` ```python ` block marked
   `# rust/<name>/demo.py`.
4. Add `<name>` to `CRATES` in this directory's `Makefile`.
5. `make sync && make test`.
