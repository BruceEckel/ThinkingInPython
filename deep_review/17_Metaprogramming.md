When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Intro roadmap sentence contradicts the two sections that follow.**
The intro closes with "This chapter shows the simpler tools first,
then metaclasses for situations that still need them."
The next two sections are "Generating Classes with `type`" and
"Generating Classes with `exec()`", and the first sentence of the first one is
"Since metaclasses create classes, you can call the metaclass yourself."
So the chapter actually opens by calling the metaclass, which is the opposite
of what the roadmap just promised, and the simpler hooks
(`__init_subclass__()`, `__set_name__()`) do not arrive until two sections later.

I did not change this because it decides the chapter's shape, not just a
sentence. Two ways out, and I recommend the first:

1. Fix the sentence to match the chapter. Replace
   "This chapter shows the simpler tools first, / then metaclasses for
   situations that still need them."
   with
   "This chapter starts by building classes by hand, so you can see what a
   `class` statement actually does. / Then come the simpler hooks, and finally
   metaclasses for the jobs that still need them."
2. Move "Generating Classes with `type`" and "Generating Classes with `exec()`"
   after "Learning a Name with `__set_name__()`", so the order matches the
   promise. Cost: `display_object()`'s first appearance moves, the `my_list.py`
   `ml.__class__.__class__` line that introduces "the metaclass" would sit right
   before "Writing a Metaclass" (which is arguably better), and the
   `EventMaker | NOT_CREATED` sentinel paragraph forward-references
   "Choosing Which Dunders to Show" either way, so nothing breaks there.

---

[] Reject

**`greenhouse.py` teaches five unrelated things at once.**
Section: Generating Classes with `type`.
The listing is the chapter's first substantial one and it introduces, in one
block: three-argument `type()` on a real problem, a `dict` subclass with a lazy
overridden `__getitem__()`, a PEP 661 sentinel used as a placeholder *and* as a
union member in an annotation, a `@dataclass` with two `ClassVar`s and a
`__post_init__()` registry, a text-file parser, and the
nested-function-has-no-`__class__`-cell rule. Four paragraphs of prose then
unpack it. `class_via_type.py` and `my_list.py` before it are each one idea, so
the escalation from "one idea" to "six ideas" happens in a single step.

Proposal: keep `greenhouse.py` where it is, but split the laziness out. Show a
first version whose `_event_maker` dict is built eagerly with a
dict comprehension calling `type()` (three lines, no `EventMakers` class, no
sentinel), point out that it builds seven classes whether or not the schedule
uses them, and only then introduce `EventMakers` as the fix. That also gives
the sentinel its own moment instead of arriving inside a base-class subscript.

Cost: one extra listing and roughly a page. If that is too much, an alternative
is to leave the code alone and add one sentence before the listing naming the
three moving parts the reader is about to meet, so the block is read as three
things rather than one wall.

---

[] Reject

**`commander.py`: the `namespace` annotation is not true at run time.**
Section: Generating Classes with `exec()`.

```python
namespace: dict[str, type[Command]] = {"Command": Command}
exec(klass, namespace)
```

`exec()` inserts `__builtins__` into any globals mapping that lacks it.
Verified on the pinned 3.15:

```
>>> ns: dict[str, object] = {}
>>> exec("class Q: pass", ns)
>>> sorted(ns)
['Q', '__builtins__']
```

So after the `exec()` call the dict holds a module (or a dict) under
`__builtins__`, and `dict[str, type[Command]]` is a false statement about the
value type in a book that argues for precise types.

The annotation is doing pedagogical work, though: the prose immediately after
says "The type checker can't see into the string, / so it believes
`namespace[class_name]` is a plain `type[Command]`". Changing it to
`dict[str, Any]` keeps the `cast()` justified (the checker then sees `Any`
rather than a wrong-but-specific type) but costs that sentence.

Recommended: change the annotation to `dict[str, Any]`, and rewrite the two
prose lines to

> The type checker can't see into the string, so `namespace[class_name]` is
> just `Any` to it.
> `cast(Callable[[], Command], ...)` records the actual no-argument signature at
> the one place the class is created, the same idiom `greenhouse.py` uses for
> `EventMaker`.

Alternative, if you prefer to keep the sentence: leave the annotation and add a
half-sentence noting that `exec()` also drops `__builtins__` into the dict, so
the annotation describes the entries you put there rather than everything the
dict ends up holding.

---

[] Reject

**`function_is_descriptor.py`'s `Person` is a hand-written data class.**
Section: Learning a Name with `__set_name__()`.

```python
class Person:
    def __init__(self, name: str) -> None:
        self.name = name

    def greet(self) -> str:
        return f"Hello, {self.name}"
```

`__init__()` does nothing but assign one parameter to one field, which the house
style says makes it a `@dataclass` unless the manual form is what the code is
teaching. Here the lesson is the descriptor protocol, not `__init__`, and
nothing in the prose explains the deviation. Verified that the `@dataclass`
form produces byte-identical output:

```python
from dataclasses import dataclass

@dataclass
class Person:
    name: str

    def greet(self) -> str:
        return f"Hello, {self.name}"
```

Counterargument for rejecting this: the listing's own comment is
"`# def created a plain function in the class namespace`", and a reader could
take `@dataclass` to be part of how that namespace got populated. If that
worry outweighs the style rule, leave it and consider adding a short line to
`ADVERSARIAL.md`-style notes so the next sweep of
`grep "def __init__(self" Chapters/` does not re-raise it.

---

[] Reject

**`mcl` is not a convention.**
Section: Writing a Metaclass, the paragraph beginning
"By convention the first argument of a metaclass method is `cls`".

The claim "except for `__new__()`, which uses `mcl` (metaclass)" overstates it.
The spellings actually in use are `mcs` (pylint's `bad-mcs-classmethod-argument`
default), `mcls` (what CPython's own sources use, and what ruff issue #24599
asks ruff to accept), and `metacls`. `mcl` appears only here, three times, all
in this chapter — nothing else in `Chapters/` or `Solutions/` uses any of them.

Recommended: rename the parameter in `new_vs_init.py` from `mcl` to `mcls`
(three occurrences: the `__new__` signature and the `super().__new__(mcl, ...)`
call), and change the prose to
"except for `__new__()`, whose first argument is the metaclass itself and is
usually written `mcls` or `mcs`."
Ruff and ty both pass with `mcls`; the `#:` output does not change.

Note that `prepare_namespace.py` correctly uses `cls` for `__prepare__()`
(ruff's N804 requires `cls` for a `classmethod`), so `__prepare__()` stays as
it is either way.

---

[] Reject

**The metamethod claim is stated but never shown failing.**
Section: Intercepting Instance Creation, opening paragraph:
"A method defined on the metaclass becomes a method of the *class object*,
callable on the class but not on its instances."

Every listing in the chapter only ever exercises the working half.
`mixin.py` prints `Derived.helper()` and stops; nothing shows
`Derived().helper()` refusing. That is the exact distinction the paragraph
draws against `classmethod`, and it is the one a reader will get wrong first.

Verified addition (drop in at the end of `mixin.py`; the message is exact on the
pinned 3.15):

```python
from exceptions import ignore
...
with ignore(AttributeError):
    Derived().helper()  # type: ignore
#: AttributeError("'Derived' object has no attribute 'helper'")
```

Placement is the open question, which is why I did not apply it.
`mixin.py` lives under "Multiple Inheritance in a Metaclass", whose point is
layout conflicts, so bolting a metamethod demo onto it splits that listing's
attention. The alternative is to add the same two lines to `simple_meta.py`
instead, calling `Simple.uses_metaclass` — but that one *is* an ordinary method
patched onto the class, so it would show the opposite result and confuse
things. `mixin.py` is the right host despite the section it sits in; a
one-clause lead-in ("and, being a metamethod, only through the class:") would
carry it.

---

[] Reject

**The two multiple-inheritance failure modes are taught in two different
sections.**
`metaclass_layout_conflict.py` (instance layout conflict) sits in
"### Multiple Inheritance in a Metaclass", and
`multiple_metaclass_inheritance.py` (metaclass conflict) sits three pages later
at the end of "When You Still Need a Metaclass". The later one already has to
reach back — "As with the layout conflict above, ty sees this without running
the program" — which is the tell that it is separated from its pair.

Both are "multiple inheritance blows up in a way you didn't expect," both are
caught statically by ty, and both carry a `# type: ignore` for the same reason.
Read together they make one point twice; read apart the reader meets the same
shape twice without noticing it is the same shape.

Proposal: move the `multiple_metaclass_inheritance.py` listing and its
"One caution: a class has a single metaclass" paragraph up into
"### Multiple Inheritance in a Metaclass", after `mixin.py`, and retitle that
subsection "### Multiple Inheritance and Metaclasses". "When You Still Need a
Metaclass" then ends on `__prepare__()` and the class-decorator comparison,
which is a stronger close for a section named that.

Cost: "When You Still Need a Metaclass" loses its last two paragraphs and needs
a new closing sentence; the moved paragraph's "As with the layout conflict
above" becomes "As with the layout conflict just shown"; nothing outside this
chapter links to either section (checked with `heading_links.py`).

---

[] Reject

**`INTERESTING_DUNDERS` and `REDEFINED_DUNDERS` are explained but never run.**
Section: Choosing Which Dunders to Show.
The section spends fourteen lines on the three `dunder` modes plus `exclude`,
and the only mode any chapter-17 listing exercises is `ALL_DUNDERS` (plus an
explicit two-name list in `new_vs_init.py`). The distinction that carries the
most weight — "A class that overrides none of the four still shows all four"
versus "`REDEFINED_DUNDERS` ... keeps only the ones whose value differs from
`object`'s own" — is asserted, not shown. `comparison.py` in chapter 12 uses
both, but that file has no Markdown block, so the reader never sees it.

Verified listing, output produced on the pinned 3.15 and checked with
`validate_output.py`, ruff (70 cols) and ty:

````markdown
```python
# dunder_modes.py
from dataclasses import dataclass
from display import (
    INTERESTING_DUNDERS,
    REDEFINED_DUNDERS,
    display_object,
)

class Plain:
    pass

@dataclass
class Point:
    x: int
    y: int

display_object(Plain, INTERESTING_DUNDERS)
#: [Attributes]
#:   None
#: [Methods]
#:   • __eq__(self, value, /)
#:   • __hash__(self, /)
#:   • __init__(self, /, *args, **kwargs)
#:   • __repr__(self, /)

display_object(Plain, REDEFINED_DUNDERS)
#: [Attributes]
#:   None
#: [Methods]
#:   None

display_object(Point, REDEFINED_DUNDERS)
#: [Attributes]
#:   • __hash__ = None [CV]
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int, y: int) -> None
#:   • __repr__(self)

display_object(Point, REDEFINED_DUNDERS, exclude=("__hash__",))
#: [Attributes]
#:   None
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int, y: int) -> None
#:   • __repr__(self)
```
````

It lands four points in one block: `INTERESTING_DUNDERS` shows `object`'s own
four on a class that redefined nothing; `REDEFINED_DUNDERS` shows nothing for
that same class; `@dataclass` redefines three of the four and nulls the fourth;
and `exclude=("__hash__",)` drops the `__hash__ = None` row, which is exactly
why `comparison.py` passes that argument.

Placement: immediately after the paragraph ending "deliberately narrowing the
comparison to those four", before the "Every class, even an empty one" paragraph.
I did not apply it because it is a new listing in a section that is already the
densest prose in the chapter, and because you may prefer a two-call version
(drop the `Plain, INTERESTING_DUNDERS` call and the `exclude` call) to keep it
short.

---

[] Reject

**`display.py`'s `_truncate()` returns text longer than its budget.**
Section: Building `display_object()`.

```python
def _truncate(text: str, budget: int) -> str:
    # Keep text within budget, marking a cut with an ellipsis:
    if len(text) <= budget:
        return text
    return text[:budget - 3] + "..."
```

When `budget` is 3 or less, `budget - 3` is zero or negative, so the slice
counts back from the *end* of the string and the result is longer than the
budget rather than shorter. Measured:

```
_truncate("abcdefghij", 5)  -> 'ab...'        (5, correct)
_truncate("abcdefghij", 2)  -> 'abcdefghi...' (12, wanted 2)
_truncate("abcdefghij", 0)  -> 'abcdefg...'   (10, wanted 0)
```

`_format_attribute()` can reach a negative budget for real, since
`budget = max_width - len(label) - len(tag) - 7` and nothing bounds `len(label)`:

```python
class Wide:
    an_extremely_long_class_attribute_name_that_eats_the_budget_entirely = 12345
display_object(Wide)
#:   • an_extremely_long_class_attribute_name_that_eats_the_budget_entirely = ... [CV]
```

That line is 79 columns against `max_width=65`. No listing in the book trips
this today, but the chapter presents the tool as something to point at
unfamiliar objects, so a reader will.

Proposed fix (three added lines, no behavior change for any budget of 4 or
more, so no existing `#:` marker moves):

```python
def _truncate(text: str, budget: int) -> str:
    # Keep text within budget, marking a cut with an ellipsis:
    if len(text) <= budget:
        return text
    if budget < 4:  # No room for text plus the ellipsis
        return "..."[:max(budget, 0)]
    return text[:budget - 3] + "..."
```

That still leaves the *label* itself unbounded, which is the real cause of the
79-column line. If you want the whole line inside `max_width`, `_format_attribute()`
also has to truncate `label`, which is a bigger change and probably not worth it
for a display helper. Say so in the prose instead, or leave the second half
alone. `display.py` is shared, so this needs a book-wide `make verify` rather
than a chapter-17 run.

---

[] Reject

**The chapter's closing claim about ordering is never traced.**
Section: Which Hook for Which Job, final paragraph:

> `__prepare__()` runs before the body, `__set_name__()` and
> `__init_subclass__()` run as it finishes, a decorator runs after, and
> `__call__()` runs later still, each time someone uses the result.
> Knowing the sequence is what tells you which one to write.

This is the chapter's thesis and its most useful takeaway, and it arrives as an
unillustrated assertion on the last page. Every hook has been demonstrated
alone; none has been demonstrated *relative to the others*, which is the thing
the paragraph says matters. It is also less precise than it could be: two of the
hooks (`__set_name__()` and `__init_subclass__()`) run from inside
`type.__new__()`, so they land in the middle of the metaclass's own `__new__()`
rather than merely "as the body finishes", and no prose in the chapter says so.

Verified listing (runs clean through `validate_output.py`, `ruff` at 70 cols,
and `ty`; output below is exactly what it prints on the pinned 3.15):

````markdown
```python
# hook_order.py
from typing import Any

class Watched:
    def __set_name__(self, owner: type, name: str) -> None:
        print(f"__set_name__({owner.__name__}, {name})")

class Meta(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> dict[str, Any]:
        print(f"__prepare__ {name}")
        return {}

    def __new__(mcl, name: str, bases: tuple[type, ...],
                nmspc: dict[str, Any]) -> type:
        print(f"__new__ {name} enter")
        cls = super().__new__(mcl, name, bases, nmspc)
        print(f"__new__ {name} exit")
        return cls

    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        print(f"__init__ {name}")

def tag[T: type](cls: T) -> T:
    print(f"decorator {cls.__name__}")
    return cls

class Base(metaclass=Meta):
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        print(f"__init_subclass__ {cls.__name__}")
#: __prepare__ Base
#: __new__ Base enter
#: __new__ Base exit
#: __init__ Base

@tag
class Derived(Base):
    field = Watched()
    print("class body")
#: __prepare__ Derived
#: class body
#: __new__ Derived enter
#: __set_name__(Derived, field)
#: __init_subclass__ Derived
#: __new__ Derived exit
#: __init__ Derived
#: decorator Derived
```
````

The two traces earn their keep separately. `Base`'s shows the bare sequence and
shows, without a word of prose, that `Base`'s own `__init_subclass__()` never
runs for `Base` — the thing the "Making a Class Final" section has to assert.
`Derived`'s shows `__set_name__()` and `__init_subclass__()` firing *inside*
`super().__new__()`, between "enter" and "exit", and the decorator arriving last.

If you take this, use `mcl` or `mcls` consistently with whatever the earlier
`mcl` finding settles on, and note that `__prepare__`'s first parameter must
stay `cls` for ruff's N804.

Placement, and why this stays a proposal:

1. **As written, at the head of "Which Hook for Which Job"**, before the job
   list, with the final paragraph rewritten to read off the trace instead of
   asserting it. This is what I would do: the chapter earns the summary rather
   than announcing it.
2. **Near the front, as motivation** (the skill's "front-load the payoff"),
   right after the `abc.ABC`/`EnumType` paragraph. Against: every name in the
   trace is unfamiliar at that point, so it would read as a table of contents
   in code form.

Either way the chapter grows by about a page, which is the cost to weigh.

---

[] Reject

**Exercise coverage misses two of the chapter's own claims.**
Section: Exercises.
The eight exercises cover `__init_subclass__` (1, 4), `__set_name__` (2),
metaclass `__call__` (3), `inspect` (5), the layout conflict (6), three-argument
`type()` (7), and `__new__`-versus-`__init__` (8). Nothing exercises the
`exec()` section, and nothing exercises `__prepare__()` — which the chapter
singles out as "the one with no simpler substitute, so it is worth seeing."
Two sections with no exercise, one of them the section the chapter says is the
whole reason metaclasses still exist.

Proposed additions:

> 9. `commander.py` validates `class_name` against `KNOWN_COMMANDS` before
>    splicing it into source text. Remove that check, call
>    `Command.make_class()` with a name containing a newline and a second
>    statement, and confirm that the injected statement runs. Restore the check.
>    (Verified: this works, and it makes the SQL-injection analogy concrete
>    rather than asserted.)
> 10. Change `prepare_namespace.py`'s `NoDuplicates` so that instead of raising,
>     it keeps the *first* definition of a duplicated name and discards the
>     later one. Confirm that `Handlers().on_open()` then runs the first
>     `on_open`. Explain why no class decorator could achieve the same thing.

Renumber or place as you prefer; if the set is already long enough, the
`__prepare__` one is the more important of the two.

## Cross-chapter

[] Reject

**`Solutions/17_Metaprogramming.md`: exercise 6 has no solution, and the file
does not say so.** Target: `Solutions/17_Metaprogramming.md` (I did not touch
it, per the review's scope).
The headings run `## 1.`, `## 2.`, `## 3.`, `## 4.`, `## 5.`, `## 7.`, `## 8.`
Exercise 6 asks the reader to delete a `# type: ignore` and compare ty's
`instance-layout-conflict` diagnostic with the runtime `TypeError`, so there is
no code to show, but the silent gap reads like an omission. Add a short
`## 6.` section giving the diagnostic text ty 0.0.65 actually emits, or a
one-line note that the exercise is an observation with no code answer.

[] Reject

**`Solutions/17_Metaprogramming.md` exercise 3 contradicts the chapter it
solves.** Target: `Solutions/17_Metaprogramming.md`, `exercise_3.py`.
The chapter's `singleton.py` writes

```python
    def __call__[T](
            cls: type[T], *args: Any, **kwargs: Any) -> T:
```

and spends a paragraph on why the `[T]` matters ("Without it, every singleton
loses its type and a type checker can no longer catch a misspelled attribute
access on the result"). The solution writes

```python
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
```

which is precisely the version the chapter argues against, and it uses
`super().__call__(...)` where the chapter uses `type.__call__(cls, ...)`.
Exercise 3 only asks for a third singleton class, so nothing forced the
simplification.

Suggested change in the Solutions file: copy the chapter's `__call__[T]`
signature verbatim into `exercise_3.py` and drop the `print()` tracing as the
solution already does. `super().__call__(...)` must then become
`type.__call__(cls, ...)`, because ty rejects the zero-argument `super()` once
`cls` is annotated `type[T]`:

```
error[invalid-super-argument]: `type[T@__call__]` is not an instance or
subclass of `<class 'Singleton'>` in `super(<class 'Singleton'>,
type[T@__call__]) call
```

I added a paragraph to the chapter explaining that constraint, so the solution
matching it is now the consistent state.
