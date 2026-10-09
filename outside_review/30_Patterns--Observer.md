<!-- outside review of Chapters/30_Patterns--Observer.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `30_Patterns--Observer.md` chapter:

**1. The Pythonic Observer (Type checking clarification)**

* **Target Text:** "The type checker rejects a responder that returns a value, because the author of that responder likely expected someone to use the value. The alternative alias `Callable[[T], object]` accepts any callable that takes a `T`, since every return type, `None` included, is assignable to `object`."
* **Issue:** PEP 484 explicitly specifies that `Callable[..., None]` means the callback's return value will be ignored. As a result, standard type checkers will actually *accept* a responder that returns a value without emitting an error. Using `Callable[[T], object]` instead would incorrectly signal that `announce()` might read and use the returned value.
* **Instruction:** Replace those sentences with: "The type checker accepts a responder that returns a value, because `Callable`'s `None` return type tells the checker that `announce()` will safely ignore any returned value. The alternative alias `Callable[[T], object]` would falsely signal that `announce()` might use the returned value."

**2. Decorated Responders (Behavioral mismatch clarification)**

* **Target Text:** "Now the subclass behaves as if its author had written `thermometer.py`'s constructor and property pair."
* **Issue:** This is not strictly true. `thermometer.py`'s manual constructor explicitly bypasses the setter by assigning to `self._celsius` to deliberately avoid a notification during initialization. In contrast, the `dataclass`-generated constructor for `Broadcasting` assigns to `self.celsius`, which triggers the property setter and calls `announce()`. The behavior differs, although it remains safe because the responders list is empty during construction.
* **Instruction:** Replace the sentence with: "The generated constructor acts slightly differently than `thermometer.py`'s: it assigns to `self.celsius`, triggering the property setter and calling `announce()`. This remains safe because the responders list is empty during construction."

**3. Decorated Responders (Cooperative inheritance caveat)**

* **Target Text:** `def __init_subclass__(cls) -> None:`
* **Issue:** `__init_subclass__` should accept `**kwargs` and pass them to `super().__init_subclass__(**kwargs)` to properly support multiple inheritance and cooperate with other base classes. Without this, inheriting from `Broadcasting` alongside another class that requires subclass arguments will break the Method Resolution Order (MRO) chain and raise a `TypeError`.
* **Instruction:** Replace the line with: `def __init_subclass__(cls, **kwargs: Any) -> None:` and insert `super().__init_subclass__(**kwargs)` as the first line of the method body. (Ensure `Any` is imported from `typing` if not already present).

## Verdicts

Applied in commit f243ed77, after each item was tested against the chapter and run under `uv run`.

1. Rejected. PEP 484 has no rule that a `None` return in `Callable` accepts any return type; `uv run ty check` on `r: Responder[float] = returns_value`, with `returns_value()` returning `int`, reports `invalid-assignment` ("`int` is not assignable to `None`"), which is the rejection the chapter describes.
2. Applied, with a different fix. A traced `announce()` showed `Thermometer(100)` calling it once with zero responders, while `thermometer.py`'s constructor bypasses the setter on purpose. The sentence now says the subclass behaves like `thermometer.py`'s pair with one difference: the generated `__init__()` assigns through the property, so construction calls `announce()`, which notifies no one.
3. Applied, with a different fix. Without the `super()` call, `Generic.__init_subclass__()` never runs for `Thermometer`: `Thermometer.__parameters__` stayed `(T,)` and `Thermometer[int]` succeeded at runtime, and a second base's `__init_subclass__()` was skipped. `broadcasting.py` (and exercise 12's copy in Solutions) now uses chapter 17's form, `**kwargs: object` rather than `Any`, after which `Thermometer[int]` raises a `TypeError`; a new paragraph explains the call.
