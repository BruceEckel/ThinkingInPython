# Deep review: 31_State_Machines.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Print the state in the vending-machine demo

**Kind:** teaching
**Where:** section "A Vending Machine" (line ~569, the `__main__` block of `tabledriven/vending_machine.py`)
**Problem:** The chapter's whole claim is that a table moves the machine between states, but the demo output never shows a state. The reader sees messages only, and cannot narrate the mechanism from the output. It is worse than merely incomplete: the too-expensive case and the sold-out case produce *the same kind of message* ("Clearing selection: costs 75, quantity 5" vs. "costs 25, quantity 0") and land in *different* states (COLLECTING vs. UNAVAILABLE). The state is the only observable difference between the two conditional branches the chapter just spent a paragraph explaining, and it is the one thing the demo hides.
**Proposal:** print the state alongside the message. Replace the demo loop's print with

```python
    machine = VendingMachine()
    for event in events:
        machine.handle(event)
        print(f"{event}: {machine.message} [{machine.state.name}]")
```

and the markers with (verified by running it; the `# Text view` comment has to go, since the line would otherwise exceed 70 characters, and the prose after the tests already explains the view idea):

```
#: quarter: Total = 25 [COLLECTING]
#: quarter: Total = 50 [COLLECTING]
#: dollar: Total = 150 [COLLECTING]
#: A: Row A [SELECTING]
#: two: Dispensing; remaining 100 [WANT_MORE]
#: A: Row A [SELECTING]
#: two: Dispensing; remaining 50 [WANT_MORE]
#: C: Row C [SELECTING]
#: three: Clearing selection: costs 75, quantity 5 [COLLECTING]
#: D: Row D [SELECTING]
#: one: Clearing selection: costs 25, quantity 0 [UNAVAILABLE]
#: Quit: Returning 50 [QUIESCENT]
```

Then add one sentence after the listing, something like:
"The two `Clearing selection` lines read alike and end in different states:
too expensive returns to `COLLECTING` with the money still in,
while sold out goes to `UNAVAILABLE`.
The condition that fired is visible only in the state."

**Cost:** rewrites twelve `#:` markers in the one listing. `test_vending.py` asserts on `vm.message` and `vm.state` separately and is unaffected. `vending_view.py` builds its own display string and is unaffected.
*Alternative:* leave the demo alone and add a second, shorter listing that prints only the state sequence. That costs a listing and repeats the event list, so I prefer the change above.

---

## 2. Say why the inputs stopped being enum members and became objects

**Kind:** teaching
**Where:** section "Table-Driven State Machine", before "The Engine" (line ~378)
**Problem:** In the mousetrap the inputs are `MouseAction` members and the tables key on a *value*. In the vending machine the inputs are classes and the table keys on a *type*. That is the largest representational change in the chapter, and the prose never names it. The reader is left to infer that the engine's `type(event)` keying is an arbitrary style choice rather than forced by the events now carrying data.
**Proposal:** insert after "and the table is an ordinary `dict`" (line ~390):

"The inputs change shape too.
The mousetrap's inputs were `MouseAction` members, names with nothing attached.
A vending machine's inputs carry values: what a coin is worth, which digit was pressed.
So each input becomes an object of its own class,
and the table keys on that class rather than on a value.
An enum member has no room for the twenty-five cents."

**Cost:** none. It sets up the `type(event)` discussion in "The Engine" that follows.

---

## 3. Give the chapter a closing section

**Kind:** structure
**Where:** after `tabledriven/vending_view.py`, before "## Exercises" (line ~746)
**Problem:** The chapter stops on a `tkinter` listing that the test harness skips, then drops straight into exercises. Nothing names what the reader can now do, and nothing places state machines outside a mousetrap and a vending machine. Chapters 35, 36, and 37 all end with a short section that adds a new angle ("Flyweights in the Wild", "Snapshots in the Wild", "Choosing the Lightest Construct"); this one ends mid-example.
**Proposal:** a short `## State Machines in the Wild` (or `## When the Table Is the Program`) with two or three paragraphs that add rather than recap:

- where these already run: a regular expression compiles to a state machine, a protocol parser (HTTP request framing, a TLS handshake) is one, a lexer is one, and `asyncio`'s transports track connection state the same way.
- the transferable point: once the machine is a `dict`, it is *data*. You can generate it from a diagram, walk it to find states no input can reach, print it back out as a diagram, or diff two versions of it. None of that is possible when the transitions are spread across `if` branches in methods.
- the honest limit: a table pays off past roughly a handful of states. Below that, the `match` in `Waiting.next()` is easier to read, and the first mousetrap is not a worse program than the second.

**Cost:** adds a heading, so the site TOC gains a row. No existing cross-reference names a section after "A Vending Machine", so nothing breaks.

---

## 4. Warn that the second half reuses `State` and `StateMachine` for different things

**Kind:** teaching
**Where:** opening of "Table-Driven State Machine" (line ~371)
**Problem:** By line 460 the chapter has two classes named `StateMachine` (in two files both named `state_machine.py`), and `State` has gone from an abstract base class with `run()` and `next()` to an `Enum` of names with no behavior. A reader skimming back to the earlier listing to compare will read the wrong one. The chapter is aware of the clash (exercise 2 spells out the path `tabledriven/state_machine.py`) but never tells the reader.
**Proposal:** add to the opening paragraph of the section:

"The names restart here.
`tabledriven/state_machine.py` holds a different `StateMachine` from the one above,
and `State` is now an `Enum` of names rather than a base class with behavior.
The states in this design do nothing; the table holds all the behavior."

**Cost:** none. It also makes proposal 11's exercise fix read naturally.

---

## 5. Give the first half a heading

**Kind:** structure
**Where:** line 1 through line ~369
**Problem:** The chapter runs 370 lines, two complete mousetrap programs, and the unexpected-input discussion before its first `##`. In the generated site TOC the chapter appears to consist of "Table-Driven State Machine" and its two subsections, with the entire first design invisible. It also leaves the second half's title implicitly contrasting with something unnamed.
**Proposal:** insert `## Each State Decides` (the phrase already used at line 78) after the opening two paragraphs, just before the `state.py` listing. Optionally add `### An Unexpected Input` before the paragraph at line ~357, which is a distinct topic that currently trails the second mousetrap.
**Cost:** two new anchors; no chapter links into the first half today, so nothing breaks. If the second sub-heading is added, `heading_links.py` must still pass (it will; nothing references it).

---

## 6. Note that every action and condition is called with the event

**Kind:** teaching
**Where:** section "The Engine", after the listing (line ~433)
**Problem:** The engine always calls `condition(event)` and `action(event)` with one argument. A reader writing their own table would reasonably write a zero-argument action and get a `TypeError` at the first transition. The chapter never states the calling convention, and the evidence for it is buried in `refund(self, event: object)`, which accepts an argument it ignores and looks like a mistake.
**Proposal:** add after "The engine tries them top to bottom, ...":

"Both callables receive the event, whether they need it or not,
which is why `refund()` takes an argument it ignores.
The `Callable[..., bool]` and `Callable[..., None]` annotations leave the parameters as `...`
because each method declares the specific event type it handles,
and no one signature covers them all."

**Cost:** none.

---

## 7. Mention `ABC` as the third option for the `State` base

**Kind:** teaching
**Where:** section around `state.py` (lines 34-41)
**Problem:** The chapter weighs `raise NotImplementedError` against `class State: pass` and stops there. [Surrogate](26_Surrogate.md#proxy) already taught the reader `ABC` and `@abstractmethod`, with `proxy_interface.py` showing that an incomplete subclass fails at construction rather than at the call. That is precisely the failure mode being discussed here, and the reader who just met it will ask why the chapter did not use it. "A slightly different error message" also understates the difference: without the base, the failure is an `AttributeError`, not a message variation.
**Proposal:** keep the listing as written and extend the discussion, along these lines:

"Without the base, the failure is an `AttributeError` at the call.
With it, a `NotImplementedError` that names what is missing.
[Surrogate](26_Surrogate.md#proxy) shows the third option:
make `State` an `ABC` with `@abstractmethod` on both methods,
and an incomplete subclass cannot be constructed at all.
The version here fails later than that, at the call rather than at construction,
which is enough for a design where every state is created once at module level."

*Alternative:* switch `state.py` to `ABC`/`@abstractmethod` outright. That is closer to the book's own advice, but it changes both mousetrap listings' base class and loses the "this class is unnecessary" opening, which is a point worth keeping. I prefer the prose fix.
**Cost:** none for the prose version.

---

## 8. Contrast `run_all()`'s `print(i)` with the vending machine's recorded message

**Kind:** teaching
**Where:** section "A Vending Machine", around the tests (line ~665)
**Problem:** The first `StateMachine.run_all()` prints its input from inside the framework. The vending machine deliberately does not print, and the prose explains why ("the model never draws anything"). The chapter has therefore shown the mistake and the fix a hundred lines apart without connecting them, and a reader could copy `run_all()` as the recommended shape.
**Proposal:** extend the paragraph at line ~665:

"Contrast `run_all()` in the first design, which prints its input from inside the framework.
That is convenient for a book listing and wrong for a reusable machine:
it fixes one output device into the engine.
Recording a message instead pushes the choice out to whoever is watching."

**Cost:** none, though it puts a mild criticism on a listing the chapter presents straight. If that is unwelcome, the alternative is a one-clause aside at `run_all()` itself instead.

---

## 9. Sharpen the Template Method claim

**Kind:** prose
**Where:** lines 67-71
**Problem:** "As [Template Method](25_Template_Method.md) puts it, subclasses supply the steps, not the flow" does not describe this code. The varying steps live in `State` subclasses, which are not subclasses of `StateMachine`, the class holding the template method. `MouseTrap` *is* a `StateMachine` subclass and supplies no steps at all, only the initial state. A reader trying to match the sentence to the code finds the pieces in the wrong places.
**Proposal:** replace the sentence with:

"[Template Method](25_Template_Method.md) puts the varying steps in a subclass;
here they come from the `State` objects the machine holds.
The flow is fixed either way, and only where the steps live changes."

**Cost:** none. The `# Template method:` comment in the listing stays accurate.

---

## 10. Move the state diagram to the section it illustrates, and describe it

**Kind:** structure
**Where:** line ~392, `![Vending machine state diagram](_images/stateMachine)`
**Problem:** The vending machine has not been mentioned when this image appears; the sentence above it is about Java class hierarchies and the section below it is the generic engine. A reader meets a diagram of a machine they have not been told about, three pages before the machine arrives. The alt text is also the shortest in the book: every other image in `Chapters/` carries a full sentence describing what the drawing shows, which is what tells whoever draws it what to draw.
**Proposal:** move the image into "A Vending Machine", just after the paragraph that describes what the machine does (line ~453), and expand the alt text to the book's usual form, for example:

`![Five states, QUIESCENT, COLLECTING, SELECTING, UNAVAILABLE, and WANT_MORE; money loops COLLECTING back on itself, a first digit moves to SELECTING, and a second digit branches three ways on price and stock, while Quit refunds from any state back to QUIESCENT](_images/stateMachine)`

**Cost:** none; the file reference is unchanged.

---

## 11. Disambiguate `state_machine.py` in exercises 5, 6, and 7

**Kind:** exercise
**Where:** "Exercises" 5-7 (lines ~761-764)
**Problem:** Two files in this chapter are named `state_machine.py` and hold different `StateMachine` classes. Exercise 2 spells out `tabledriven/state_machine.py`; exercises 5, 6, and 7 say "using `state_machine.py`" and do not say which. An elevator and an HVAC system both want conditions on the transitions, which only the table-driven engine has, so the reader who picks the first one hits a wall.
**Proposal:** name the file in each. My reading of the intent: exercise 5 (the mood machine) suits the first design, exercises 6 and 7 (elevator, heating/AC) suit `tabledriven/state_machine.py`, since both need conditions. Please confirm or override, since this is your call.
**Cost:** none.

---

## 12. Make `StateT.next()`'s failure name the state and the input

**Kind:** code
**Where:** `mouse_trap2.py`, `StateT.next()` (lines ~270-275)
**Problem:** Two things. The message `"Input not supported for current state"` names neither the state nor the input, so a reader who triggers it while doing exercise 4 learns nothing; the table-driven engine's message twenty pages later gets this right (`f"no transition from {self.state!r} on ..."`), which makes the earlier one look like an oversight. And the lookup is LBYL (`if event in self.transitions: return self.transitions[event]`) where the book's own style prefers EAFP for a dict lookup, with no stated reason for the exception.
**Proposal:**

```python
    @override
    def next(self, event: object) -> State:
        try:
            return self.transitions[event]
        except KeyError:
            raise RuntimeError(
                f"{type(self).__name__} has no transition "
                f"for {event}") from None
```

**Cost:** none to output; the exception is never raised on this input file, so no `#:` marker changes. Verify the lines stay under 70 characters after sync.
*Alternative:* keep the LBYL shape and only improve the message. That fixes the reader-facing half and leaves the style deviation.

---

## 13. Tighten the `StrEnum` description

**Kind:** prose
**Where:** lines 97-98
**Problem:** "Because it is a `StrEnum`, each member is its string value. Members also compare equal to their equivalent string." Read literally the first sentence claims identity, which is false (`MouseAction.APPEARS is "mouse appears"` is `False`), and the second sentence then restates the weaker, true claim, so the pair reads as a correction of itself.
**Proposal:** "Because it is a `StrEnum`, each member *is* a `str`, and compares equal to and prints as its value. That is why `print(i)` in `run_all()` shows `mouse appears` rather than `MouseAction.APPEARS`."
**Cost:** none. The added second sentence explains an output line the reader is about to see and cannot otherwise account for.

---

## 14. Rewrite exercise 8's definition of "generator"

**Kind:** exercise
**Where:** exercise 8 (lines ~765-770)
**Problem:** "A *generator* produces objects, like a factory but taking no arguments" is the Java-era sense of the word, and the same exercise then says to write one "using `yield`", which is the Python sense. The book already reconciles the two in [Factory](27_Factory.md) with a link to [Iterators](23_Iterators.md#generators), so this local re-definition adds a collision the reader has to untangle.
**Proposal:** drop the definition and link instead: "Write a `mouse_move_generator()` ([Iterators](23_Iterators.md#generators)) that yields valid `MouseAction` moves in sequence, where each possible move depends on the previous one (it is another state machine). Have it accept an `int` for the number of moves to produce, then stop."
**Cost:** none.

---

## 15. Small items

**Kind:** prose | code
**Where:** various
**Problem and proposal**, one line each; take or leave them individually:

- **line ~544:** the two-line comment "Actions record a message instead of printing, so the model does not touch the screen; a view reads vm.message and displays it" says the same thing as the prose at line ~665. Per house style the explanation belongs in prose; delete the comment.
- **line ~76:** "A `State` whose `run()` reads attributes off the machine revives the trap" is exactly what exercise 3 asks the reader to build ("Each state stores a reference back to the controller object"). Point at it: "...revives the trap, which is worth remembering during exercise 3."
- **line ~677:** "The button loop builds sixteen commands with `partial(select, r, c)`, not with a lambda" sits directly below three buttons that *do* use lambdas. Add "(the three fixed buttons above use lambdas safely, since they close over nothing that varies)" so the reader does not conclude that lambdas are the problem.
- **`StateT`:** in a book that uses PEP 695 generics throughout, a trailing `T` reads as a type parameter. `TableState` says what it is. Renaming touches `mouse_trap2.py` only.
- **line ~573:** `SecondDigit("two", 1)` displays as `two` while indexing column 1, next to a comment reading `# Buy [0][1]`. A reader checking the arithmetic stumbles. `SecondDigit("col 1", 1)` (or a 0-based name) removes it.
- **line 11:** *Template Method* is named here and only linked at line 70. Move the link to the first mention.
- **Exercises:** nothing in the set exercises the ordered-conditions feature, which is the table-driven engine's one non-obvious mechanism. Exercise 2's washing machine could ask for it explicitly: "give one `(state, input)` pair two rows told apart by a condition, such as a load too heavy for the fast spin."

**Cost:** none individually.

---

## Already fixed directly (no decision needed)

- line ~388: "because in Java a method is not a value you can store in a table" is version-stale. Java 8 (2014) added lambdas and method references, so a modern Java version of this table would store `Predicate`/`Consumer` values and need no `Condition`/`Transition` hierarchies. Changed to "because the Java of the time had no way to store a method as a value", which keeps the point about the original version without asserting something false about Java now.
- line ~351: dropped "exactly" from "the output continues exactly as in the first version" (watch-list intensifier; the sentence says the same without it).
- line ~604: "check where it lands" used "lands", on the do-not-use list. Now "check which state it reaches".
- `tabledriven/state_machine.py`: `def handle(self, event: Any)` is now `def handle(self, event: object)`, and the `from typing import Any` import is gone. The engine only calls `type(event)` and passes the event on to `Callable[...]` values, so nothing needed `Any`; `vending_view.py`'s `send(event: object)` already typed the same value as `object`, so the two listings now agree. Verified: `ty check` clean, `ruff` clean, the five tests pass, and the demo output is byte-identical, so no `#:` markers change.
