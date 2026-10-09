<!-- outside review of Chapters/18_Techniques--Performance.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `18_Techniques--Performance.md` chapter:

**1. Section: Reading a `cProfile` Report (prose misdescribes listing behavior)**

* **Target Text:** "This section's report profiles a small script, `prof_demo.py`, built with one obvious hot spot and one function called too many times:"
* **Issue:** In `prof_demo.py`, neither `slow()` nor `helper()` is called too many times—each function is called exactly once. The 10,001 calls in the profiler report belong to the generator expression (`<genexpr>`) driven by `sum()`, not to repeated invocations of a function.
* **Instruction:** Change "built with one obvious hot spot and one function called too many times:" to "built with one obvious hot spot and one generator expression evaluated per element:".

**2. Section: The Tail-Calling Interpreter (non-existent compiler release and unsupported calling convention)**

* **Target Text:** "A source build needs `--with-tail-call-interp` and a compiler with the `preserve_none` calling convention: Clang 19 or newer, or Visual Studio 2026."
* **Issue:** Visual Studio 2026 does not exist (Visual Studio 2022 is the current release), and the MSVC compiler does not support LLVM's `preserve_none` calling convention. Building CPython's tail-calling interpreter on Windows requires Clang 19 or newer (such as via `clang-cl`).
* **Instruction:** Change "Clang 19 or newer, or Visual Studio 2026." to "Clang 19 or newer (including `clang-cl` on Windows).".

**3. Section: Heap (prose asserts an action the listing does not perform)**

* **Target Text:** "The list's own `pop(0)` returns the smallest value the first time, but it also destroys the heap ordering, so a second `pop(0)` returns 6 while 4 is still in the list:"
* **Issue:** `heap_corruption.py` calls `pop(0)` only once (returning 3). It never executes a second `pop(0)`; instead, it prints `heap` to show that `heap[0]` is now 6 while 4 remains at index 1.
* **Instruction:** Change "so a second `pop(0)` returns 6 while 4 is still in the list:" to "leaving 6 at `heap[0]` while 4 is still in the list (so a second `pop(0)` would return 6):".

**4. Section: Converting a Slow Function to Rust (benchmarking unoptimized debug build)**

* **Target Text:** "`maturin develop` compiles and installs `fastcount`,"
* **Issue:** By default, `maturin develop` builds using Cargo's unoptimized debug profile (`dev`), which leaves compiler optimizations disabled and runtime checks enabled. In a chapter dedicated to performance benchmarking against Numba and CPython, omitting `--release` leads readers to benchmark an unoptimized binary.
* **Instruction:** Change "`maturin develop` compiles and installs `fastcount`," to "`maturin develop --release` compiles an optimized build and installs `fastcount`,".

## Verdicts

Second run, on the Flash model. Applied in commit a5c628ef, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. Running the extracted `prof_demo.py` under `uv run python -m cProfile` shows `slow()` and `helper()` at one call each and `<genexpr>` at 10001, so no function in the source is called many times. The sentence now says the script has one generator expression that `cProfile` counts as a call per element, which matches the later sentence about `<genexpr>`'s ten thousand calls.
2. Rejected. Both the python.org 3.15.0rc2 binary (the build the section says uses the tail-calling interpreter) and the uv-managed one report `MSC v.1951` in `sys.version`, the MSVC 14.50 toolset that ships with Visual Studio 2026, so that release exists and builds the tail-calling interpreter on Windows.
3. Applied. The extracted `heap_corruption.py` calls `pop(0)` once and then prints `[6, 4, 7, 10, 5, 8, 9]`. The sentence now says `heap[0]` holds 6 while 4 is still in the list, in place of describing a second `pop(0)` the listing never makes.
4. Applied. `maturin develop` builds Cargo's debug profile unless given `--release`, while the book's own `tip rust-build` goes through `uv sync`, which builds in release mode, so the sample speedups come from an optimized build. The sentence now gives `maturin develop --release` and says the flag selects the optimized profile; the crate was not built (no Rust toolchain in the gate).
