<!-- outside review of Chapters/28_Patterns--Function_Objects.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `28_Patterns--Function_Objects.md` chapter:

**1. An Event Bus: Handlers Keyed by Type (Type checker error in internal list)**

* **Target Text:**
```python
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)
```
(and later) "Its lists cannot name a single event class, so their element type is `Handler[Any]`."
* **Issue:** Function types are contravariant in their arguments. A handler for a specific event (like `Callable[[Deposit], None]`) is not a subtype of `Handler[Any]` (which demands a function that can accept *any* object). Appending specific handlers to a `list[Handler[Any]]` will be flagged as an error by strict type checkers like `pyright`.
* **Instruction:** Change the list's element type to `Any` to safely store heterogeneous callables:
```python
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Any]
        ] = defaultdict(list)
```
Then replace the target prose sentence with: "Its lists cannot name a single event class, so their element type is `Any`."

**2. A Tagged Bus: Handlers That Name Their Event (Type checker error on subscribe)**

* **Target Text:**
```python
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Handler[Any]]
        ] = defaultdict(list)

    def subscribe(self, handler: Handler[Any]) -> None:
```
* **Issue:** Because functions are contravariant, passing a concrete handler (like `Handler[Deposit]`) to `subscribe(handler: Handler[Any])` causes a type error at the call site for every valid handler. The text accurately claims that the tagged bus passes the type checker because there is "no pair to compare," but this only holds if `subscribe` infers the event type generically instead of demanding `Handler[Any]`.
* **Instruction:** Make `subscribe` generic over `E` so it cleanly accepts any specific handler, and update the internal list to `Any` as in the previous section:
```python
    def __init__(self) -> None:
        self._handlers: defaultdict[
            type, list[Any]
        ] = defaultdict(list)

    def subscribe[E](self, handler: Handler[E]) -> None:
```

**3. A Tagged Bus: Handlers That Name Their Event (Callable class vs function object terminology)**

* **Target Text:** "`@handler` makes a function object whose fields are its configuration, and stores in `HANDLES` the event its `__call__()` accepts."
* **Issue:** The `@handler` decorator produces a frozen dataclass, which is a class, not a function object. The chapter carefully distinguishes between plain functions and callable objects, dedicating the earlier section "A Callable Object as a Command" specifically to classes with `__call__()`.
* **Instruction:** Change "function object" to "callable class" to match the chapter's taxonomy. Replace the sentence with: "`@handler` makes a callable class whose fields are its configuration, and stores in `HANDLES` the event its `__call__()` accepts."

## Verdicts

Applied in commit c7ce7764, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The parameter type in `Handler[Any]` is `Any`, which is assignable in both directions, so a handler for any one event type fits it; the item confuses `Any` with `object`. A probe appending a `(Deposit) -> None` function to a `list[Handler[Any]]` passes both `ty` and Pyright 1.1.414 in strict mode, while the same append to a `list[Handler[object]]` draws an error from each, and `event_bus.py` with its demo checks clean under both.
2. Rejected. The same `Any` reasoning applies: `tagged_bus_demo.py`'s `bus.subscribe(Announce("+"))` checks clean under `ty` and Pyright strict. A generic `subscribe[E]()` would add nothing, since `E` appears in one parameter and constrains nothing, and the chapter's point that one argument leaves "no pair to compare" holds as written.
3. Applied, with a different fix. The sentence is imprecise: `@handler` returns a class, and its instances are the function objects. The reviewer's "callable class" fits poorly, since the chapter says a few paragraphs later that every class is callable. The sentence now reads "`@handler` makes a class whose instances are function objects, with fields that hold their configuration".
