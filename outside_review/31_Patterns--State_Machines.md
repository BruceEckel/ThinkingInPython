<!-- outside review of Chapters/31_Patterns--State_Machines.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `31_Patterns--State_Machines.md` chapter:

**1. Section: The Engine (Strict typing for `type`)**

* **Target Text:** `type Table = dict[tuple[Enum, type], list[Transition]]`
* **Issue:** In strict mode, type checkers may flag the bare `type` alias as missing its generic type parameter (`type[T]`). Using `type[object]` or `type[Any]` satisfies strict checks while still expressing that any class object is allowed as an event type key.
* **Instruction:** Change the line to: `type Table = dict[tuple[Enum, type[object]], list[Transition]]`

**2. Section: A View for the Vending Machine (Double-send on rejected first digit)**

* **Target Text:**
```python
    def select(r: int, c: int) -> None:
        send(FirstDigit(f"row {r}", r))
        send(SecondDigit(f"col {c}", c))
```
* **Issue:** If the `FirstDigit` event is rejected (e.g., if pressed before any money is inserted), `send()` catches the `NoTransition` exception, but `select()` continues and sends the `SecondDigit` anyway. This causes a second rejected event and a redundant UI render. Returning a boolean from `send()` allows `select()` to abort the sequence early.
* **Instruction:** Change `send`'s signature to `-> bool`, track success with a boolean to return after `render()`, and change `select` to abort if the first send fails:
```python
    def send(event: object) -> bool:
        success = True
        try:
            vm.handle(event)
        except NoTransition:
            vm.message = "not allowed yet"
            success = False
        render()
        return success

    def select(r: int, c: int) -> None:
        if send(FirstDigit(f"row {r}", r)):
            send(SecondDigit(f"col {c}", c))
```

**3. Section: Which Design Should You Use? (Initial state action in table design)**

* **Target Text:** "The action repeats on every row that leads to that state, or routes through a helper you write yourself."
* **Issue:** Because the table-driven design relies entirely on transitions to trigger actions, the machine does not automatically execute an entry action when it is initialized into its starting state. If the initial state requires an action (like broadcasting the cheese smell in the mousetrap), the table design requires an explicit startup event to trigger it, which is an important design difference to highlight.
* **Instruction:** Add a sentence immediately following the target text: "This also means the initial state's action is never run automatically; if the machine must do something on startup, you must feed it a starting event."

## Verdicts

Applied in commit 08050ef2, after each item was tested against the chapter and run under `uv run`.

1. Rejected. `uv run ty check` on the extracted `table_machine.py` and `vending_machine.py` passes, and `uv run pyright` on a copy of `table_machine.py` with `# pyright: strict` reports 0 errors, so neither checker flags the bare `type` in `Table`; the gate runs `ty` alone, which has no strict mode.
2. Rejected. A probe of `send()` and `select()` against the extracted listings showed the one rejection case is `QUIESCENT`, where `SecondDigit` is rejected too and leaves the same message and state; `select()` always moves the machine out of `SELECTING`, so a rejected first digit never lets the second through. The extra `render()` repaints identical text, so the guard adds defensive code to a teaching listing with no visible effect.
3. Applied, with a different fix. The difference is real: `state_machine.py`'s constructor calls the initial state's `run()`, while `table_machine.py`'s stores `initial` and runs nothing. The "Which Design Should You Use?" paragraph now says startup bypasses the table and that a startup action is a call you make before the first event; a synthetic starting event would need a table row the vending machine has no use for.
