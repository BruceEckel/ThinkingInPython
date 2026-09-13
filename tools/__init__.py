"""The book's build and verification tools, run as `python -m tools.<name>`.

Each module is a script with a `main()` and a thorough docstring;
the shared pieces (`config`, `repo`, `markdown`, `prose`, `pycode`,
`report`, `extract`) are imported by the others as `tools.<name>`.
Run from the repository root, which `-m` puts on `sys.path`, so
`tools` is the only name the package adds to it; a book listing can
therefore be called `config.py` or `report.py` without either
shadowing the other. See tools/README.md.
"""
