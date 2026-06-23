# Review: Chapter 05 (Modules and Packages)

A clear, well-ordered escalation: module, `from`/`as`, packages, nested packages.
All eight scripts run and their output matches the prose (including the claim in
line 52 that `import_module.py` shows only `'module' imported`).

## Should fix

1. **`PYTHONPATH` section overstates and conflates (lines 171-179).**
   Two issues:
   - "the original (and now semi-deprecated) solution" overstates it. `PYTHONPATH`
     is not deprecated; it is just less commonly reached for. Consider "less
     common now" rather than "semi-deprecated".
   - "effectively superseded by the *virtual environment*" mixes two different
     mechanisms. A virtual environment isolates installed packages; `PYTHONPATH`
     adds import search paths. A venv does not really replace `PYTHONPATH` for the
     "my module lives in another directory" problem. The usual modern answer to
     that is an installable package (`pip install -e .`) or adjusting `sys.path`,
     often inside a venv.
   - Scope note: the book otherwise avoids explaining virtual environments on
     purpose. This section gestures at them. You may want to reframe it to stay
     language-focused (for example, point at making the code an installable
     package) rather than introducing venvs here.

2. **`__main__` as a value, not a variable (lines 28, 37, 44).**
   "`__name__` is equivalent to `__main__`" and "`__name__` is `__main__`" read as
   if `__main__` were a variable. It is the string value `"__main__"`. Writing it
   quoted (`"__main__"`) when you mean the value would be more precise, matching
   the `if __name__ == "__main__":` in the code.

## Nits / optional

3. **Tangent on special methods (lines 29-31).**
   While explaining `if __name__ == "__main__"`, the text pivots to "Methods named
   with double underscores are special methods... hook your class into the
   language's operators". True, but it is a detour from the variable under
   discussion. Consider keeping just the "dunder" naming point here and leaving
   special methods to the Classes chapter.

4. **"empty" vs "nothing but a comment" (lines 84, 87).**
   Line 84 says `__init__.py` "is empty"; line 87 gives it "an `__init__.py`
   containing nothing but a comment". The demonstrated file holds the path-marker
   comment, so it is not literally empty. Harmless, but the two lines disagree.

## Verified

- Ran all eight scripts (`use_module`, `import_module`, `using_from`, `using_as`,
  `using_packages`, `from_packages`, `no_qualification`, `two_levels`). Output is
  sensible and consistent with the prose; the nested-package import works and the
  module-level `print()` side effects appear in the expected order.
- Function-paren convention applied (`print()`, `useful_function()`,
  `module.useful_function()`).
- The `__init__.py` footnote and the `__package__.py` aside render as written.
