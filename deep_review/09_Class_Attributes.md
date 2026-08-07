[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

Notes on what was already applied (not repeated as findings below, listed so
you can find the hunks in the diff):

- Line 43: `vars()` is now named at first use ("`vars(obj)` returns that
  dictionary"). It was the first use of `vars()` in the book.
- Lines 64-69: new paragraph noting `@property` is the exception to both
  halves of the lookup rule. Verified: for a data descriptor, reading calls
  the getter even when the instance `__dict__` holds the name, and assigning
  calls the setter without touching the instance `__dict__`.
- Lines 104-105: the mutable-default deferral now points at this chapter's
  own "Real Per-Object Defaults" first, then at chapter 12.
- Lines 193-199: "`ClassVar` is a hint for the checker, **not the runtime**"
  was wrong-by-omission; `@dataclass` reads `ClassVar` at runtime and
  excludes the field from the generated `__init__()` (chapter 12's `D`).
  Reworded, with a link to that section.
- Line 201: "It does not catch every form of it" had two pronouns with two
  possible referents each, worse after the paragraph above. Now
  "`ClassVar` does not catch every form of shadowing".
- Lines 273-276: new sentences connecting subclass shadowing to instance
  shadowing (the same rule one level up).
- Line 313: **"here it is a default argument, evaluated per call" was wrong**
  and directly contradicted chapter 5 ("Python evaluates a default value
  once, at function definition") and the house style rule about mutable
  defaults. Rewritten, with a link to chapter 5 and a sentence saying a
  mutable default argument brings the sharing straight back.
- Lines 321-326: "`@dataclass` reads the class-attribute declarations" was
  loose. It reads the *annotated* ones. Added the near-miss: `x = 100` with
  no `x: int` in a `@dataclass` body produces no field, no constructor
  parameter, and no complaint from runtime or `ty`. Verified both.

---

[] Reject

**Line 3 and lines 13-16, opening: the C++/Java comparison never names the
construct that actually corresponds.**

The chapter is pitched at C++/Java programmers and tells them a class-body
field is *not* what they expect, but never says what it *is* in their terms.
Chapter 7 already does the mapping ("If you assign to a name in the class
body, C++/Java style, that name becomes a class-level field instead (similar
to a static field in C++/Java)"), so the reader who came through chapter 7
has it and the reader who opened here does not.

Proposed change, after line 16:

> A Python class attribute is the equivalent of a C++ or Java `static` field.
> Python has no syntax for declaring a per-object field in the class body;
> per-object storage comes from assigning through `self` inside a method.

Reasoning: it converts a warning ("this is not what you think") into a
translation ("this is the other thing you already know"), which is cheaper to
remember. Left unimplemented because it changes the chapter's opening beat.

---

[] Reject

**Lines 13, 14, 29, 40, 71, 95, 285, 294: "instance variable" is used only in
this chapter, and the chapter is titled "Class Attributes".**

`grep -c "instance variable" Chapters/*.md` returns hits in
`09_Class_Attributes.md` and nowhere else (8 lines). `"instance attribute"`
appears in no chapter at all. Chapter 7 says "object field"; chapter 12 says
"field". So the whole book avoids the term except here, and here it is paired
with "class attribute" in the same sentences, which reads as if the two were
different kinds of thing:

> Assigning through an instance always writes to the instance,
> creating the instance variable on first assignment.

Proposed change: replace all eight with "instance attribute", so the pair is
"class attribute" / "instance attribute" and the shadowing rule is symmetric
in its own vocabulary. The comment on line 29
(`# Assigning makes an instance variable on 'a'`) and line 294
(`# An instance variable, one per object`) are in listings, so they change
too.

Alternative, if "instance variable" is deliberate for the C++/Java audience:
keep it, but say once at first use that Python's own name for it is an
instance attribute. Recommend the first.

Note that `Solutions/09_Class_Attributes.md` already mixes both terms
(lines 19, 22, 111 say "instance attribute"; line 79 says "instance
variable"), so whichever you pick, that file needs the same pass. See
Cross-chapter below.

---

[] Reject

**Lines 37-44 and the `inside_objects.py` listing: `vars()` on a class returns
a `mappingproxy`, and the listing quietly avoids showing it.**

`vars(a)` is printed bare (`{}`, then `{'x': 1}`) but `vars(A)` is only ever
subscripted, `vars(A)["x"]`. That is the right choice for the output, but a
reader following along will type `vars(A)` and get
`mappingproxy({'__module__': ..., '__firstlineno__': ..., 'x': 100, ...})`,
which looks nothing like the instance case and includes several dunders that
have not been introduced.

Proposed change, one sentence after the listing:

> `vars(A)` is subscripted here because a class's dictionary is a read-only
> `mappingproxy` carrying the compiler's own bookkeeping alongside `x`;
> the instance dictionary is a plain `dict` holding only what was assigned.

Reasoning: the asymmetry in the listing is deliberate and currently
unexplained, which is the kind of thing a careful reader stops on.

---

[] Reject

**Section 1, after `inside_objects.py`: methods are class attributes too, and
the chapter never says so.**

This is the largest teaching gap in the chapter. The fallback rule the chapter
teaches (instance dict first, then class dict) is exactly how every method
call the reader has made since chapter 7 has been resolved. Saying that once
converts the chapter from "a gotcha about shared values" into "the attribute
model of the language", at the cost of two sentences. It also explains the
`[Methods]` half of the `display_object()` output in `class_var.py`, which the
prose currently walks past.

Proposed change, after the `inside_objects.py` discussion:

> A method is a class attribute like any other. `def show(self):` in a class
> body stores a function object in the class dictionary, and `a.show()` finds
> it by the same fallback that found `a.x`: nothing on the instance, so look
> at the class. That is why `display_object()` reports attributes and methods
> separately even though both live in the same dictionary, and why assigning
> `a.show = something` would shadow the method for `a` alone.

Left unimplemented because it adds a paragraph to a section that is already
carrying the chapter's main argument, and you may prefer it in chapter 7.

---

[] Reject

**Lines 71-73: "makes the 'default' value seem different" is vague twice
over.**

> A class attribute seems like a default until someone assigns to an instance
> variable of the same name.
> Changing the class attribute makes the "default" value seem different for
> every object that has not shadowed it.
> This produces bugs that surface far from their cause.

The second sentence says "seem different" where it means "change", and
"different" from what is never stated. Proposed replacement:

> A class attribute reads like a default right up until someone assigns to an
> attribute of the same name on one instance.
> After that, changing the class attribute changes the value for every object
> that has not shadowed it, and leaves the one that has behind.
> The bug surfaces far from the line that caused it.

---

[] Reject

**Lines 99-101: "Reading is the dangerous half" is a flourish standing in for
the literal point.**

> Reading is the dangerous half:
> an attribute read that ends in a method call can change shared state,
> and the shadowing rule offers no protection.

"an attribute read that ends in a method call" is doing a lot of work for a
phrase that never names the thing. Proposed replacement:

> Reading is the half with no protection.
> `a.items` is a read, so it reaches the shared list, and `.append()` then
> mutates the object every instance is reading.
> Only assignment makes an instance its own copy, and this line never
> assigns.

---

[] Reject

**Lines 170-191: the bare-annotation material is 22 lines of a different
topic sitting in the middle of the `ClassVar` argument.**

Section 2 runs 109-233. Its argument is: declare shared state with
`ClassVar`, and here is the one shadowing form `ClassVar` still misses
(`counter_near_miss.py`). Between the setup and that payoff sit three
paragraphs about what a bare annotation is, whether it is required, and where
in chapter 38 it becomes mandatory. That material is correct and belongs in
this chapter (an annotated name with no value is a class-body fact), but a
reader tracking the `ClassVar` thread has to hold it for 22 lines.

Proposed change: give lines 170-191 a `###` subheading, e.g.

> ### A Bare Annotation Declares, It Does Not Create

Cost of the move, checked: nothing in `Chapters/` or `Solutions/` links to a
sub-anchor in section 2, so a new `###` breaks no links. It would give
`Chapters/12_Data_Classes_as_Types.md:302` a better target than the one it
currently uses (see Cross-chapter below). If you would rather not add a
heading, the cheaper version is to move the two paragraphs at 183-191 (is the
annotation required, and the chapter-38 pointer) to just before line 227
("Shared storage is not a mistake..."), which restores the
setup/near-miss adjacency and keeps the digression as an aside.

---

[] Reject

**Line 229: "a constant that all instances read but none change" raises the
`Final` vs `ClassVar` question and does not answer it.**

Chapter 8's type-hint summary lists `Final` and `ClassVar` in the same table
section, "Constants and class variables", and points at this chapter for
`ClassVar`. A reader who wants exactly what line 229 describes has two
plausible spellings and no guidance.

Verified under `ty` 0.0.65: `A: Final[int] = 5` in a class body type-checks,
stores `5` on the class, and is rejected on reassignment; `Final` and
`ClassVar` cannot be combined in one annotation.

Proposed change, after line 230:

> For the third of these, a class-level constant, `Final[int]` says more than
> `ClassVar[int]`: it declares the value shared *and* not reassignable. Use
> `ClassVar` when the shared value is meant to change, as `Tally.total` is.

Reasoning: the chapter itself names the three cases, so answering the second
question it raises costs three lines.

---

[] Reject

**Line 143: the commented-out `ty` error does not match what `ty` prints.**

```python
# a.total = 99  # ty: cannot assign ClassVar "total" via instance
```

The actual 0.0.65 diagnostic is

```
error[invalid-attribute-access]: Cannot assign to ClassVar `total` from an
instance of type `Tally`
```

Proposed change: match the real wording, shortened to fit 70 columns:

```python
# a.total = 99  # ty: Cannot assign to ClassVar `total`
```

Also worth knowing: because the line is commented out, nothing in the gate
verifies the claim, so it can go stale on a `ty` upgrade with nothing
noticing. Uncommenting it and adding `# type: ignore[invalid-attribute-access]`
would make the gate fail if `ty` ever stops flagging it, at the cost of a
noisier listing. Recommend just fixing the wording.

---

[] Reject

**Lines 321-332: consider a listing for the unannotated-`@dataclass` trap.**

The prose fix applied at 322-326 states the trap; a three-line listing would
show it. Verified: `@dataclass class B: x = 100` produces `fields(B) == ()`,
`vars(B()) == {}`, `B().x` is `100` read from the class, `b.x = -1` shadows,
and both the runtime and `ty` are silent.

If you want it:

````markdown
```python
# dataclass_no_annotation.py
from dataclasses import dataclass, fields

@dataclass
class B:
    x = 100  # No annotation, so not a field

print(fields(B))
#: ()
b = B()
print(vars(b), b.x)
#: {} 100
b.x = -1
print(vars(b), B().x)  # Same shadowing as Stars
#: {'x': -1} 100
```
````

Left unimplemented because it is a fourth listing in a section that already
has the contrast it needs, and "the reader should be told, not shown" is a
reasonable call here.

---

[] Reject

**Lines 227-233: the chapter's thesis sentence sits three sections before the
end.**

> The bug is not the class attribute;
> it is writing one where you meant a per-object default.

That is the chapter's claim in one sentence, and it currently closes section
2. Sections 3 and 4 follow, and the chapter then stops on the mechanics of
`@dataclass`-generated `__init__()` plus a pointer to chapter 12. Chapters 8
and 10 both end on a titled closing insight ("How Much to Annotate", "The
Rule"), so a short closer is in character for this part of the book.

Proposed change: keep line 232-233 where it is, and add a two-or-three
sentence close after line 334, along the lines of:

> Every attribute question reduces to "which dictionary
> did the value land in?" Assignment answers it, and assignment through `self`
> and assignment through the class name give different answers. Decide which
> you want, then write the spelling that says so: `ClassVar` for shared,
> a constructor default or a `@dataclass` field for per-object.

A heading for it (`## Which Dictionary?`) is optional; without one it reads as
a closing paragraph of section 4.

---

[] Reject

**Exercises (lines 336-363): nothing exercises `counter_near_miss.py`, the
chapter's sharpest lesson.**

The six exercises map to `class_attribute_confusion.py`, `class_var_inheritance.py`,
`real_defaults.py`, `class_var.py`, `shared_mutable.py`, and
`inside_objects.py`. `counter_near_miss.py` is the only listing with no
exercise, and it carries the one mistake the chapter says you are most likely
to make and the checker misses.

Proposed new exercise:

> 7.  In `counter_near_miss.py`, print `vars(a)` and `vars(Tally)["total"]`
>     after constructing both instances, and use them to explain the `1 1 0`
>     output. Then fix the class so the counter actually counts, without
>     changing the `ClassVar` declaration, and say why `ty` accepted the
>     broken version.

---

[] Reject

**Exercises: nothing combines the mutable-value trap with inheritance.**

Sections 1 and 3 teach the two halves and never meet. `Base.shared` as a list,
mutated through `Left`, is the composition, and it is a real bug pattern (a
registry on a base class that every subclass silently shares).

Proposed new exercise:

> 8.  Change `class_var_inheritance.py` so `shared` is
>     `ClassVar[list[int]] = []` and `Left` and `Right` both call
>     `.append()` on it. Predict what `Base.shared` holds afterwards, then
>     check. Give `Right` its own list with `shared = []` in its body and
>     repeat.

---

## Cross-chapter

These need changes in files this review is not allowed to touch.

**`Chapters/08_Static_Typing.md`, line 565.** The `ClassVar[T]` row links to
`09_Class_Attributes.md#class-attributes-are-not-default-values`, which is
the section about plain class attributes and the shadowing bug; `ClassVar`
itself is not mentioned there. Change the target to
`09_Class_Attributes.md#declaring-shared-state-with-classvar`. That anchor
exists today.

**`Chapters/12_Data_Classes_as_Types.md`, line 302.** "As
[Class Attributes](09_Class_Attributes.md#class-attributes-are-not-default-values)
puts it, a bare annotation is a declaration rather than a placeholder" points
at section 1, but the bare-annotation passage it is quoting is in section 2
(chapter 9 lines 170-181). Change the target to
`09_Class_Attributes.md#declaring-shared-state-with-classvar`, or, if the
`###` subheading proposed above is added, to that subheading's anchor.

**`Solutions/09_Class_Attributes.md`, exercise 3 (lines 61-84).** The exercise
says "create `b = B()` and assign `b.x = -1`. Then create a second instance,
`b2 = B()`". The solution creates both instances first and only then assigns:

```python
b = B()
b2 = B()
b.x = -1
```

That still passes, but it tests a weaker claim. The exercise's order (assign,
then construct) is the one that mirrors `print(a.x, A().x)` in
`real_defaults.py`, where the point is that a later construction is
unaffected. Swap the two lines so `b2 = B()` comes after `b.x = -1`. The
output and the explanatory prose are unchanged.

**`Solutions/09_Class_Attributes.md`, terminology.** Lines 19, 22 and 111 say
"instance attribute"; line 79 says "instance variable". Whatever the chapter
settles on (see the terminology finding above), this file should match.
