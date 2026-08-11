[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/27_Factory.md` in the
clean-slate sweep. The mechanical layer is sound: every `#:` marker
validates (the seeded `random` sequences are deterministic), `ty`,
ruff, and the 8 tests are clean on `build/examples/27_Factory`, and all
ten scripts run. The cross-chapter claims hold: chapter 21's taxonomy
says this chapter covers *Factory Method*, *Abstract Factory*,
*Prototype*, and *Builder* and "builds both" dictionary-factory forms,
and it does (the hand-filled `SHAPES` table and the
`__init_subclass__()` registry); `Solutions/27_Factory.md` covers all
eight exercises; the `_images/abstract_factory` reference follows the
house extension-less convention; every anchor link resolves under the
gate. One factual error surfaced, in the Polymorphic Factories section:
"*GoF Design Patterns* provides no example of this" is wrong. The GoF
book's Factory Method sample code is the `MazeGame` with
`BombedMazeGame` and `EnchantedMazeGame` subclasses overriding the
factory methods; the accurate observation is that it reuses the maze
example from *Abstract Factory* rather than supplying a new one.
The registry addition below was probe-verified before writing: a
grandchild class registers through `__init_subclass__()` while
`Shape.__subclasses__()` lists only direct subclasses. No live blocks
this run: every finding had one defensible answer.

## Applied directly

- Polymorphic Factories: "provides no example of this, instead
  repeating the example used for the *Abstract Factory* (the next
  section shows this)" is now "For its sample code, *GoF Design
  Patterns* reuses the maze example from the *Abstract Factory* (the
  next section covers that pattern), subclassing the game to override
  its factory methods." GoF does give an example; the reuse is the
  point. The rewrite also resolves the ambiguous "(the next section
  shows this)".
- Registry section: added "`Shape.__subclasses__()` could have built
  the table instead, but it stops at direct subclasses;
  `__init_subclass__()` runs for every class anywhere below `Shape`."
  The chapter teaches `__subclasses__()` three pages earlier, so a
  reader would plausibly build the registry from it; probe-verified
  both halves.
- Abstract Factories intro: "you decide how the program will use every
  object that factory creates" is now "you choose the concrete version
  of every object that factory will create". Choosing the factory
  fixes what gets created, not how the program uses it, and "version"
  matches the GUI sentence that follows.
- Builder opening: "The last creational pattern in *GoF Design
  Patterns* this chapter has not covered is *Builder*" was a
  garden-path sentence; now "*Builder* is the last of the *GoF Design
  Patterns* creational patterns left to cover".
- "(which polymorphism takes care of)" is now "(which polymorphism
  handles)" (stranded preposition).
- "The effect is the same. Adding a new type can cause problems."
  merged with a colon: two clipped fragments whose halves are one
  claim.
- "an argument that allows it to determine what type of `Shape` to
  create" is now "an argument that selects the type of `Shape` to
  create".
- Underscore-names sentence: "discouraged by convention rather than
  hidden" is now "a convention rather than concealment", removing the
  "To discourage ... discouraged" echo.
- "Key on a qualified name if that can happen" is now "when a
  collision is possible" (watch-list "happen").
- "The steps must happen in an order" is now "must come in an order"
  (same).
- "the setup and play is simple" is now "are simple": the sentence
  goes on to call them "those activities".
- "slider, etc. it will automatically create" gained the comma after
  "etc.".
- Ran `make reflow CH=27` over the edited prose.

## Considered and declined

- `shape_name_gen()` calls `Shape.__subclasses__()` inside the loop in
  `shape_factory1.py` but hoists it in `shape_factory2.py`. Both are
  correct, the variation is harmless, and aligning them would churn a
  listing for no teaching gain.
- "Which Factory Should You Use?" keeps its question form: the heading
  rule bars "You Can/Must" clauses, not questions, and chapter 24's
  "Which Should You Use?" is the precedent.
- `PizzaBuilder` keeps its hand-written `__init__`: the prose frames
  the listing as a direct translation of the Java workaround, so the
  deviation from dataclass style is explained.
- `games.py` keeps its `raise NotImplementedError` base classes: the
  paragraph after the listing exists to critique them, and converting
  to `@abstractmethod` would delete the teaching contrast that
  motivates `games2.py`.
- The top-level-demo vs `__main__`-guard split (`shape_table.py`,
  `games*.py`, `prototype.py` top-level; `registry.py`,
  `prototype_registry.py`, `pizza_*.py` guarded) tracks which modules
  the tests import, so it is consistent, not drift.
- The opening paragraph's "... or so it seems" ellipsis and legacy
  cadence stay as authorial voice.
