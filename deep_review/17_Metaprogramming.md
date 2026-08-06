# Deep review: 17_Metaprogramming.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

Verification run before writing this file (all against the freshly synced tree, read-only):

- every listing executed; **every `#:` marker matches real stdout**
- `ty check 17_Metaprogramming` clean, `ruff check` clean, `pytest` 7 passed
- `heading_links.py` clean, `validate_output.py` clean, `codespell` clean, `reflow_prose.py --diff` reports 0 paragraphs
- every cross-reference target confirmed by reading the target chapter: `14_Decorators.md#a-limitation-methods-need-a-descriptor`, `24_Singleton.md#singleton-using-metaclasses` (including the claim that it uses `klass: Any = cls`, adds `instance`, and swaps `__new__()`), `09_Class_Attributes.md#class-attributes-are-not-default-values`, `08_Static_Typing.md#hints-are-not-enforced-at-run-time`
- the three chapter-12 listings named in the `[CV]` discussion (`classvar_dataclass.py`, `class_with_defaults.py`, `display_messenger.py`) tag exactly what the prose says they tag
- claims re-verified directly on the pinned 3.15.0b4: `class X(dict, type)` raises the same layout `TypeError` with no metaclass involved; ty reports `instance-layout-conflict` on the suppressed line and `conflicting-metaclass` on the other; the `[T]` on `Singleton.__call__` really does turn `Any` into `ASingleton` (checked with `reveal_type`); `__annotations_cache__` is absent until `__annotations__` is first read, then holds the result; `__annotate_func__` is the computing function

**No outright errors found, so nothing was edited directly.** Everything below is a proposal.

---

## 1. Deliver the class-decorator promise, or stop making it

**Kind:** teaching
**Where:** the opening tool list (line ~74) and section "When You Still Need a Metaclass" (line ~918)
**Problem:** the chapter names class decorators twice as one of the three tools that replace a metaclass, and never shows one, never links to one, and never says what they can and cannot do. A reader told to prefer a tool the chapter refuses to deliver has to go find it. `__init_subclass__()` and `__set_name__()` each get a full section; the third item is a dangling reference.
**Proposal:** link both mentions to the existing coverage in chapter 14 and state the dividing line once. At line ~74:

```
- *Class decorators* transform a class after Python builds it
  ([Decorating Classes](14_Decorators.md#decorating-classes)).
```

At line ~918, replace "For everything else, `__init_subclass__()`, `__set_name__()`, and class decorators are simpler and easier to read." with:

```
For everything else, `__init_subclass__()`, `__set_name__()`,
and [class decorators](14_Decorators.md#decorating-classes)
are simpler and easier to read.
A class decorator receives the finished class,
so it can add, replace, or inspect members,
but it cannot change the name, the bases, or the namespace,
and it cannot give the class object behavior of its own.
Setting `__call__` from a decorator makes *instances* callable;
only a metaclass makes the class callable in a new way.
```

That last distinction is the operative one behind the whole "When You Still Need a Metaclass" list, and stating it here converts a bullet list into a rule the reader can apply.
**Cost:** adds one inbound link to `14_Decorators.md#decorating-classes` (the heading exists; `heading_links.py` will gate it). No terms redefined.

---

## 2. State that `__init_subclass__()` never runs for the class that defines it

**Kind:** teaching
**Where:** section "Self-Registration of Subclasses" (line ~408) and section "Making a Class Final" (line ~880)
**Problem:** this is the single most common surprise with `__init_subclass__()`, the chapter's most-recommended hook, and the chapter never states it. Two listings silently depend on it: `Color` and `Shape` stay out of their own registries, and `final_runtime.B` builds successfully even though its own `__init_subclass__()` raises unconditionally. The explanation given for the second, "Python builds `B` normally because `A` does not forbid subclassing," names the operative cause but leaves the reader to infer the rule from it. Verified: defining the hook in `B` prints nothing when `B` is created and fires only for `C`.
**Proposal:** extend the paragraph at line ~407 (currently ending "Its first argument is the new subclass.") with:

```
It never runs for the class whose body defines it,
only for classes derived from that class,
which is why neither `Color` nor `Shape` appears in its own registry.
```

Then sharpen line ~880 from "Python builds `B` normally because `A` does not forbid subclassing." to:

```
Python builds `B` normally.
A class's own `__init_subclass__()` never runs for that class,
and the version that does run when `B` is created is the one `B` inherits from `A`,
which is `object`'s do-nothing default.
```

**Cost:** none; both are additions to existing paragraphs.

---

## 3. Ground the chapter: the reader has already used two metaclasses

**Kind:** teaching
**Where:** section opening, after "That is metaclass programming." (line ~64)
**Problem:** the chapter introduces metaclasses as a fascinating tool to be avoided, which leaves a reader with no reason to believe metaclasses matter at all. Two metaclasses they have already used sit in the standard library, and both do something the chapter later claims needs a metaclass, which makes the claim concrete instead of theoretical. `abc.ABC` appears in chapter 13 and `Enum` in chapter 12, so both referents are already familiar.
**Proposal:** insert after line ~64:

```
You have used metaclasses already, without writing one.
`abc.ABC` is built by `abc.ABCMeta`,
which makes a class with an unimplemented abstract method refuse instantiation.
An `Enum` subclass is built by `enum.EnumType`,
which turns each class-body assignment into a member
and makes `for c in Color` walk them.
Iterating a class is behavior on the class object,
which is where a metaclass can put it and an ordinary class cannot.
```

Verified on 3.15.0b4: `type(abc.ABC) is ABCMeta`, `type(Color) is enum.EnumType`, and `__iter__` lives in `EnumType.__dict__`.
**Cost:** none. It also pre-answers the first bullet of "When You Still Need a Metaclass" (a custom `__iter__()` on the class), which currently says "shown above" while only `__call__()` was shown.

---

## 4. Show `__prepare__()`, the one metaclass power with no simpler substitute

**Kind:** teaching
**Where:** section "When You Still Need a Metaclass" (line ~913)
**Problem:** the section lists three genuine reasons to write a metaclass. Two are demonstrated (`__call__` interception, and a shared metaclass enforcing an invariant is a small step from `simple_meta1.py`). The third, `__prepare__()`, is named and never shown, so a reader who hits that case has a name and no mechanism. It is also the strongest possible argument for the chapter's thesis: it is the one hook `__init_subclass__()`, `__set_name__()`, and a class decorator cannot reproduce, because it acts while the class body is still executing.
**Proposal:** add a listing after the three bullets. Verified: runs, passes `ty`, passes `ruff` at line-length 70.

````
```python
# prepare_namespace.py
from typing import Any
from exceptions import ignore

class NoDuplicates(dict[str, Any]):
    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            raise TypeError(f"{key} defined twice")
        super().__setitem__(key, value)

class Strict(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> NoDuplicates:
        return NoDuplicates()

with ignore(TypeError):
    class Handlers(metaclass=Strict):
        def on_open(self) -> None: ...
        def on_close(self) -> None: ...
        def on_open(self) -> None: ...  # noqa: F811
#: TypeError('on_open defined twice')
```
````

Prose to follow it:

```
`__prepare__()` runs before the class body does,
and whatever mapping it returns is the namespace that body executes into.
Every `def` and every assignment in the body becomes a `__setitem__()` call on that mapping,
so `NoDuplicates` sees the second `on_open` land on a name it already holds.
Python then hands the finished mapping to `type.__new__()`.
No other hook can do this: `__init_subclass__()`, `__set_name__()`,
and a class decorator all run after the body finished and the duplicate already won.
The `# noqa: F811` suppresses ruff's own report of the same mistake,
which is the static half of the check;
`__prepare__()` catches it at run time, including on names the body computes.
```

**Cost:** ~35 lines in an already-long chapter, and a new `exceptions.py` import (already used by `commander.py` and `metaclass_layout_conflict.py` in this chapter). Basename `prepare_namespace.py` is unused book-wide.
**Alternative if you would rather not add a listing:** replace the bullet with two sentences saying what `__prepare__()` buys (a namespace that reacts to each assignment as the body runs: rejecting duplicates, recording order under another key, pre-seeding names the body can see) and noting that ordering alone is no longer a reason, since class-body namespaces have been ordered since 3.7.

---

## 5. Give the chapter a closing section

**Kind:** structure
**Where:** after "The Tool in Use" (line ~1315), before Exercises
**Problem:** a 1375-line chapter that opens with a strong thesis ("use the simplest hook, not a metaclass") ends on "The rest, from `__class__` to `__static_attributes__`, is the bookkeeping every class carries." The thesis is never cashed in, and the decision rule the chapter spent thirteen sections building is scattered across "Use a metaclass only when these cannot do the job" (line 76), "prefer `__init__()`, which is simpler" (line 692), "Choose the lightest tool that solves your problem" (line 772), and "When You Still Need a Metaclass". The neighbouring chapters all close this way: 18 "Choosing a Strategy", 20 "Guidelines", 23 "The Pattern That Disappeared", 24 "Which Should You Use?".
**Proposal:** add a short section titled for its content, not "Summary". Suggested title: **"Which Hook for Which Job"**. Content: a job-to-tool list (react to each new subclass → `__init_subclass__()`; let an attribute learn its own name → `__set_name__()`; rewrite a finished class → a class decorator; build a family of classes from data → `type()`; change name, bases, or namespace before construction → a metaclass `__new__()`; control the namespace the body executes into → `__prepare__()`; decide whether an instance gets built at all → a metaclass `__call__()`; read a class you did not write → `inspect`), then close on the insight the chapter earns and never states: none of this is a special facility, it is the ordinary consequence of a class being an object built at run time by executing its body, so every hook is a normal function called at a known moment in that sequence.
**Cost:** none structurally. It does add a heading, which changes nothing about existing anchors.

---

## 6. Explain the `**kwargs` that three listings carry

**Kind:** teaching
**Where:** section "Self-Registration of Subclasses" (line ~408)
**Problem:** `**kwargs: object` appears in `init_subclass.py` twice and in `final_runtime.py` once, and the chapter never says what it is for or where the keywords come from. A reader copying the idiom carries a parameter they cannot explain. The answer is one of the nicest features of the hook: keywords written in the subclass header reach it.
**Proposal:** after the sentence added in proposal 2, add:

```
The keyword arguments come from the subclass header.
Writing `class Blue(Color, shade="cool"):` delivers `shade="cool"` to `__init_subclass__()`,
so a subclass can configure its own registration.
Passing the rest on with `super().__init_subclass__(**kwargs)` lets a base further up the chain take the keywords it declared,
and makes an unrecognized keyword an error rather than a silent no-op.
```

Verified: declaring `def __init_subclass__(cls, shade: str = "plain", **kw: object)` and writing `class Blue(Color, shade="cool")` registers under `"cool"`.
**Cost:** none if prose-only. Adding a listing for it would be a second option; the existing `init_subclass.py` is already carrying two hierarchies and should not grow a third concern.

---

## 7. Show the rejected subclass in `final.py`

**Kind:** code
**Where:** listing `final.py` (line ~836) and the sentence at line ~848
**Problem:** `final.py` demonstrates nothing about `@final`. It builds a `B`, prints `"B"`, and the actual point (that the checker rejects a subclass) lives only in the prose sentence that follows. The book's own convention elsewhere is to put the rejected line in the listing as a comment: chapter 08 has `# MAX_RETRIES = 5  # ty: cannot assign to final name "MAX_RETRIES"`, chapter 09 has `# a.total = 99  # ty: cannot assign ClassVar "total" via instance`.
**Proposal:** add the commented line to the listing, matching ty's real message (verified: `error[subclass-of-final-class]: Class 'C' cannot inherit from final class 'B'`):

```python
# final.py
from typing import final

@final
class B:
    pass

# class C(B): pass  # ty: cannot inherit from final class "B"
b = B()
print(type(b).__name__)
#: B
```

Line length 60, well inside 70. The prose sentence at line ~848 can then read "The commented line is what the type checker rejects; nothing at run time stops it."
**Cost:** touches `Examples/17_Metaprogramming/final.py` on the next sync. No marker change.

---

## 8. Make `greenhouse.py`'s sentinel follow the rule the chapter itself documents

**Kind:** code
**Where:** listing `greenhouse.py` (line ~163)
**Problem:** the chapter contains both halves of a contradiction about the same idiom. `display.py`, later in this chapter, annotates a sentinel-or-value parameter as `Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS`, and the prose at line ~1170 explains at length why naming the specific sentinel value is right. `greenhouse.py` instead casts the sentinel to the value type, `NOT_CREATED: EventMaker = cast(EventMaker, sentinel("NOT_CREATED"))`, which tells the checker a marker meaning "no class yet" is a callable that builds an `Event`. Nothing explains the difference, so the reader gets two contradictory models of the same construct from one chapter.
**Proposal:** use the union form. Verified: runs identically, passes `ty`, passes `ruff`.

```python
type EventMaker = Callable[[int, int], Event]
NOT_CREATED = sentinel("NOT_CREATED")

class EventMakers(dict[str, EventMaker | NOT_CREATED]):
    def __getitem__(self, class_name: str) -> EventMaker:
        if class_name not in self:
            raise ValueError(f"Unknown event class: {class_name!r}")
        maker = super().__getitem__(class_name)
        if maker is NOT_CREATED:
            print(f"Creating {class_name}")
            # Local function to pass to type constructor:
            def init(self: Event, hour: int, minute: int) -> None:
                Event.__init__(self, class_name, hour, minute)
            new_cls = type(class_name, (Event,), {"__init__": init})
            maker = cast(EventMaker, new_cls)
            self[class_name] = maker
        return maker
```

The remaining `cast()` is the one the chapter already explains at line ~318 (`type()` returns `type`, not the call signature), and the `is NOT_CREATED` check now narrows the union to `EventMaker` for real instead of by assertion. This also drops one `super().__getitem__()` call.
**Cost:** the marker output is unchanged (verified on a reduced copy). If you keep the cast instead, the chapter needs one sentence saying why this sentinel is erased into its value type while `display.py`'s is not.
**Smaller alternative:** keep the code and add that sentence.

---

## 9. Contrast zero-argument `super()` across the two generation techniques

**Kind:** teaching
**Where:** section "Generating Classes with `exec()`" (line ~323)
**Problem:** the chapter sets up a genuine lookalike pair and never closes it. `greenhouse.py`'s nested `init()` must call `Event.__init__(self, ...)` explicitly, and the chapter explains why (no `__class__` cell). `commander.py`'s generated `__init__` uses zero-argument `super()` and works. The prose next to it says "`__init__` is defined textually inside a `class` block. The compiler doesn't care that the block arrived as a string," which states the mechanism but never points at the earlier listing that failed the same test. A reader who read both eleven pages apart will not connect them.
**Proposal:** extend that paragraph:

```
`__init__` is defined textually inside a `class` block.
The compiler doesn't care that the block arrived as a string.
That is the difference from `greenhouse.py`,
whose `init()` is a nested function rather than a method in a class body,
so it gets no `__class__` cell and cannot use zero-argument `super()`.
Text that reaches the compiler as a class body gets the cell;
a function object handed to `type()` does not.
```

**Cost:** none.

---

## 10. Move the `class Simple1(SimpleMeta1)` warning after its listing, and sharpen it

**Kind:** structure, prose
**Where:** section "Writing a Metaclass" (lines ~567-576)
**Problem:** the section's second paragraph warns against a mistake using two names, `SimpleMeta1` and `Simple1`, that the reader has not met yet: the listing that defines them is below. The reader has to hold two unexplained identifiers to follow a warning about a construct they have not been shown. It is a good warning in the wrong place. "so `Simple1` becomes a metaclass-shaped class" is also imprecise: with that syntax `Simple1` is a metaclass, since it inherits `type`.
**Proposal:** keep paragraph one and the listing where they are, move the warning paragraph to just after the `display_object` discussion at line ~612, and rewrite it as:

```
Since a metaclass is a subclass of `type`,
writing `class Simple1(SimpleMeta1):` means something else.
That syntax makes `SimpleMeta1` an ordinary base class,
so `Simple1` inherits `type` and becomes a second metaclass,
not a class built by `SimpleMeta1`.
`metaclass=` is the mechanism for naming what builds a class,
independent of its base classes.
A subclass repeats `metaclass=` only if its bases do not already carry the same metaclass,
since Python computes a new class's metaclass from all of its bases.
```

**Cost:** none; nothing references the paragraph.

---

## 11. Complete the data / non-data descriptor pair

**Kind:** teaching
**Where:** section "Learning a Name with `__set_name__()`" (line ~536)
**Problem:** the chapter names *data descriptor* and states the rule that matters ("a data descriptor outranks the instance's `__dict__`"), but never names the other half, even though `function_is_descriptor.py` twenty lines earlier is a non-data descriptor. Half a distinction is worse than none: a reader concludes descriptors always win, which explains `Field` but contradicts the fact that assigning to `p.greet` shadows the method. Verified: putting `greet` in an instance `__dict__` does shadow the class function.
**Proposal:** after "Storing under `"_x"`, a name no descriptor claims, breaks the loop." add:

```
A descriptor with only `__get__()` is a *non-data descriptor*,
and the ranking reverses: the instance's `__dict__` wins.
That is why assigning `p.greet = something` shadows the method on that one instance,
while `p.x = 3` cannot shadow `Field`, because `Field` defines `__set__()`.
```

**Cost:** none.

---

## 12. Move "Making a Class Final" up beside the other `__init_subclass__()` material

**Kind:** structure
**Where:** section "Making a Class Final" (line ~830)
**Problem:** the section currently splits the metaclass arc. The sequence runs Writing a Metaclass → `__init__` vs `__new__` → Intercepting Instance Creation → Multiple Inheritance in a Metaclass → **Making a Class Final** → When You Still Need a Metaclass, and the interruption is a section about `typing.final` and `__init_subclass__()` whose only tie to metaclasses is the aside "older literature claims this requires a metaclass. It does not." "When You Still Need a Metaclass" then has to re-establish the metaclass context it lost.
**Proposal:** move it to directly after "Self-Registration of Subclasses", where its `__init_subclass__()` machinery is fresh and its "you do not need a metaclass for this" point lands before metaclasses are introduced rather than after. The metaclass sections then run uninterrupted into "When You Still Need a Metaclass".
**Cost:** the heading text must stay identical, because `08_Static_Typing.md` and `25_Template_Method.md` both link to `#making-a-class-final`. Anchors are position-independent, so the move alone breaks nothing. `test_final.py` travels with the section. Exercise 4 references `final_runtime.py` and is unaffected.
**Alternative:** leave the order and add a transition sentence at line ~830 tying it back ("Before leaving metaclasses, one more job people used to hand them.") and another at line ~907 picking the thread up.

---

## 13. Let `singleton.py` show the interception, not only its result

**Kind:** code
**Where:** listing `singleton.py` (line ~719)
**Problem:** the section's claim is that a metaclass `__call__()` sits above `__new__()`/`__init__()` and can decline to build an instance. The listing proves the outcome (`a is b`) with three asserts and prints two class names. A reader cannot narrate the mechanism from the output: nothing shows that the second `ASingleton()` skipped construction, which is the whole point.
**Proposal:** trace the decision and drop the redundant name print:

```python
    def __call__[T](
            cls: type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in Singleton._instances:
            print(f"building {cls.__name__}")
            Singleton._instances[cls] = type.__call__(
                cls, *args, **kwargs)
        else:
            print(f"reusing {cls.__name__}")
        return Singleton._instances[cls]
```

with the markers becoming `building ASingleton` / `reusing ASingleton` / `building BSingleton` / `reusing BSingleton`. The `assert` lines stay.
**Cost:** the `#:` markers change and the final `print(a.__class__.__name__, ...)` line becomes redundant. Chapter 24 links to this section but quotes nothing from the listing.

---

## 14. Broaden the exercise set

**Kind:** exercise
**Where:** section "Exercises" (line ~1316)
**Problem:** the six exercises cover `__init_subclass__`, `__set_name__`, the singleton metaclass, runtime-final, `inspect`, and the layout conflict. Nothing exercises the two class-generation sections that open the chapter (`type()` with three arguments, `exec()`), and nothing exercises `__new__()` versus `__init__()` in a metaclass, which has a section to itself. Exercise 4 ("add a class `D(A)` and confirm it succeeds") restates the third test in `test_final.py`, which the chapter already prints, so it asks the reader to retype an answer they were just given.
**Proposal:** add two exercises and strengthen the fourth.

```
7.  Using `type()` directly, build a class `Celsius` with a base of
    `float`, an attribute `unit = "C"`, and a method
    `describe(self)` returning `f"{self} degrees {self.unit}"`.
    Confirm `Celsius(21.5).describe()` works and that
    `type(Celsius)` is `type`.
8.  In `new_vs_init.py`, move the `bases += (Tag,)` line from
    `__new__()` into `__init__()` and predict what happens before
    running it. Explain the result in terms of when the class
    object comes into existence.
```

and replace exercise 4 with something the chapter does not already answer, for example: extend `final_runtime.py` so a class can declare itself final with a keyword in its header (`class B(A, final=True)`), using the `**kwargs` that `__init_subclass__()` receives, and confirm a non-final sibling still subclasses freely.
**Cost:** `Solutions/17_Metaprogramming.md` currently answers exercises 1-5 and would need entries for whatever is added or changed. If proposal 6 is rejected, the rewritten exercise 4 has no support in the chapter and should be dropped.

---

## 15. Say that ty predicts the metaclass conflict too

**Kind:** teaching
**Where:** section "When You Still Need a Metaclass" (line ~938)
**Problem:** `multiple_metaclass_inheritance.py` carries a bare `# type: ignore` on `class C(A, B):` with no explanation, twenty lines after the chapter made a point of explaining the identical suppression in `metaclass_layout_conflict.py` and calling it "static typing at its best." The reader is left to guess whether the second ignore is the same situation or an unrelated workaround. Verified: ty reports `conflicting-metaclass` with a message naming both metaclasses.
**Proposal:** after "This creates a metaclass conflict you must resolve.", add:

```
As with the layout conflict above,
ty sees this without running the program,
reporting `conflicting-metaclass` and naming both `MetaA` and `MetaB`,
which is why the line carries a `# type: ignore`.
```

**Cost:** none.

---

## 16. Say why `EventMakers` is a `dict` subclass

**Kind:** teaching
**Where:** section "Generating Classes with `type`" (line ~248)
**Problem:** `greenhouse.py` is the chapter's largest listing and introduces a dict subclass, a sentinel, a nested closure, a dataclass registry, file parsing, and dynamic class creation at once. Four paragraphs unpack it afterwards, but they never answer the first question the listing raises: why subclass `dict` at all, rather than write a `make_event()` function. The answer is the design point of the listing.
**Proposal:** open the explanation (before the current line 248 paragraph) with:

```
`EventMakers` subclasses `dict` so the laziness is invisible at the call site.
`Event._event_maker[class_name]` reads as an ordinary lookup,
and the overridden `__getitem__()` decides whether that lookup returns a class
or builds one first.
The alternative, a `make_event()` function, would push that decision into every caller.
```

While there, consider whether the unknown-name failure should be a `KeyError` rather than a `ValueError`. `__getitem__()` raising `ValueError` surprises anyone writing `try: ... except KeyError`, and the chapter teaches EAFP elsewhere. If the `ValueError` is deliberate for its message, one clause saying so would settle it.
**Cost:** the `KeyError` change would alter no marker (the exception is never triggered in the listing) but would touch the sentence at line ~260.

---

## 17. Point forward to `display_object()` at its first use

**Kind:** prose
**Where:** the chapter's first listing (line ~11)
**Problem:** the chapter's opening line of code is `from display import display_object`, and the tool is not built until line 1003, roughly a thousand lines later. A reader arriving at chapter 17 in order has met it in chapters 7, 9, and 12, but nothing tells them that this is the chapter where it finally gets explained, so the pull to skip ahead is unresolved.
**Proposal:** one clause in the sentence introducing the first listing, e.g. "…using `display_object()`, the inspection helper this chapter builds in [Building `display_object()`](#building-display_object)."
**Cost:** adds an internal anchor link; `heading_links.py` gates it. Verified against `tools/heading_links.py`'s own slugger: `### Building \`display_object()\`` slugs to `building-display_object`, so no explicit `{#id}` is needed.

---

## 18. Prose pass: small wording items

**Kind:** prose
**Where:** scattered
**Problem:** individually minor, listed together so they can be accepted or rejected in one pass. None changes meaning.
**Proposal:**

- line ~151: "Generating classes programmatically with `type` creates possibilities." says nothing concrete. Suggest: "Generating classes programmatically with `type` pays off when a family of classes differs only by name."
- line ~250: "turns `"WaterOn 3:30"` into three plain strings" → drop "plain".
- line ~707: "the same method that makes any object callable when parentheses are attached" → "…callable when you call it with parentheses" (or just "when it is called").
- line ~807: "as long as the extra class is a plain mixin with no competing layout" → drop "plain".
- line ~1150: "A class has no instance-level storage to compare against:" strands the preposition. Suggest "A class has no instance-level storage for the comparison:".
- line ~1160: "from where the value actually lives" → drop "actually".
- lines ~1180-1182: "A class inherits all four of those from `object` without overriding any of them, so `INTERESTING_DUNDERS` shows `object`'s generic versions, which can look like the class defined them itself." reads as a general claim but means the overriding-nothing case, and ends on a flourish "itself". Suggest: "A class that overrides none of the four still shows all four, because it inherits `object`'s versions, and the report cannot tell those from ones the class wrote."
- lines ~68 and ~563 use "hooks", which is on the watch list. It may well be the right word here, since it is the standard name for `__init_subclass__()` and `__set_name__()`. Flagged for your call, not changed.
- line ~68: "Python 3 added simpler hooks" is loose. `__init_subclass__()` and `__set_name__()` arrived in 3.6; class decorators predate Python 3 entirely. "Python 3.6 added the first two" would be precise, or drop the version.

**Cost:** none.

---

## 19. Rename `SimpleMeta1` / `Simple1`

**Kind:** code
**Where:** listing `simple_meta1.py` (line ~578)
**Problem:** the trailing `1` on both names, and on the filename, implies a numbered series that does not exist anywhere in the chapter or the book. A reader looks for `SimpleMeta2` and finds nothing.
**Proposal:** rename to `SimpleMeta` / `Simple` and the file to `simple_meta.py`.
**Cost:** the filename change means `Examples/17_Metaprogramming/simple_meta1.py` becomes orphaned and needs `make prune-examples` after the sync. Nothing else in `Chapters/`, `Solutions/`, or `tools/data/norun.txt` mentions it (checked). Proposal 10 quotes `Simple1` and would need the same rename.

---

## 20. The C++ footnote's `instance()` is private

**Kind:** code
**Where:** footnote `[^crtp]` (line ~1341)
**Problem:** in the CRTP snippet, `instance()` is a member of a `class`, so it is private by default and no caller outside the hierarchy could reach it. The footnote is illustrative and nothing compiles it, but a C++ reader will stop on it, which is a distraction in a footnote whose job is to explain a language difference.
**Proposal:** add `public:` above `static T& instance()`.
**Cost:** none; the block is a fenced `cpp` listing that no gate extracts.

---

## Already fixed directly (no decision needed)

Nothing. Every listing ran clean, every `#:` marker matched real stdout, every cross-reference resolved to the heading it names, every version-dependent claim re-verified on the pinned 3.15.0b4, and no banned phrase from `tools/data/banned_phrases.txt` or the "Don't use" tier of the watch list appears. The one hit for "spelling" (footnote `[^parametrize]`, line ~1373) is the literal meaning of the word, which the rule exempts.
