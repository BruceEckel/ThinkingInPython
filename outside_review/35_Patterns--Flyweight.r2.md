<!-- outside review of Chapters/35_Patterns--Flyweight.md, model gemini-3.8-flash-high, 2026-10-09 -->

**Please apply the following technical and structural refinements to the `35_Patterns--Flyweight.md` chapter:**

**1. Section: Exercises (Exercise 7 trade-off phrasing)**

* **Target Text:** "What does the type checker now catch that the `Literal` version caught, and what does it catch that the `Literal` version did not?"
* **Issue:** The question is intended to contrast what is lost versus gained when moving from `Literal` to `Enum`. Calling out what the type checker "now catches" that `Literal` already caught is contradictory; with `Tile(s)`, the type checker now *misses* invalid symbol strings that `to_symbol()` and `Literal` caught statically, while it *gains* exhaustive `match` checking across members.
* **Instruction:** Replace "now catch that the `Literal` version caught" with "now miss that the `Literal` version caught". The sentence should read: "What does the type checker now miss that the `Literal` version caught, and what does it catch that the `Literal` version did not?"

**2. Section: Interning in the Constructor (contradictory explanation of `defaultdict`)**

* **Target Text:** "A `defaultdict` calls its `default_factory` with no arguments, and building a `Color` needs the three components, so `_pool` stays a plain dict with an explicit membership test."
* **Issue:** The claim that building a `Color` needs the three components contradicts the preceding paragraph, which explains that `__new__()` deliberately builds a bare instance via `super().__new__(cls)` without components and leaves initialization to `__init__()`. The real limitation of `defaultdict` is that its factory does not receive the lookup key, making it unsuitable for key-dependent pooling.
* **Instruction:** Reframe the sentence to explain that `defaultdict`'s factory does not receive the key. Change the sentence to: "A `defaultdict` calls its `default_factory` with no arguments and does not receive the missing key, so `_pool` stays a plain dict with an explicit membership test."

**3. Section: Python Uses Flyweights (scope of string interning)**

* **Target Text:** "String *interning* keeps one copy of identifier-like strings."
* **Issue:** String interning as a pattern—and `sys.intern()` as demonstrated in the listing—is not restricted to identifier-like strings; it can intern arbitrary strings. CPython automatically interns identifier-like strings at compile time, but stating categorically that string interning keeps one copy of "identifier-like strings" confuses an internal CPython heuristic with the general flyweight facility.
* **Instruction:** Clarify that while CPython automatically interns identifiers, interning in general applies to arbitrary strings. Change the sentence to: "String *interning* keeps one copy of each distinct string. CPython automatically interns identifier-like strings, and `sys.intern()` extends the technique to arbitrary strings:"

**4. Section: A Pool That Does Not Leak (`@record` decorator interface)**

* **Target Text:** "`record()` does not pass `weakref_slot` through, so `Name` writes the `dataclass` call in full."
* **Issue:** Across the book, `@record` is a parameterless decorator defined in `utils/record.py`, not a callable factory invoked as `record(...)`. Phrasing it as "`record()` does not pass `weakref_slot` through" implies that `record` accepts keyword arguments that it fails to forward to `dataclass()`, rather than being a zero-argument decorator with a fixed configuration.
* **Instruction:** Rephrase to reflect that the decorator does not take options. Change the sentence to: "`@record` provides no `weakref_slot` option, so `Name` writes the `dataclass` call in full."

## Verdicts

Second run, on the Flash model. Applied in commit 39a59728, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The item's premise is wrong: the `Literal` version never caught a symbol arriving as data, since `@cache` hides `tile()`'s `Symbol` parameter and `to_symbol()` is a runtime check, and Solutions 35 exercise 7 answers the question as written, opening with "The type checker still catches what the `Literal` version catches." The reviewer's misreading shows that "now catch" read as a contradiction, so the exercise says "still catch" instead of "miss".
2. Applied, with a different fix. A probe giving `Color` a `defaultdict(lambda: object.__new__(Color))` pool with `return cls._pool[(red, green, blue)]` printed `Color(red=220, green=20, blue=60) True 1`, so building the pooled object needs no components, and the chapter's reason was wrong; the key is not needed either, so the reviewer's reason is wrong too. A subclass built through the same probe came back a bare `Color` that raised an `AttributeError` on `repr()`, because the factory cannot see `cls`, so the sentence now says `super().__new__(cls)` needs the class that asked.
3. Applied. Under `uv run`, two separately compiled `"flyweight"` constants were the same object while two `"fly weight!"` constants were not, and `sys.intern()` mapped two joined `"fly weight!"` strings to one object, so interning covers any string and CPython's automatic interning covers identifier-like constants. The sentence now says both.
4. Rejected. `utils/record.py` is dual-form, `record(cls)` or `record(*, slots: bool = True)`, and chapter 18 teaches the called form `@record(slots=False)`, so `record()` takes an option and does not forward `weakref_slot`, which is what the chapter says.
