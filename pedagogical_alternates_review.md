# Pedagogical Alternates Review

**Status (2026-08-09):** everything below is applied.
The five removals landed first,
item 5 via its rebuild-small option
(chapter 17's reference to the removed metaclass listing was inlined as part of item 3).
The two trims followed:
item 6 cut `strategy_pattern.py` to a paragraph
(keeping the Context's when-useful note and fixing the Solutions reference),
and item 7 cut `adapter_variations.py` to approaches 2 and 3,
with a parenthetical noting GoF's inner-class fourth placement.

A survey of Part III (chapters 21-39) for sections that present an
alternate approach for teaching purposes:
the classic GoF form shown beside the Pythonic one,
or a deliberately inferior design shown to be replaced.
Each was judged on two questions.
Does it teach something valuable enough?
Would anybody use it in real code?
A section survives if either answer is yes.
Most survive; the proposals below are the ones that fail both tests,
or that repeat a lesson a neighboring section teaches better.

Verdicts: **Remove**, **Trim** (shrink to prose or fold into a neighbor),
**Keep** (listed so the survey is visibly complete).

## Proposed Removals

### 1. Remove: 24_Singleton, "Eager Creation" (`singleton_eager.py`)

A near-duplicate of the Lazy Creation listing directly above it:
the same nested private class, the same `__getattr__()` delegation,
differing in one line (where the inner instance is created).
Nobody would use either form, and the chapter says so,
but the lazy version at least carries the mangling and delegation lessons.
This one adds two small points:
the lazy/eager trade-off,
which the cached-factory section covered when it introduced priming at import,
and the fact that the bare `__OnlyOne()` works in the class body
while the qualified `OnlyOne.__OnlyOne()` does not.
Both fit in a paragraph appended to Lazy Creation.

Entanglements:
exercise 1 ("modify it to use lazy initialization") and its entry in
`Solutions/24_Singleton.md` build on this listing;
the exercise would invert (start from `singleton_pattern.py`, make it eager)
or go.

### 2. Remove: 24_Singleton, "Overriding `__new__`" (`singleton_with_new.py`)

This variant has `__new__()` return the nested *foreign* object,
so `OnlyOne()` hands back something that is not an `OnlyOne`:
`isinstance()` fails and `__init__()` is skipped.
Nobody would use a constructor that constructs a different class,
and the section that follows, "One Instance in a Class Variable,"
is the sane `__new__()` form the chapter endorses in
"Which Should You Use?".
The one lesson here, that what `__new__()` returns decides whether
`__init__()` runs, is restated in both the class-variable section and the
metaclass section, so it does not need a third telling.
Three variations on the nested-private-class design is two too many.

Entanglements:
`singleton_class_variable.py`'s prose contrasts against this listing by name,
and the metaclass section links to the `#overriding-__new__` anchor;
both contrasts would re-anchor to the class-variable section,
where the same rule can be stated against `object.__new__(cls)`.

### 3. Remove: 24_Singleton, "Singleton Using Metaclasses" (`singleton_metaclass.py`)

The chapter's own framing is the tell: "This version is here for completeness."
[Metaprogramming](Chapters/17_Metaprogramming.md) shows a metaclass singleton
via `__call__()`, and this section opens by saying so.
Its unique content is the contrast
(replacing `__new__()` makes `__init__()` rerun, so the last call's
arguments win, where the `__call__()` version keeps the first call's),
plus the `klass: Any` escape hatch,
which repeats the Any-in-metaprogramming lesson chapter 17 owns.
The contrast is worth keeping as two or three sentences pointing at
chapter 17, without the 35-line listing.
"Which Should You Use?" says the decorator and metaclass versions are more
machinery than the problem justifies; the decorator section earns its
place anyway (see Keep list), and this one does not.

### 4. Remove: 27_Factory, "Preventing Direct Creation" (`nested_shape_factory.py`)

Fifty lines demonstrating that nesting the shape classes inside `factory()`
hides them, followed by the demonstration that it is broken:
each call defines fresh classes, so `type(a) is type(b)` fails,
`isinstance()` across calls fails, and `Shape.__subclasses__()` is useless.
The section concludes that the practical answer is module-level classes with
a leading underscore, which needs no listing.
Nobody would use the nested form, and its teaching is duplicated:
chapter 24's "Nothing Keeps the Class Private" walks the same ground
(nesting a class for privacy looks airtight and is not),
including the same `type()` recovery.
The class-statements-execute-per-call fact is worth one sentence on
`shape_factory1.py`.

### 5. Remove or rebuild: 27_Factory, "Polymorphic Factories" (`shape_factory2.py`)

The largest and most tangled candidate.
Seventy lines of GoF Factory Method:
a nested `Factory` class in every shape,
dispatched through `eval(f"{kind}.Factory()")`.
The chapter's own verdict is that neither piece is needed and the `eval()`
is "worse than unnecessary" (an injection hazard).
Nobody should use it, and the section says so at length.
What it teaches:
GoF's actual Factory Method intent (subclassable factories),
which GoF gives no example for,
and the eval-injection lesson that exercise 8 turns into a demonstration
and a fix.
Presenting a dangerous form as the primary listing and then disclaiming it
is the weight-not-pulled shape this review exists to catch.

Two options, in preference order:

- **Rebuild small**: keep the section, but make the listing the
  dictionary-of-`Factory`-objects version that exercise 8 currently asks the
  reader to produce, with a sentence noting the original used `eval()` and
  why that is an injection hazard.
  The GoF-intent teaching survives, the unsafe code stops being the
  presented artifact, and the section shrinks by half.
- **Remove**: fold the "GoF meant subclassable factories; in Python a
  factory object is worth writing when creation takes real work" paragraph
  into the section end that says this now, and drop the listing.

Entanglements, which make Rebuild the cheaper move:
exercises 2, 4, and 8 use `shape_factory2.py`
(8 exists to expose the `eval()`), with matching entries in
`Solutions/27_Factory.md`;
the Pattern Catalog's Factory Method row was deliberately retargeted to
`27_Factory.md#polymorphic-factories` in a prior deep review,
so removal means retargeting that row (probably to the dictionary factory)
and revisiting that decision;
"Which Should You Use?" names "the nested-`Factory`-class dispatcher."

## Proposed Trims

### 6. Trim: 28_Function_Objects, one of the two classic-form listings

The chapter shows Command as a function then as classes
(`command_pattern.py`),
and Strategy as a function then as classes (`strategy_pattern.py`).
Both classic forms exist to make the same point,
which the chapter states after each
("four classes and a wrapper to say what one list of functions says
directly"; "Five classes produce the same three lines")
and then generalizes in "Choosing the Lightest Callable."
One contrast carries the lesson; the second is a rerun.
Proposal: keep `command_pattern.py`
(shorter, first, and its when-to-use note about `undo()` threads through
the rest of the chapter)
and cut `strategy_pattern.py` to a sentence:
the classic form wraps each algorithm in a class and adds a Context,
and the Context earns its keep when something must hold the current
algorithm between calls.
Entanglement: `Solutions/28_Function_Objects.md` references
`strategy_pattern.py` in one solution's prose, a one-line fix.

Counterargument for keeping both:
the chapter's opening announces the twice-shown structure as a design,
and each classic form is under 60 lines.
This one is a judgment call; the removals above are not.

### 7. Trim: 29_Changing_the_Interface, `adapter_variations.py`

Four placements of the same adaptation, output "deliberately monotonous,"
introduced as what they are: "The four variations above are Java habits."
Approach 3 (the class adapter) pulls weight,
because the object-adapter/class-adapter split is GoF vocabulary a reader
meets elsewhere, and composition-versus-inheritance is a live choice.
Approaches 2 and 4 (adapter built into `op()`, inner-class adapter) are
Java translations nobody would write in Python.
The listing's best content is incidental to the variations:
the positional-only `/` override lesson and the honest-`Any`
Liskov-narrowing discussion, both attached to approach 2.
Proposal: cut to approaches 2 and 3
(2 carries the type lessons, 3 carries the class-adapter family),
dropping approach 4, whose inner-class packaging teaches nothing the
others do not.
If the type lessons can move onto another listing, cut to approach 3 alone.

## Reviewed and Kept

Sections that met the same description
(alternate approach shown for teaching)
and survived, with the reason:

| Chapter | Section / listing | Why it stays |
|---|---|---|
| 22 | Hand-rolled `Messenger` | Self-aware ("worth writing only to show how `SimpleNamespace` works underneath"); 15 lines that set up the chapter's typing thread. |
| 23 | `flatten_loop` beside `flatten` | Teaches `yield from` by direct substitution; the loop form is what readers write first. |
| 23 | "The Pattern That Disappeared" (`gof_iterator.py`, `asking_costs.py`) | Nobody would use it, but it is the chapter's capstone: honoring `first()`/`current_item()` over a stream rebuilds the list, which explains why Python dropped them. Ties together `tee`, buffering, and PEP 479. |
| 24 | "Lazy Creation" (`singleton_pattern.py`) | The one GoF translation worth keeping: carries the name-mangling and `__getattr__()` delegation lessons the removed variants lean on. |
| 24 | Borg | Named in the literature (the catalog's Monostate row links here); teaches `__dict__` sharing and the dataclass-breaks-Borg trap. |
| 24 | Class-decorator singleton | People write `@singleton` decorators in the wild; showing that `isinstance()` and subclassing break, with the metaclass error naming a class not on the failing line, is a practical warning. |
| 25 | `template_function.py` | Not a strawman: the function form is the recommended shape for stateless steps, and it closes the `@final` gap. |
| 26 | `proxy_1.py` explicit forwarding | Endorsed later as "the version a checker can see through"; the ABC/Protocol/`__getattr__()` progression is the chapter. |
| 27 | `shape_factory1.py` | The match-based factory function is real code people write; narrative setup for the dictionary. |
| 27 | `games.py` inheritance Abstract Factory | The `raise NotImplementedError` versus `@abstractmethod` versus Protocol failure-time comparison is concrete, and inheritance-based factories are common in the wild. |
| 27 | `pizza_builder.py` | Fluent builders are everywhere in Python libraries; the contrast with keyword arguments, and the survival cases (`GameBuilder`, `argparse`), give real guidance. |
| 28 | `command.py` / `command_pattern.py` pair | At least one classic contrast belongs here (see Trim 6). |
| 29 | `facade.py` static-method Facade | 15 lines; Java transplants write this, and exercise 3 converts it to the module facade. |
| 30 | `classic_observer.py` | Mirrors `java.util.Observer`; the "four things are gone" enumeration in the Pythonic section depends on it. |
| 31 | Both mousetrap designs | Not pedagogical-only: "Which Design Should You Use?" treats each as a real choice. |
| 32 | `paper_scissors_rock.py` double dispatch | The chapter's subject, with genuine keep-when guidance (state-reading combinations, subclass overrides). |
| 33 | `flower_visitors.py` classic Visitor | Kept deliberately ("seeing the price is part of the point"); the `Any` cost is the argument for `singledispatch`. |
| 34 | `filesystem_classic.py` | Carries the open-set/closed-set guidance: the classic form is the right one when plugins add node types. |
| 36 | Classic Memento (`sketch.py`) | The chapter narrows rather than dismisses it: large states and state you do not own still need it. |
| 37 | `recycle_rtti.py` / `plastic_dropped.py` | The wrong first cut is the chapter's structure; `plastic_dropped.py` makes "silently drop trash on the floor" a number you can see. |

## Mechanics of Applying a Removal

For each accepted removal:
delete the section and listing from the chapter,
rework or delete the entangled exercises and their `Solutions/` entries,
re-anchor the cross-references named above,
run `make sync` and `make prune-examples`
(the extracted files under `Examples/` become orphans),
and finish with `make verify`.
The Pattern Catalog retarget (item 5) also needs the heading-links gate
to pass, which `make verify` covers.
