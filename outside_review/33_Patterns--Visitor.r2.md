<!-- outside review of Chapters/33_Patterns--Visitor.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `33_Patterns--Visitor.md` chapter:

**1. Section: The Classic Visitor (Double dispatch naming contradiction)**

* **Target Text:** "The `accept()`/`visit()` pair is the *double dispatch*. `accept()` passes the concrete flower to the visitor, `visit()` resolves the visitor's type, and the `pollinate()` or `eat()` call inside `visit()` resolves the flower's type."
* **Issue:** In `flower_visitors.py`, `Flower.accept()` is a single inherited method that does no polymorphic resolution. The two dynamic dispatches that select runtime behavior are `visitor.visit()` (resolving to `Pollinator.visit` or `Predator.visit`) and `flower.pollinate()` / `flower.eat()` (resolving to `Flower.eat` vs `Chrysanthemum.eat`), as confirmed by the subsequent discussion of `dispatch_trace.py` naming `visit` the first dispatch and `eat` the second dispatch.
* **Instruction:** Rephrase to distinguish the classic GoF pair from the two dispatches that actually occur in `flower_visitors.py`. Proposed wording: "In the classic pattern, the `accept()`/`visit()` pair is the *double dispatch*. In `flower_visitors.py`, `accept()` is merely a trampoline: the two dispatches that resolve types are `visit()` (which resolves the visitor's type) and the `pollinate()` or `eat()` call inside `visit()` (which resolves the flower's type)."

**2. Section: The Pythonic Visitor: singledispatch (Statically stubbed parameters vs runtime construction)**

* **Target Text:** "`ty` and Pyright accept `nectar(42)` too, because the dispatcher that `@singledispatch` builds declares its parameters as `Any`."
* **Issue:** Static type checkers like `ty` and Pyright do not inspect runtime dispatch wrappers built by decorator execution. They accept `nectar(42)` because typeshed's `_SingleDispatchCallable` stub declares `__call__()` with `*args: Any` instead of preserving parameter types from the decorated base function.
* **Instruction:** Attribute the type checkers' behavior to typeshed's stub signature rather than runtime object construction. Proposed wording: "`ty` and Pyright accept `nectar(42)` too, because typeshed's stub for `_SingleDispatchCallable` declares `__call__()` with `*args: Any` rather than typing the call from the base function's signature."

**3. Section: One Dispatch Is Enough (Dispatch order inverted from classic GoF)**

* **Target Text:** "The second dispatch in the classic pattern exists not because two types are unknown, but because the operation must be a method on some class. The visitor's type stands in for the operation, so the language must resolve that type at runtime along with the element's type."
* **Issue:** In the classic GoF pattern, the element's `accept()` override executes first, resolving the element's type, and the visitor's `visitConcreteElement()` method executes second, resolving the operation. However, the chapter's Python implementation in `flower_visitors.py` executes these in reverse order (`visit()` first to choose the operation, then `pollinate()`/`eat()` second to choose the element implementation), making "the second dispatch in the classic pattern" confusing when read against `dispatch_trace.py`'s trace where the element dispatch was second.
* **Instruction:** Clarify which dispatch resolves the operation in classic GoF versus `flower_visitors.py`. Proposed wording: "In the classic pattern, resolving the visitor's type is the second dispatch (following `accept()`), whereas in `flower_visitors.py` it is the first; in both cases, that extra dispatch exists not because two types are unknown, but because the operation must be a method on a class."

## Verdicts

Second run, on the Flash model. Applied in commit 19adcb92, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The paragraph opened by calling the `accept()`/`visit()` pair the double dispatch and then described `flower_visitors.py`, where the inherited `accept()` resolves nothing and `dispatch_trace.py` names `visit()` and `eat()` as the two dispatches. The paragraph now says the pair is the double dispatch "in the classic pattern," where the `accept()` override resolves the element's type and its `visit()` call the visitor's, then describes `flower_visitors.py` separately; "trampoline" was left out as jargon the chapter never introduces.
2. Rejected. The Pro run's item 3 tested the same claim. Rerun against the extracted `visitor_singledispatch.py`, `ty` reveals `nectar` as `_SingleDispatchCallable[str]` with `__call__(...) -> str` and checks `nectar(42)` cleanly, which the runtime answers with `42: no nectar`; "the dispatcher that `@singledispatch` builds declares its parameters as `Any`" describes that type, so the sentence holds.
3. Applied, with a different fix. "The second dispatch in the classic pattern" counts in GoF order (`accept()` first), while `dispatch_trace.py` a few sections earlier calls the `visit()` dispatch the first, so the ordinal pointed two ways. The sentence now names it by what it resolves, "The dispatch on the visitor's type," which reads the same against either order.
