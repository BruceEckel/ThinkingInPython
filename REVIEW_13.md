# Review: Chapter 13 (Decorators)

A strong, well-sequenced chapter: replacement decorator, add-behavior, signature
preservation with `ParamSpec`, decorators with arguments, the class form (no-arg
and arg-taking), stacking, class decoration, and the object Decorator pattern.
All eleven example scripts run, every "The output is:" block matches, the tests
pass, and `ty`/`ruff`/`prose_lint`/`spellcheck` are clean.

## Nits / optional

3. **Name-rebinding written two ways (`cheese()` vs `add`).**
   Line 30 says "This name is assigned to `cheese()` during decoration" (parens),
   while line 100 says "assigned to the name `add`" (bare) for the same idea of a
   name being rebound. Pick one. I would leave a rebound name bare ("assigned to
   `cheese`"), since you are naming the binding, not calling it.

4. **`# type: ignore` on `func.__name__` is unexplained.**
   It appears in `tracer.py`, `trace_class.py`, and `count_calls.py`. The reason is
   that `Callable[P, R]` has no `__name__` known to the checker, even though every
   function has one at runtime. Given how carefully the chapter explains the rest
   of the typing, one sentence noting why those ignores are needed would close the
   loop for a curious reader. Optional.

5. **Intro examples use bare `Callable` (lines 13, 39).**
   `simple_decoration.py` and `add_behavior.py` use `func: Callable` with no type
   parameters, which is `Callable[..., Any]`. This is reasonable (it is before
   `ParamSpec` is introduced), but sitting near the later fully-typed versions it
   can read like an omission. A half-sentence ("typing comes next; for now a bare
   `Callable`") would signal it is deliberate. Optional.

## Verified

- Ran all scripts: `simple_decoration` (Replacement behavior), `add_behavior`
  (Hijacked / Wensleydale / Hijacking over), `tracer` and `trace_class`
  (-> add(2, 3) / <- add = 5), `repeat` and `repeat_class` (Hello, Bob x3),
  `count_calls` (call 1 / hello / call 2 / hello / 2), `stacking`
  (-> greet('Bob',) / Hello, Bob x2 / <- greet = 'Bob'), `register`
  (['Espresso', 'Latte']), `coffee` (the two drink lines, $2.75 and $2.50). Every
  output matches the prose.
- `pytest` on the chapter: 3 passed (`test_coffee`).
- `ty`, `ruff`, `prose_lint`, `spellcheck` all clean.
- The recent changes hold up: the `ParamSpec` prose is accurate, the three class
  decorators now preserve signatures (`assert_type`-level confirmed earlier),
  `stacking.py` works, and the `tracer.py` rename resolved the stdlib `trace`
  shadow so the function form could be imported if needed.

This chapter is in good shape; the items above are polish.
