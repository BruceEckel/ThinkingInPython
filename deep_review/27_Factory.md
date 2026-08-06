[[Reviewed]]
# Deep review: 27_Factory.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Show the dictionary factory the section is named for

**Kind:** teaching
**Where:** section "The Pythonic Factory: a Dictionary" (line ~186)
**Problem:** The section says "the simplest factory is a dictionary that maps names to classes. There is no factory method and no factory class; the `dict` is the factory," then shows no such dictionary. The only listing is the `__init_subclass__()` self-registering version, which the prose introduces as going "one step further." The reader is asked to accept the first step on faith and meets the section's headline idea only in a listing that also teaches a dunder hook. This is the section chapters 37 and 38 link to for "the registry idea," and it opens at full complexity, which inverts the escalating-difficulty order.

**Proposal:** Add a small listing between "the `dict` is the factory" and "You can go one step further," so the section shows the table before it shows the automation. Verified to run and to fit the 70-column limit:

```python
# shape_table.py
from typing import Final, override

class Shape:
    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

SHAPES: Final[dict[str, type[Shape]]] = {
    "Circle": Circle,
    "Square": Square,
}

def make(kind: str) -> Shape:
    return SHAPES[kind]()

make("Circle").draw()
#: Circle.draw
make("Square").draw()
#: Square.draw
```

with a connecting sentence such as: "The `dict` values are classes, so `type[Shape]` is their type, and calling one constructs an instance. Adding a `Triangle` means one new class and one new line in `SHAPES`." Then the existing "You can go one step further, so the factory never needs editing when you add a type" reads as the removal of that second line.

Alternatives, if a second listing is too much: show the dictionary literal inline in the prose without making it an extractable example, or fold it into the paragraph as a two-line snippet inside `registry.py`'s introduction.

**Cost:** New extractable example (`27_Factory/shape_table.py`), so the usual sync/gate loop. `make` is defined in both `shape_table.py` and `registry.py`; that is fine because no test imports both, but keep the names parallel deliberately, since the parallel is what makes the "one step further" contrast land. No cross-reference names this section's listings, only its heading, which does not change.

---

## 2. Close the chapter with a "Which Factory Should You Use?" section

**Kind:** structure
**Where:** after "Builder", before "Exercises" (line ~795)
**Problem:** The chapter teaches six creational forms: static factory method, nested-class factory, dictionary/registry, polymorphic factory objects, Abstract Factory, Prototype, and Builder. Each section says something about when its form is worth it, but those judgments are scattered across seven sections and a reader finishing the chapter has no single place that ranks them. Neighbors solve this: chapter 24 ends with "Which Should You Use?" and chapter 29 with "Telling the Wrappers Apart." Chapter 27, which covers more distinct patterns than either, ends mid-topic on Builder.

**Proposal:** Add a closing section modeled on chapter 24's, roughly:

> ## Which Factory Should You Use?
>
> Match the machinery to what varies:
>
> - A name maps to a class: use a dictionary. Add `__init_subclass__()` registration once the set of classes is open, or spread across modules.
> - Construction takes real work beyond calling a constructor (pooling, caching, consulting configuration): write a factory function, and a factory class only when that work has state of its own.
> - Several products must be chosen together as a matched set: use Abstract Factory, expressed as a `Protocol` rather than a base class.
> - The interesting part of an object is its configured state rather than its type: keep a prototype and copy it. For a frozen data class, `replace()` is that copy.
> - Construction is a genuine process with ordered steps and rules spanning them: use Builder. When the "steps" are optional values, keyword arguments are the builder.
>
> The static `factory()` method and the nested-`Factory`-class dispatcher are here because *GoF Design Patterns* describes them, not because Python needs them. Both exist to work around languages where a class is not an object you can put in a dictionary.

**Cost:** New `##` heading, so a new anchor (`#which-factory-should-you-use`). Nothing links to it yet. Existing incoming links point at `#builder`, `#prototype`, `#abstract-factories`, and `#the-pythonic-factory-a-dictionary`, all unchanged. The section restates judgments already made in each section, so if it goes in, consider trimming the closing sentence of the Polymorphic Factories section ("much of the time you don't need the complexity ...") to avoid saying it twice.

---

## 3. Say that `shape_factory2.py`'s `eval()` is a code-execution hole, not just unnecessary

**Kind:** teaching
**Where:** section "Polymorphic Factories", the paragraph beginning "This version leans on `eval()`" (line ~371)
**Problem:** The chapter's only criticism of `eval(f"{kind}.Factory()")` is that Python does not need it. That undersells it. `create_shape()` compiles and runs whatever string it is handed, so any `kind` reaching it from outside the program is arbitrary code. Verified against the built example: `ShapeFactory.create_shape("(print('arbitrary code ran'), Circle)[1]")` prints the message and returns a `Circle`. The book takes an explicit stance against `eval()` on untrusted input elsewhere, and this is the listing where a reader would copy the idiom.

**Proposal:** Replace the paragraph with:

> This version leans on `eval()` and a `Factory` class nested in every shape,
> neither of which Python needs.
> The `eval()` is worse than unnecessary.
> `create_shape()` compiles and runs whatever string it receives,
> so a `kind` arriving from a configuration file, a request, or a command line is arbitrary code rather than a shape name.
> The registry shown above does the same job with a dictionary lookup,
> which either produces a class or raises a `KeyError`.
> Prefer that.
> A separate factory class is worth writing when object creation takes real work beyond calling a constructor,
> such as pooling, caching, or consulting external configuration.

This also removes the "Because classes are already first-class objects" clause, whose "already" is a watch-list word and whose point is made two sections earlier.

**Cost:** None. The listing stays as it is, so the `#:` markers are untouched.

---

## 4. Make `games.py`'s two base classes refuse the same way

**Kind:** code
**Where:** `games.py`, `Obstacle` and `Character` (lines ~404-409)
**Problem:** `Obstacle.action()` raises `NotImplementedError`; `Character.interact_with()` has a `...` body and silently returns `None`. The prose four pages later is specifically about what `raise NotImplementedError` does and does not enforce, and a reader who looks back at the listing finds only one of the two bases doing it. The `...` form is strictly worse than the one the prose criticizes: a concrete character that forgets `interact_with()` produces no failure at any point, not even at call time.

**Proposal:** Change `Character.interact_with()`'s body to `raise NotImplementedError`, matching `Obstacle`:

```python
class Character:
    def interact_with(self, obstacle: Obstacle) -> None:
        raise NotImplementedError
```

The existing paragraph about call-time versus instantiation-time failure then covers both bases without further change. `GameElementFactory` already uses `raise NotImplementedError` for both of its methods, so all three bases become consistent.

Alternative: leave the code and add a clause to the prose noting that `Character`'s `...` body fails even later, at no point at all. That teaches the third failure mode but makes the listing carry an inconsistency the prose has to explain away.

**Cost:** Output is unchanged, so no `#:` markers move. `games2.py`'s Protocol version deliberately uses `...` bodies (that is what a Protocol body is) and must not be changed to match.

---

## 5. `ShapeFactory.add_factory()` is dead code, and `dict[str, Any]` gives the section's contrast away

**Kind:** code
**Where:** `shape_factory2.py`, `ShapeFactory` (lines ~299-311)
**Problem:** Two things in this listing are never explained. `add_factory()` is never called, in the chapter, in the solutions, or anywhere in `Examples/`, so it is a method a reader has to decide is important and then discover is not. And `factories: ClassVar[dict[str, Any]]` uses `Any` with no stated reason in a chapter that shows a precisely typed `dict[str, type[Shape]]` two sections earlier; the reader sees the loose typing without being told it is a symptom of the design rather than a house-style lapse.

**Proposal:** Delete `add_factory()`, and give the nested factories a `Protocol` so the dispatcher's dictionary carries a real type:

```python
class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class ShapeFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {}

    # Build and cache each kind's factory on first request:
    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        if kind not in cls.factories:
            cls.factories[kind] = eval(f"{kind}.Factory()")
        return cls.factories[kind].create()
```

The nested `Circle.Factory` and `Square.Factory` satisfy `ShapeMaker` structurally, with no change to them. This tightens the comparison the section is drawing: even at its most precise, the polymorphic version needs a Protocol, a nested class per shape, and an `eval()` to do what one dictionary does.

Alternatives: keep `add_factory()` and add a sentence saying it is the hook for a shape whose factory cannot be constructed by name (which is the only reading that makes it earn its place); or keep `Any` and say in prose that the heterogeneous store is what forces it.

**Cost:** `eval()` returns `Any`, so assigning it into a `dict[str, ShapeMaker]` still type-checks; confirm with `ty` after the change. Output is unchanged. Exercise 2 ("Add a class `Triangle` to `shape_factory2.py`") and its solution add a nested `Factory` with `create() -> Triangle`, which satisfies `ShapeMaker` without edits, but `Solutions/27_Factory.md` should be re-run.

---

## 6. Show the Protocol check biting in `games2.py`

**Kind:** teaching
**Where:** section "Abstract Factories", after `games2.py` (line ~548)
**Problem:** The paragraph claims "the type checker still verifies that each one fits the appropriate `Protocol`," and the listing gives the reader no way to see it. Every class in `games2.py` conforms, so the output is identical to `games.py`'s and nothing distinguishes the structural version from a version with no typing at all. This is also where the section's argument is decided: the reader is being asked to give up a base class in exchange for a check they have not seen fire.

**Proposal:** Add a commented near-miss at the end of `games2.py`, following the pattern already used in `nested_shape_factory.py` (`# Circle()  # Not defined outside factory()`):

```python
class BrokenFactory:
    def make_character(self) -> Kitty: return Kitty()

# GameEnvironment(BrokenFactory())  # ty: invalid-argument-type
```

and one sentence of prose naming what the checker says. Verified against `ty` 0.0.56 in this repo, uncommented:

```
error[invalid-argument-type]: Argument to `GameEnvironment.__init__` is incorrect
info: type `BrokenFactory` is not assignable to protocol `GameElementFactory`
info: └── protocol member `make_obstacle` is not defined on type `BrokenFactory`
```

The teaching point sharpens the paragraph two above it about `@abstractmethod` versus `raise NotImplementedError`: the Protocol catches the omission earlier than either, before the program runs at all.

**Cost:** Adds a class to `games2.py` with no runtime effect, so no `#:` markers move. The commented-out call must stay commented or the chapter's own `ty` gate fails. Quoting a `ty` diagnostic in prose ties the chapter to the checker's current message; keep the quote to the `info:` line about the missing protocol member, which is the stable part.

---

## 7. Show the shallow copy the Prototype prose describes

**Kind:** teaching
**Where:** section "Prototype", after `prototype.py` (line ~595)
**Problem:** "A shallow copy shares that list, and editing one monster corrupts the other" is the sentence that justifies `deepcopy()` over `copy()`, and it is asserted rather than shown. `copy.copy()` and `copy.deepcopy()` are the chapter's clearest lookalike pair, one character apart in effect and a word apart in the source, and a reader who writes the wrong one gets a bug with no error.

**Proposal:** Extend `prototype.py` with the failing form at the end, after the two existing prints:

```python
shallow = copy.copy(goblin)
shallow.powers.append("shared")
print(goblin.powers)  # The original changed too
#: ['bite', 'shared']
```

Verified: `copy.copy()` on this dataclass leaves `goblin.powers is shallow.powers` `True`. Placing it last keeps the existing two markers untouched.

Alternatives: put it in its own listing (`shallow_trap.py`) so `prototype.py` stays a clean success story; or leave the code and add a sentence naming which objects `deepcopy()` cannot clone (open files, locks, sockets) and pointing at `__deepcopy__` for control, which covers a different gap in the same paragraph.

**Cost:** The demo ends on a failure rather than the success, so the prose after it must say the last two lines are the trap, not the recommendation.

---

## 8. `GameEnvironment` stores a field it never reads and names two others `p` and `ob`

**Kind:** code
**Where:** `games.py` (line ~451) and `games2.py` (line ~532)
**Problem:** `self.factory = factory` is assigned in both versions and read in neither; the factory's whole job finishes inside `__init__`. `self.p` and `self.ob` are Java-translation abbreviations in a book that tells readers to use standard naming. Both listings are otherwise the cleanest statement of the pattern in the chapter, and `GameEnvironment` is the class the reader is meant to notice never names a concrete type.

**Proposal:** In both files:

```python
class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.character = factory.make_character()
        self.obstacle = factory.make_obstacle()
    def play(self) -> None:
        self.character.interact_with(self.obstacle)
```

Dropping `self.factory` also makes the point sharper: the factory is consumed at construction and nothing holds onto it.

**Cost:** Output is unchanged. `Solutions/27_Factory.md` reproduces `GameEnvironment` for exercise 3 and would need the same edit, and its closing prose mentions `GameEnvironment` by name. Exercise 4 does not touch this class.

---

## 9. The one-line Multiple Dispatching aside teaches nothing where it sits

**Kind:** prose
**Where:** section "Abstract Factories" (line ~477)
**Problem:** "This also contains examples of [Multiple Dispatching](32_Multiple_Dispatching.md)." sits alone between two paragraphs, names no line of the listing, and forwards to a chapter five ahead. A reader cannot tell what in `games.py` is being pointed at. The candidate is `Kitty.interact_with()` dispatching on `self` and then calling `obstacle.action()`, which is a second virtual call, but chapter 32's double dispatch is the tighter structure where the second call passes `self` back. Naming the pattern here without checking that structure is the overlabeling the house style warns about.

**Proposal:** Either name the mechanism, replacing the line with something like:

> `interact_with()` dispatches on the character's type, and `obstacle.action()` dispatches again on the obstacle's, so the pair of calls chooses behavior from both types.
> [Multiple Dispatching](32_Multiple_Dispatching.md) develops this into a technique.

or cut the line. The rewrite is worth more; the reader learns what to look for in the listing in front of them.

**Cost:** None. Chapter 32 does not link back to this sentence.

---

## 10. `nested_shape_factory.py` quietly abandons `__subclasses__()`

**Kind:** teaching
**Where:** section "Preventing Direct Creation" (line ~157)
**Problem:** `shape_factory1.py` picks a shape with `random.choice(Shape.__subclasses__())`; the nested version hardcodes `random.choice(["Circle", "Square"])` with no comment. That change is forced by the nesting, and it is a second, concrete price for the privacy the section buys. Verified: after two `factory()` calls, `Shape.__subclasses__()` holds four classes, growing with every call, because each call defines two more.

**Proposal:** Add a sentence to the existing "The privacy has a price" paragraph, after the `type(a) is type(b)` claim:

> `shape_gen()` also has to name the shapes as strings.
> `Shape.__subclasses__()` no longer identifies the two kinds:
> it grows by two entries on every `factory()` call, one per class the call defined.

**Cost:** None. The paragraph is already about the cost of nesting, so this extends the existing argument rather than opening a new one.

---

## 11. The Pythonic Factory section never links to the thesis it cashes in

**Kind:** prose
**Where:** section "The Pythonic Factory: a Dictionary" (line ~233)
**Problem:** Chapter 21 argues that classic patterns dissolve into Python, and chapter 23 closes its Pythonic section with "This is the dissolution described in [The Pattern Concept](21_The_Pattern_Concept.md)." Chapter 27's Pythonic section makes the same move without the connection, even though chapter 21 names factories specifically as the creational example the reader will meet later.

**Proposal:** After "and it is the most common form of factory in idiomatic Python," add a clause pointing back, matching chapter 23's phrasing:

> Creating objects through a dictionary of classes is the dissolution described in [The Pattern Concept](21_The_Pattern_Concept.md): the pattern does not go away, it stops needing a class hierarchy to express it.

**Cost:** None. Chapter 21 already links forward to chapter 27, so this closes the loop.

---

## 12. Mention `copy.replace()` alongside `dataclasses.replace()`

**Kind:** teaching
**Where:** section "Builder", the paragraph after `pizza_direct.py` (line ~744)
**Problem:** The chapter says "`dataclasses.replace()` covers the other use of builder chains" and that for a frozen data class it "is Prototype and Builder rolled into one function." Since 3.13 the same operation has a general form, `copy.replace()`, which works on anything defining `__replace__` rather than dataclasses alone. The chapter targets 3.15 and this is the one place where the generalization matters, because the Prototype section three pages earlier already used `copy` for the same purpose.

**Proposal:** Add a sentence after the `replace()` claim:

> `copy.replace()` is the general form of the same operation, working on any object that defines `__replace__()`; a data class gets that method for free.

Verified on the pinned 3.15 beta: `copy.replace(pizza, size=20)` returns `Pizza(size=20, cheese=True, toppings=(...))`.

**Cost:** None if it stays prose. Switching the listing to `copy.replace()` would change the import line and lose the connection to `dataclasses`, so keep the listing as it is.

---

## 13. Prototype has no exercise

**Kind:** exercise
**Where:** section "Exercises" (line ~797)
**Problem:** The six exercises cover the simple factory (1), the polymorphic factory (2), Abstract Factory (3, 4), Builder (5), and registry import timing (6). Prototype gets a full section, two listings, and a test file, and nothing to do. The exercises also cluster three-deep on the Abstract Factory, which is the section with the least Python-specific content.

**Proposal:** Add an exercise that exercises the deep-copy point rather than restating it:

> 7.  Give `Monster` in `prototype_registry.py` a `parts: dict[str, int]` field and add a prototype that uses it.
>     Change `spawn()` to use `copy.copy()` instead of `copy.deepcopy()`, run `test_prototype.py`, and explain which assertion fails and why.
>     Then restore `deepcopy()` and add a test that would have caught the bug through `parts` rather than `powers`.

Consider also retargeting exercise 4, which repeats exercise 3's pattern on a different hierarchy, toward `games2.py`'s Protocol form: "Add `GnomesAndFairies` to `games2.py` and omit `make_obstacle()`. What does `ty` report, and at which line?"

**Cost:** New solution needed in `Solutions/27_Factory.md`.

---

## 14. The generator-as-factory paragraph mixes up names and objects

**Kind:** prose
**Where:** section "Simple Factory Method" (lines ~90-94, ~118)
**Problem:** "A generator is a special case of a factory, because it takes no arguments to create a new object" sits directly under a listing whose generator yields strings, not shapes. `shape_name_gen()` produces the *input* to the factory, so on first reading the sentence says the generator is a factory for shapes when it is a source of names. "`next(gen)` produces the next object from the generator" a few lines later repeats "object" for what is a string. The claim about taking no arguments is also blurred by `shape_name_gen(n)`, which takes one: the argument goes to the generator function, and the generator object then produces values without further input.

**Proposal:** Rewrite the two passages so the distinction is explicit:

> I have also used a *generator* (see [Iterators](23_Iterators.md#generators)).
> A generator is a special case of a factory.
> A factory takes information telling it what to build;
> a generator object holds an internal algorithm and produces the next value with no argument at all.
> `shape_name_gen()` takes `n` and returns a generator object, and that object then produces names on demand.
> Those names are the data driving `Shape.factory()`.

and change "produces the next object from the generator" to "produces the next name from the generator."

**Cost:** None.

---

## 15. Small prose tics in the newer passages

**Kind:** prose
**Where:** lines ~237, ~359, ~641, ~474
**Problem:** Four spots use a watch-list word or a vague noun where the sentence would be clearer without it.

**Proposal:**

- Line ~237, "Know when the registration happens:" → "Know when the registration runs:" ("happens" is on the watch list, and "runs" is what the following sentence goes on to say).
- Line ~359, "The actual creation of shapes happens in `ShapeFactory.create_shape()`" → "`ShapeFactory.create_shape()` creates the shapes" (legacy prose; "actual" and "happens" both go, and the sentence gets a real subject).
- Line ~641, "These tests show that Prototypes are safe." → "These tests pin down the two properties a prototype registry has to have:" ("safe" names no property, and the next sentence lists the two).
- Line ~474, "Here, `GameEnvironment` does not anticipate inheritance, although it might make sense to do that." → cut, or say what it would mean: "`GameEnvironment` is not designed to be subclassed, though a real game would probably subclass it to vary the rules of play." As it stands the sentence names a design choice without saying what the alternative would look like.

**Cost:** None.

---

## Already fixed directly (no decision needed)

- line ~281: "The static `factory()` method in the previous example" named the wrong listing. The previous example is now `registry.py`/`test_registry.py`, because the Pythonic Factory section was inserted between the simple factory and this one. Changed to "in `shape_factory1.py`".
- line ~801: exercise 3 asked for "a new type of `GameEnvironment` called `GnomesAndFairies`". `GnomesAndFairies` is a concrete factory, not an environment, and `Solutions/27_Factory.md` implements it as `class GnomesAndFairies(GameElementFactory)`. Changed to "a new type of `GameElementFactory`".

---

## Verification run before editing (all clean)

- `uv run ruff check build/examples/27_Factory` — passed.
- `(cd build/examples && uv run ty check 27_Factory)` — passed.
- `uv run pytest build/examples/27_Factory` — 8 passed.
- Every listing run directly; all `#:` markers match stdout, including the two seeded-`random` sequences.
- `tools/heading_links.py` and `tools/banned_phrases.py` — clean. No em-dashes in the chapter.

## Cross-chapter thread check

- The import-time-registration and name-collision caveats in "The Pythonic Factory" still back chapter 37's `Trash.registry` (which links here as "this is a [Factory]") and chapter 38's maze registry (which links to `#the-pythonic-factory-a-dictionary`). Both ends hold; nothing to change at either.
- The accrued deep-review note lists chapter 20 as a consumer of this thread. Chapter 20 contains no registry and no `__init_subclass__` today, so that half of the note is stale. Nothing to fix in this chapter; the note itself is the thing that is out of date.
- Chapter 21's "patterns dissolve into the language" thesis names factories explicitly and links forward to this chapter. This chapter does not link back; see proposal 11.
