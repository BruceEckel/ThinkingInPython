> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 29_Patterns--Changing_the_Interface (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the chapters it links (6, 8, 14, 18, 20, 21, 24, 26, 27),
the GoF text for *Adapter*, *Façade*, and *Proxy*, runtime probes on the pinned 3.15,
and `ty` 0.0.84 and Pyright 1.1.414 probes.
The mypy statements rest on mypy's issue tracker (issues 8314 and 17606), since mypy is not installed here.
`tip verify-ch CH=29` passes 24 of 24.

## Applied directly

Chapter, corrections:

- "Adapter in Python", the recursion-trap paragraph: it said copying or pickling `Adapter` recurses.
  `Adapter` is a record, and a frozen, slotted data class defines `__getstate__()` and `__setstate__()`,
  so `copy.copy()`, `copy.deepcopy()`, and a pickle round trip all work (probed).
  The trap belongs to an adapter with a hand-written `__init__()`, which the same probe confirms.
  The paragraph now says both, and `test_adapter.py` gained a test that pins the copy and the pickle.
- "Façade": "the 'static factory method' GoF pairs with *Façade*" credited GoF with a phrase its *Façade* chapter does not contain.
  GoF says a *Façade* is usually one object (so often a *Singleton*) and that *Abstract Factory* can create the subsystem's objects.
  The opening now states those two facts as the basis for "a *Singleton* *Abstract Factory*",
  and the sentence after the listing describes what `start_car()` does without the attribution.
- "Three Places for the Adaptation": "*GoF Design Patterns* splits the three approaches into two families" left Approach 2 in neither.
  Now "names two families of adapter", with a sentence placing Approach 2 (it uses the object adapter inside `op()`).
- The same section called Approach 3 "the adaptee's own class". `WhatIHave2` is a subclass of the adaptee,
  which matters because the section's premise is that you cannot change the adaptee. Approach 2 was "the call site"; it is the method that needs the interface.
- The pluggable-adapter parenthetical described one of GoF's three implementations (the delegate) as the definition.
  It now gives GoF's definition, a class with the adaptation built in, as two sentences after the class-adapter paragraph.
- "What an Override May Change": "`ty` rejects a renamed keyword-capable parameter" holds for Pyright too (probed),
  and the unnamed "checker that accepts such a rename" is mypy. Both are now named.
- Two links to *Surrogate* pointed at `#proxy` for claims that live in its subsection `#what-the-implementation-supplies`
  (the ABC and `Protocol` comparison, and the looser definition of *Proxy*). Retargeted.

Chapter, teaching:

- "Adapter in Python" told the reader to name the target with a `Protocol` and showed no code.
  New listing `protocol_adapter.py`: `WhatIWant` as a `Protocol`, an `ObjectAdapter` record with no base, and the near-miss `use(WhatIHave())` that `ty` rejects.
- "Façade": "`Ignition` needs `FuelPump`, and `FuelPump` needs `Engine`, in that order, or the call sequence is wrong"
  did not say which order or what goes wrong. Now: each constructor takes the object its method calls, so the caller builds from the inside out.
- Exercise 1 now asks for `len(adapter)`, which cashes in the "(see exercise 1)" pointer on the special-methods sentence.
- Exercise 5 is new: remove the `/`, keep the renamed override, and see the `ty` error and the runtime `TypeError`.
  "What an Override May Change" had no exercise.

Chapter, prose:

- "An adapter sits between them and fixes the problem" now says what the adapter does.
- Emphasis italics removed from "*where*" and "*module*" (neither introduces a term).
- "The approaches differ only in where the adaptation lives. When the output is the same for every approach, only packaging separates them" said one thing twice. One sentence remains.
- "callers cannot use a positional-only parameter name" is now "no caller can pass a positional-only parameter by name".
- "*Façade* has a failure mode too": nothing before it had one. "too" removed.
- "An interface that replaces one you own has a second half" is now "Replacing an interface you own takes two steps, and writing the new interface is the first."

Solutions:

- Exercise 1: `PairsAdapter` hand-wrote `__init__()` and carried a parenthesized docstring,
  while the exercise says to follow `getattr_adapter.py`, which is a record. It is now a `@record` with no docstring.
  The listing also shows `len(adapter)` raising a `TypeError`, with a paragraph explaining the special-method lookup.
- Exercise 2: "runs without a word" is now "runs without a warning".
- Exercise 5: new solution, `exercise_5.py`, with the quoted `ty` diagnostic.

Other files:

- `tools/data/exercise_refs_baseline.txt`: one entry added for the new "(see exercise 5)" reference.

## Considered and declined

- **A real-world adapter in place of `WhatIHave`/`WhatIWant`.** The abstract names keep the three approaches comparable,
  and chapter 20's `PairCoord` is the concrete case the chapter links.
- **Moving "What an Override May Change" out of the *Adapter* section.** It is a digression on overriding,
  but Approach 2 is what raises the question, and chapter 20's substitutability section is linked.
- **Adding the `__getattr__()` guard to `getattr_adapter.py`.** The record does not need it for copying or pickling,
  and chapter 26 owns the guard.
- **An exercise on a deprecated `@overload`.** The paragraph is a pointer to a static-only feature; exercise 2 covers the runtime half.
- **`Facade` with `@staticmethod` as non-idiomatic.** The chapter presents it as the GoF form and replaces it with a module two paragraphs later.
- **A conclusion section.** "Deprecating the Old Interface" ends on a paragraph that ties both patterns to the deprecation step.
- **"never", "only", and "already" in existing sentences** ("never learns how those classes are built", "An adapter's only job").
  Each was reread; the sentences read clearly and are left as written.
