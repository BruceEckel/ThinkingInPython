<!-- outside review of Chapters/30_Patterns--Observer.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `30_Patterns--Observer.md` chapter:

**1. Section: Easier Names (contradictory method-naming claim)**

* **Target Text:** "Sending a change and receiving it share one name, `announce()`, where GoF has two."
* **Issue:** This contradicts both the table directly above and the sentence immediately preceding it ("The last row has no method name on the right. A responder is a callable, so the receiving end needs no specially-named method."). A responder does not share the method name `announce()`; it is an arbitrary callable.
* **Instruction:** Rephrase to clarify that broadcasting eliminates the second method name: "Broadcasting relies on one method name, `announce()`, where GoF has two (`notify()` on the subject and `update()` on the observer)."

**2. Section: The Pythonic Observer (typing specification error for `Callable[..., None]`)**

* **Target Text:** "The alias turns that silent discard into a type error. The type checker rejects a responder that returns a value, because the author of that responder likely expected someone to use the value."
* **Issue:** In the Python Typing Specification (PEP 484), `Callable[..., None]` is a special case: a callable returning any value is assignable to `Callable[..., None]` because caller code ignores the return value. A type checker does not reject a responder returning a value when annotated as returning `None`.
* **Instruction:** Replace the claim that the type checker rejects non-`None` return values with: "The alias documents that the broadcaster ignores return values. In Python's type system, `Callable[[T], None]` accepts callables with any return type because the caller discards whatever is returned."

**3. Section: Disconnecting During an Async Notification (misidentified beneficiary of unpacking)**

* **Target Text:** "The tuple also means a responder that disconnects itself mid-notification still receives this change, an async counterpart to `self_removing_responder.py`:"
* **Issue:** A responder that disconnects itself mid-notification has already been invoked (which is how it executes `disconnect()`). The argument unpacking protects subsequent responders (like `always`) from being skipped when `self._responders` shrinks mid-broadcast.
* **Instruction:** Update the sentence to name the responders that unpacking actually protects: "The tuple also ensures that disconnecting a responder mid-notification does not skip remaining responders, an async counterpart to `self_removing_responder.py`:"

**4. Section: Decorated Responders (factual error regarding `Generic.__init_subclass__`)**

* **Target Text:** "One of those bases is `Generic`, which `class Broadcasting[T]` adds, and its `__init_subclass__()` records that `Thermometer` takes no type parameter. If you leave the call out, the runtime accepts `Thermometer[int]`."
* **Issue:** Subscripting at runtime (`Thermometer[int]`) is handled by `Generic.__class_getitem__`, which checks `Thermometer.__parameters__` (populated during class construction, not inside `__init_subclass__`). `Generic.__init_subclass__` does not record type parameters, and omitting `super().__init_subclass__()` does not cause the runtime to accept `Thermometer[int]` (it still raises a `TypeError`).
* **Instruction:** Replace the explanation with the cooperative multiple inheritance rationale: "`super().__init_subclass__(**kwargs)` ensures cooperative multiple inheritance works as expected, allowing any sibling base classes or mixins in the subclass's MRO to execute their own `__init_subclass__()` hooks."

## Verdicts

Second run, on the Flash model. Applied in commit 1185bf25, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The sentence said sending and receiving "share" `announce()`, which reads as if a responder also carries that name, against the two sentences before it. It now reads "Broadcasting a change takes one method name, `announce()`, where GoF uses two."
2. Rejected. The first round rejected the same claim, and a rerun agrees: `uv run ty check` on `r: Responder[float] = returns_value`, with `returns_value()` returning `int`, reports `invalid-assignment` ("`int` is not assignable to `None`"), the rejection the chapter describes.
3. Applied, with a different fix. The tuple protects the responders after the one that disconnects, which the sentence before already says ("cannot skip a responder") and the prose after the listing shows with `always`; the disconnecting responder is running when it calls `disconnect()`, so the tuple adds nothing for it. The sentence now introduces the listing as the async counterpart to `self_removing_responder.py`, with a responder that disconnects itself mid-notification, and leaves the claim about `once` out.
4. Rejected. A probe under `uv run python` with a `class Base[T]` whose `__init_subclass__()` calls `super()` gave the subclass `__parameters__ == ()` and made `Sub[int]` raise a `TypeError`; the same class without the call left `__parameters__ == (T,)` and accepted `Sub[int]`. `Generic.__init_subclass__()` does record the parameters, as the chapter says, and the first round's item 3 applied this paragraph on the same evidence.
