> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 27_Patterns--Factory (2026-10-13)

This review has no live blocks.
I checked the chapter and its Solutions file against every listing,
against the chapters that link here (6, 12, 14, 17, 21, 29, 32, 33, 37, 38, 39, 47; every inbound sentence holds),
and against `ty` 0.0.86, Pyright 1.1.414, and runtime probes on Python 3.15.0.
Probes confirmed the `Literal`, abstract-instantiation, function-attribute, generic-bound, `@make.register` bound, `isinstance-against-protocol`, `invalid-return-type`, and `Builder.__name__` diagnostics the prose quotes,
the three `deepcopy()` `TypeError` messages,
`-X lazy_imports=all`,
and that the chapter's seed draws a `Triangle` in four picks (Solutions 1 and 2).
`tip verify-ch CH=27 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after.

## Applied directly

Chapter, corrections:

- "Factory Objects": "Much of the time, however, a single static method in the base class ... is enough" recommended the form the chapter's closing calls a tradition Python does not need. Cut it; the case it introduced (a caller that keeps the factory) joins the next paragraph.
- "Factory Objects": "Use a separate factory class when object creation needs work beyond calling a constructor" disagreed with "Which Factory to Use", which says a factory function, and a class only when the work has state. The paragraph now names the state (a pool, a cache, loaded configuration) or a caller that keeps the factory.
- "Simple Factory Method": "`n` is the maximum number of shapes it can produce" described a generator that yields names, `n` of them. Now "produces `n` names on demand".
- "Explicit Registration with a Protocol": "The ABC in `registry.py` exists so that `__init_subclass__()` has a class" credited the ABC with what the base class does; the section above says `ABC` adds a guard. Now "needs a base class because Python calls the base class's `__init_subclass__()`".

Chapter, teaching:

- "The Pythonic Factory": added the near-miss of a table of instances (`{"Circle": Circle()}`), where every caller shares one object, with a link to *Prototype*, which keeps instances on purpose and copies them. The paragraph split at the seam between what the table holds and what adding a type takes.
- "Explicit Registration with a Protocol": the closing "Choose the failure you prefer" weighed only the incomplete class. It now names both sides: the ABC registers every subclass, the Protocol leaves registration to you.
- "Which Factory to Use": added a bullet for *Factory Method* proper (a creator that does work, subclasses picking the product, `shape_sketch.py`), the one form the chapter teaches that the list left out.

Chapter, prose:

- "no `@classmethod` needs a class on which to sit" now names the hazard it removes: no shape class carries a `make()` that `Circle.make("Square")` could misuse.
- "In this case, a closed `Literal` complicates things" now says it rules out a `Literal` and that `make()` takes a `str`.
- "Whereas a factory takes information ... a generator object does the opposite" split into two positive statements.
- "If object creation is spread throughout", "neither has been updated for": active forms.
- "To add a `Triangle` is a single class definition": "Adding a `Triangle` takes".
- "The builder is quietly single-use" now says what happens: a `PizzaBuilder` keeps its settings after `build()`. "the single-use hazard" became "that hazard".
- Cut "genuinely", "genuine", "real work", and "touches only a single place".

Solutions:

- Exercise 4: `Circle` and `Square` had hand-written `__init__()` methods that only stored `thickness`. They are records now, under a `Shape` with `__slots__ = ()`, per the record rulings.
- Exercise 7: heading "What `copy.copy()` costs a prototype registry" is now "breaks in" (commerce word; no exercise reference names it).
- Exercise 3: "a factory that omits it defines without complaint" is now "Python accepts the definition of a factory that omits it".

## Considered and declined

- Moving "Factory Objects" ahead of "The Pythonic Factory: a Dictionary". The section reads as a step back after the dictionary, but it sets up the factory objects that *Factory Method* and *Abstract Factory* use, and its prose already says Python does not need it.
- Quoting the `# ty:` comment in `shape_table.py` like the book's other `# ty: expected "X", found "Y":` comments. The found type is `Literal["Hexagon"]`, so quoting nests quotes.
- `exercise_6.py` prints `extra_shapes.Circle.__name__`, a line that mostly gives the import a use. Harmless, and the `noqa` discussion covers the import.
- Everything the 2026-09-29 review declined still holds and was not re-raised.

## For the session

- `tip verify-ch` regenerated `Solutions/27_Patterns--Factory/exercise_4.py` from the edited README; that generated file is in the diff and belongs in the commit.
- No cross-chapter errors found, and no new baseline hits.
