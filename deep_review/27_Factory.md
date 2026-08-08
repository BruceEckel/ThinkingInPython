When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Exercise 3 (line 900) sends the reader to the version the chapter argues
against.**

"Add a new type of `GameElementFactory` called `GnomesAndFairies` to
`games.py`." `games.py` is the `raise NotImplementedError` translation whose
weaknesses the chapter spends a paragraph on; `games2.py` is the form it
recommends. As written the exercise drills the discarded design, and it never
exercises the `Protocol`, which is the section's actual teaching.

Proposed change: ask for both, so the contrast is the exercise.

> 3.  Add a new type of `GameElementFactory` called `GnomesAndFairies`,
>     first to `games.py` and then to `games2.py`.
>     In `games2.py`, leave out `make_obstacle()` at first and confirm the
>     error your type checker reports; then add it.

That turns the near-miss in `BrokenFactory` into something the reader
performs rather than reads.

---

[] Reject

**"Simple Factory Method", lines 104-121: `explicit_generator.py` teaches
generators, not factories.**

The listing exists only to show `next(gen)` twice. Generators have their own
chapter ([Iterators](23_Iterators.md#generators)), which line 90 already
links. In a Factory chapter this is a second unfamiliar construct competing
with the first listing's actual subject, and it is the one place in the
chapter where a listing does not produce or discuss an object factory.
`gen = shape_name_gen(7)` asking for seven names and consuming two adds to
the impression that the number does not matter.

Proposed change: cut `explicit_generator.py` and the two sentences around it,
and keep the three-sentence generator explanation at lines 90-96 that earns
its place by explaining where `Shape.factory()`'s input comes from.

Cost of the cut: `Examples/27_Factory/explicit_generator.py` becomes orphaned
and needs `make prune-examples`. Nothing else in the book references it
(checked). No exercise depends on it.

Alternative, if the listing should stay: move it into the generator
explanation at line 96 so the section does not restart after the
`__subclasses__()` paragraph, and change `shape_name_gen(7)` to
`shape_name_gen(2)` so the count matches what is consumed.

---

[] Reject

**Exercises: nothing exercises the chapter's strongest safety claim.**

The `eval()` critique at lines 424-433 is the sharpest practical warning in
the chapter — a `kind` from a config file or a request is arbitrary code —
and no exercise touches it. Exercises 2 and 4 ask the reader to *extend*
`shape_factory2.py`, entrenching the `eval()` without questioning it.

Proposed addition, as a new exercise 8:

> 8.  In `shape_factory2.py`, call `ShapeFactory.create_shape()` with a
>     `kind` string that is not a shape name but a Python expression with a
>     side effect, and show that `create_shape()` runs it.
>     Then replace the `eval()` with a dictionary of the nested `Factory`
>     classes and show that the same string now raises `KeyError`.

Verified that the attack works as described on the pinned build: a `kind` of
`__import__('sys').stderr.write('pwned\n') or Circle` is evaluated before the
`.Factory()` attribute lookup fails.

---

[] Reject

**"Abstract Factories", lines 530-531: the sentence contradicts itself.**

> `GameEnvironment` is not designed to be subclassed,
> though a real game would probably subclass it to vary the rules of play.

A reader cannot act on this. Either the class is unsuitable for subclassing,
in which case a real game should not subclass it, or it is fine to subclass
and the first clause is wrong. (The Java original said "not designed to be
inherited from, although it could make sense to do that," which has the same
problem.)

Proposed change, stating the actual limitation:

> `GameEnvironment` has no hook for varying the rules of play, so a real game
> would need one, either a subclass overriding `play()` or a rules object
> passed alongside the factory.

Alternative, if the point is only that the listing is deliberately minimal:
drop the sentence. It is the only place in the section that discusses
`GameEnvironment`'s extensibility, and the section's subject is the factory,
not the environment.

---

[] Reject

**`registry.py` and `prototype_registry.py`: importable modules carrying
top-level demos, unlike the two pizza modules in the same chapter.**

`thinking-in-python-skill.md` says "Importable modules carry no top-level
demo." `pizza_builder.py` and `pizza_direct.py` follow it with
`if __name__ == "__main__":` guards, precisely because `test_pizza.py`
imports them. `registry.py` and `prototype_registry.py` are imported by
`test_registry.py` and `test_prototype.py` respectively and run their demos
at import, printing into every pytest session that touches them.

Proposed change: guard both demos the way the pizza listings do. In
`registry.py`, indent the `print(sorted(Shape.registry))` line and the
`for kind in ...` loop under `if __name__ == "__main__":`; in
`prototype_registry.py`, indent everything from `a = spawn("goblin")` down.
`validate_output.py` execs each block with `__name__` set to `"__main__"`
(confirmed in `tools/validate_output.py`, lines 165 and 244), so the `#:`
markers keep validating unchanged.

Reported rather than applied because it is a consistency decision across
four listings, and the unguarded form may be deliberate for readability in
a chapter where the registry contents are the lesson.

---

[] Reject

**"Simple Factory Method", lines 90-121: the chapter gives three different
answers to "what is the factory here?"**

Within thirty lines the reader gets:

- line 91: "A generator is a special case of a factory."
- lines 92-93: a factory and a generator are *contrasted* — "A factory takes
  information telling it what to build; a generator object holds an internal
  algorithm and produces the next value with no argument at all."
- line 121: "`shape_name_gen()` is the factory, and `gen` is the generator" —
  now the generator is the *product* of a factory, not a kind of factory.

Each sentence is defensible alone. Read in sequence they do not settle what
relationship the chapter is claiming, and this is a reader's first encounter
with the distinction in a chapter whose whole subject is factories.

Proposed change: pick the framing in lines 92-93 (they are the clearest) and
make the other two agree with it. Drop line 91 outright, and rewrite line 121
as "`shape_name_gen()` builds the generator; `gen` produces the names."
That leaves one claim: a factory is asked *what* to build, a generator is
asked only for *the next* value, and a generator function is one more thing
that returns an object.

---

[] Reject

**"Preventing Direct Creation", lines 182-184: the listing never shows the
identity failure the prose describes.**

The prose says "`type(a) is type(b)` is `False`, and `isinstance()`
comparisons across calls fail with it", but `nested_shape_factory.py`'s
output is eight `draw`/`erase` lines identical to the previous listing's.
Nothing in the run distinguishes the nested version from the module-level
one, so the price of the privacy is asserted rather than demonstrated. This
is the section's whole point, and it is the one claim a reader is most likely
to doubt.

Proposed change: add two lines to the `__main__` block and their markers:

```python
    a, b = factory("Circle"), factory("Circle")
    print(type(a) is type(b), isinstance(a, type(b)))
#: False False
```

Verified on the pinned 3.15 build: both print `False`.

Reported rather than applied because it grows a listing the chapter is
arguing against, which is an author's call about how much space a
cautionary example deserves.

---

[] Reject

**"Polymorphic Factories", lines 420-423: the lazy caching is stated but not
observable.**

"`ShapeFactory` fills its dictionary lazily. The first request for a kind
builds that kind's factory object (via `eval()`) and caches it for later
requests." Nothing in the output differs from `shape_factory1.py`'s, so the
reader takes the caching on faith. This is the only behavioral difference
between the two listings, and the sentence that names it is the reader's only
evidence.

Proposed change: in `shape_factory2.py`'s `__main__` block, print the cache
keys before and after:

```python
    print(sorted(ShapeFactory.factories))
#: []
    shapes = [ShapeFactory.create_shape(kind)
              for kind in shape_name_gen(4)]
    print(sorted(ShapeFactory.factories))
#: ['Circle', 'Square']
```

Verified: with `random.seed(4)` the four names are Circle, Square, Circle,
Square, so two `eval()` calls fill a two-entry cache and the last two
requests hit it.

Reported rather than applied for the same reason as the nested-class finding:
it spends listing space on a design the chapter then tells the reader not to
use.

---

[] Reject

**`registry.py`, line 254 (`Shape.registry[cls.__name__] = cls`): why the
hard-coded `Shape` rather than `cls`, unexplained.**

Writing `cls.registry[cls.__name__] = cls` behaves identically here, so a
reader has no way to see why the base class is named explicitly. The reason
is that `cls.registry` resolves through the MRO, so a subclass that ever
assigns its own `registry = {}` would silently start a second table and
`make()` would stop finding its descendants. Chapter 37's `trash.py` makes
the same choice with the same silence.

Proposed change: one sentence in the caveat paragraph after
"Key on a qualified name if that can happen."

> Registration names `Shape.registry` rather than `cls.registry` on purpose:
> `cls.registry` resolves through the MRO, so a subclass that gave itself a
> `registry` of its own would quietly start a second table that `make()`
> never reads.

Since this chapter owns the registry caveats for chapters 14, 17, and 37,
this is the right place for it if it is stated anywhere.

---

[] Reject

**"The Pythonic Factory: a Dictionary", line 279: "the most common form of
factory in idiomatic Python" is an unsupported superlative, and "it" is
ambiguous.**

The sentence reads "This is the same self-registration used in [Pattern
Refactoring](...), and it is the most common form of factory in idiomatic
Python." "It" can attach to self-registration or to the dictionary factory of
the previous listing. Read as self-registration, the claim is doubtful:
`__init_subclass__()` registries are a specialist tool, and the far more
common Python factory is the plain dict two listings up — or just calling the
class. Read as the dictionary, the sentence contradicts its own first half.

Proposed change: split the claims and drop the superlative.

> This is the same self-registration used in
> [Pattern Refactoring](37_Pattern_Refactoring.md#simulating-a-trash-recycler).
> A dictionary of classes, filled by hand or filled by the classes
> themselves, is the ordinary Python factory.

---

[] Reject

**"Builder", line 736: "The remaining creational pattern in *GoF Design
Patterns* is *Builder*" is not accurate.**

GoF lists five creational patterns: Abstract Factory, Builder, Factory
Method, Prototype, and Singleton. The chapter has covered three of the five
by this point, so two remain, not one. Singleton is simply somewhere else in
this book.

Proposed change:

> The last creational pattern in *GoF Design Patterns* this chapter has not
> covered is *Builder* ([Singleton](24_Singleton.md) has its own chapter):

---

[] Reject

**`shape_factory1.py` (line 66, 71) and `shape_factory2.py` (line 391, 396):
`i` names a shape-name string, not an index.**

Both listings write `shapes = [Shape.factory(i) for i in shape_name_gen(4)]`,
where `i` is a `str` like `"Circle"`. `i` reads as a loop counter everywhere
else in the book, so the comprehension looks like it is indexing when it is
naming. The same two functions also write `for i in range(n):` with `i`
unused in the body.

Proposed change, in both listings:

- `for i in range(n):` becomes `for _ in range(n):`
- `[Shape.factory(i) for i in shape_name_gen(4)]` becomes
  `[Shape.factory(kind) for kind in shape_name_gen(4)]`
- `[ShapeFactory.create_shape(i) for i in shape_name_gen(4)]` becomes
  `[ShapeFactory.create_shape(kind) for kind in shape_name_gen(4)]`

`kind` is already the parameter name on `Shape.factory()` and
`ShapeFactory.create_shape()`, so the call site would then use the same word
the signature does. `nested_shape_factory.py`'s `for i in range(n):`
(line 160) has the same unused `i` and should get `_` too. No output changes.

Reported rather than applied only because it edits three listings for
readability alone; the change itself is mechanical and safe.

---

## Cross-chapter

[] Reject

**Chapter 20 (`20_Rethinking_Objects.md`): the deep-review skill's accrued
note is stale.**

`.claude/skills/deep-review/SKILL.md`, in the "Accrued notes" list, says
"the registry factory's import-time-registration and name-collision caveats
live in 27 and back the registries in 20/37". Chapter 20 contains no registry
and no `__init_subclass__()` — `grep -ni "registry\|__init_subclass__\|
register" Chapters/20_Rethinking_Objects.md` returns nothing. The chapter-20
reviewer reports the same. The "20" in that note is wrong.

Proposed change, in `SKILL.md` only (no chapter edit): change
"back the registries in 20/37" to "back the registries in 14/17/37", which
are the three chapters that actually build one — 14's `register.py` class
decorator, 17's `init_subclass.py`, and 37's `trash.py`.

---

[] Reject

**Chapter 14 (`14_Decorators.md`), "Decorating Classes", `register.py`
around line 663: the same two caveats apply and are not mentioned.**

`register.py` builds a name-keyed registry through a class decorator. It has
both hazards this chapter owns: the decoration runs when the defining module
is imported (so a class in an unimported module never registers, and a
`lazy import` of it defers registration indefinitely), and `registry` is
keyed by `cls.__name__`, so two same-named classes from different modules
overwrite each other silently. Chapter 14 says neither, and its only forward
pointer is to chapter 17 for `__init_subclass__()`.

Proposed change in chapter 14, after "it exists only for the side effect of
recording the class.":

> Recording by side effect carries two caveats, both covered in
> [Factory](27_Factory.md#the-pythonic-factory-a-dictionary): a class in a
> module nobody imports never registers, and `registry` keyed by
> `cls.__name__` lets two same-named classes overwrite each other.

Anchor check: `#the-pythonic-factory-a-dictionary` is the pandoc slug for
this chapter's heading and passes `heading_links.py`.

---

[] Reject

**Chapter 17 (`17_Metaprogramming.md`), "Self-Registration of Subclasses"
around line 370: same pointer.**

17 teaches the `__init_subclass__()` mechanism thoroughly (implicit
classmethod, subclass keywords, why the defining class is absent from its own
registry) and this chapter now links to it for that. The reverse pointer is
missing: 17 never says what goes wrong with a registry in practice.

Proposed change in chapter 17, at the end of the section: one sentence
pointing at [Factory](27_Factory.md#the-pythonic-factory-a-dictionary) for
the import-timing and name-collision caveats, so the mechanism and its
failure modes are one link apart in both directions.

---

[] Reject

**Chapter 6 (`06_Modules_and_Packages.md`), "Lazy Imports" around line 396:
worth naming the concrete casualty.**

This chapter now warns that a `lazy import` defers the module body and with
it any registration, and that an import written purely for a side effect
never uses the imported name, so it never loads at all. Verified on the
pinned 3.15.0b2 build: `lazy import extra_shapes` with the name never used
afterward prints nothing, and `python -X lazy_imports=all` does the same to a
plain `import extra_shapes`.

Chapter 6's own caveat paragraph mentions only that errors surface late.
Proposed change there: after "the error surfaces at that first use rather
than at the import line," add

> An import that exists only for a side effect, such as registering a plugin
> class ([Factory](27_Factory.md#the-pythonic-factory-a-dictionary)), never
> uses the imported name, so `lazy` stops it from running at all.
> Keep those imports eager.

This is exercise 6's setup in this chapter, so the two would line up.

---

[] Reject

**`Solutions/27_Factory.md`: house-style drift.**

Two listings (exercises 1 and 2, at lines 9 and 62) open with
`from __future__ import annotations`. Under PEP 649 on the pinned Python that
import does nothing, and `thinking-in-python-skill.md` says explicitly that
forward references need "no `from __future__ import annotations`." The
chapter's own `shape_factory1.py` and `shape_factory2.py` omit it and their
`Shape.factory(kind: str) -> Shape` annotations resolve fine.

The same two listings also drop the `@override` decorators the chapter's
versions carry on `draw()` and `erase()`; exercise 6 is the only solution
that uses `@override`. Exercises 3 and 4 drop them too.

Proposed change in `Solutions/27_Factory.md`: delete both
`from __future__ import annotations` lines and restore `@override` on the
overriding methods in exercises 1, 2, 3, and 4, so the solutions match the
listings they answer.
