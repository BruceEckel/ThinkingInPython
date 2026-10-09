<!-- outside review of Chapters/28_Patterns--Function_Objects.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `28_Patterns--Function_Objects.md` chapter:

**1. Section: A Tagged Bus: Handlers That Name Their Event (handler instance versus class in static type check)**

* **Target Text:** "so a class with the right `__call__()` that skipped `@handler` passes the type checker and fails only when `subscribe()` looks it up."
* **Issue:** `EventBus.subscribe()` has the signature `def subscribe(self, handler: Handler[Any]) -> None:`. Passing a class itself (e.g. `Plain`) fails static type checking because `type[Plain]` does not satisfy the `Handler[Any]` protocol. An *instance* of such an undecorated class (e.g. `Plain()`, as exercised in `test_subscribe_rejects_an_undecorated_class()`) satisfies `Handler[Any]`, passes the type checker, and fails only at runtime when `subscribe()` queries `HANDLES`.
* **Instruction:** Change "so a class with the right `__call__()` that skipped `@handler` passes the type checker and fails only when `subscribe()` looks it up." to "so an instance of a class with the right `__call__()` that skipped `@handler` passes the type checker and fails only when `subscribe()` looks it up."

**2. Section: A Tagged Bus: Handlers That Name Their Event (handler instance versus class in test summary)**

* **Target Text:** "- `subscribe()` refuses a class that skipped `@handler`."
* **Issue:** `EventBus.subscribe()` accepts handler instances rather than class objects; passing a class object would cause `type(handler).__name__` to evaluate to `"type"` rather than the class's name. The accompanying test `test_subscribe_rejects_an_undecorated_class()` confirms this by passing an instance, `EventBus().subscribe(Plain())`.
* **Instruction:** Change "- `subscribe()` refuses a class that skipped `@handler`." to "- `subscribe()` refuses an instance of a class that skipped `@handler`."

**3. Section: A Tagged Bus: Handlers That Name Their Event (event instance versus class in parameter type rationale)**

* **Target Text:** "`publish()` keeps its `object` parameter,
because no static type means "a class `@event` decorated",
so a stray string reaches the bus and `EVENTS` rejects it there."
* **Issue:** `EventBus.publish()` accepts event instances (such as `Deposit(100)` or `"Deposit"`), not class objects. Passing a class object such as `Deposit` directly fails at runtime because `type(Deposit)` is `type`, which is not in `EVENTS`. The expressiveness limitation in Python's type system is that no static type denotes an instance of a class decorated with `@event`.
* **Instruction:** Change "because no static type means "a class `@event` decorated"," to "because no static type means "an instance of a class decorated with `@event`","

## Verdicts

Second run, on the Flash model. Applied in commit de914628, after each item was tested against the chapter and run under `uv run`.

1. Applied. A probe against the extracted `tagged_bus.py` showed `ty` accepting `bus.subscribe(Plain())` and rejecting `bus.subscribe(Plain)` with `invalid-argument-type` (`<class 'Plain'>` is not assignable to `Handler[Any]`, parameter `event` missing), so the sentence's "a class ... passes the type checker" was wrong for the class object. The sentence now reads "so an instance of a class with the right `__call__()` that skipped `@handler` passes the type checker".
2. Applied. Under `uv run python`, `EventBus().subscribe(Plain())` raises a `TypeError` reading "Plain is not a @handler", while `subscribe(Plain)` reads "type is not a @handler", and the test passes `Plain()`. The bullet now reads "`subscribe()` refuses an instance of a class that skipped `@handler`."
3. Applied. `EventBus().publish(Deposit)` raises a `TypeError` reading "type is not an @event", so the parameter takes event instances, and the missing static type is one for an instance. The quoted phrase now reads "an instance of a class decorated with `@event`".
