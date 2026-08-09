When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter-level: the chapter's summary paragraph lands one section before the
end.**

"Three walkers over one set of nodes is the pattern pair in full ... Python
compresses the pair into frozen data classes, a union, operator methods that
build nodes, and `match` functions that walk them" reads as a chapter
conclusion, and then a whole further section follows it.

Having read it twice I do **not** think this should move, and I am recording
the finding mainly so a later review does not re-raise it. The paragraph
closes the three-walker arc, which genuinely completes there; "A Template Is a
Tree" is explicitly framed as an extension ("Python has a composite of its own
with no walker supplied"); and that section ends on the strongest sentence in
the chapter ("here it is a way to keep a decision available to whoever is
qualified to make it"), which a trailing summary would flatten.

If you disagree, the cheapest fix is not a move but a demotion: change the
first sentence to "Three walkers over one set of nodes is the pattern pair in
full for a nested grammar," which scopes it to the section and leaves the
t-string section room to generalize. Do not retitle or reorder the sections —
`02_Tour.md`, `33_Visitor.md`, `39_Pattern_Catalog.md`, and
`44_Effect_Management.md` all link to headings in this chapter by anchor.

---

[] Reject

**"Simplification Rewrites the Tree," `simplify.py`: `Num(0)` appears as a
pattern and as a constructor call two lines apart, with no acknowledgement.**

```python
case (Num(0), _) | (_, Num(0)):
    return Num(0)
```

Identical syntax, opposite direction: the first two `Num(0)`s destructure and
never call `Num`, the third constructs. [Class
Patterns](13_Pattern_Matching.md#class-patterns) teaches the class-pattern
form and shows the two uses on one page, so a reader who has it fresh is fine.
Twenty-one chapters later, this is the single densest spot in the book for the
confusion, and it costs one clause to defuse:

> A `Num(0)` on the left of a `case` is a pattern that never calls `Num`;
> the one on the right of `return` is the constructor.

I did not apply it because the chapter's silence here may be deliberate — 13
is a prerequisite and the book generally does not re-teach prerequisites.[[do it]]

---

[] Reject

**End of "Simplification Rewrites the Tree": the recursion limit names an
escape hatch and never shows it, and no exercise reaches for it.**

> A machine-generated chain of thousands of nested nodes does,
> and the escape is an iterative walk driving an explicit stack of pending
> nodes.

This is the one place in the chapter where a mechanism is named purely in
prose. It is also the only genuinely hard thing left for a reader who has
understood everything else, because an iterative `evaluate()` needs an
explicit post-order (push the node, push its children, then combine the two
results on the way back up) and a reader who tries the obvious pre-order stack
gets a walker that visits every node and computes nothing.

Confirmed on the pinned build: `sys.getrecursionlimit()` is 1000, so
"roughly a thousand frames" is right.

Proposed exercise 8:

> 8.  Build a left-deep expression by folding `+` over a few thousand `Num`
>     nodes and confirm that `evaluate()` raises `RecursionError`. Then write
>     `evaluate_iterative()`, which walks the same tree with an explicit stack
>     and no recursion, and check that the two agree on a small expression.
>     Raising `sys.setrecursionlimit()` is the other way out; say what it
>     costs.

Alternative, if a whole exercise is too much: add half a sentence naming the
post-order requirement, so the reader who tries it is not ambushed.

---

[] Reject

**Exercises: nothing exercises the chapter's own closing rule for section 2.**

"A Composite of Data Classes" ends on the sharpest piece of guidance in the
chapter — "Match over a closed set, use polymorphism for an open one" — and
seven exercises later, nothing has asked the reader to apply it. Exercise 2
comes closest but pushes the opposite way: it adds a type to a closed union
and admires the checker.

Proposed exercise:

> A plugin package wants to add its own entry types to `filesystem.py`
> without editing your code. Sketch what breaks, then write the version of
> `disk_usage()` that supports it. Which of the two designs would you ship
> for a file system, and which for the expression language in `expr.py`?

This is the one claim in the chapter a reader could repeat back without being
able to act on it.

Pricing the placement: it reads best right after exercise 2, since both work
on `filesystem.py`, but inserting it there renumbers 3 through 7, and the
chapter's own prose names one of them by number ("Exercise 6 closes the hole
with the declining-`NotImplemented` idiom"), as does the heading
`## 6. Declining with `NotImplemented`` in
`Solutions/34_Composite_and_Interpreter.md`. Appending it costs nothing and
breaks nothing, so append unless you are willing to fix both call sites. If
the recursion-limit exercise above is also taken, this one is 9 and that one
is 8.

---

[] Reject

**Across the two filesystem listings: three names change meaning between
`filesystem_classic.py` and `filesystem.py`, none of them remarked on.**

The two listings are meant to be read as before/after, and the numbers in
their output are deliberately identical (`1940 650 10`), which invites a
line-by-line comparison. Three things move underfoot during that comparison:

1.  `File.byte_count` becomes `File.size`.
2.  `Node.size()` (a method) becomes `disk_usage()` (a function), even though
    a field named `size` and a module-level function named `size` would not
    actually collide — the real reason is that `case File(_, size)` binds
    `size`, so a walker named `size` would be shadowed inside its own body.
3.  `Directory` changes call shape: `Directory("src", File(...), File(...))`
    in the classic version (`*entries: Node`) becomes
    `Directory("src", (File(...), File(...)))` in the data-class version
    (`entries: tuple[Node, ...]`).

Item 3 is the one that costs the reader something. The extra parentheses look
like a typo until you reach the immutability paragraph two pages later, and a
reader typing along from muscle memory writes the varargs form and gets a type
error the chapter never predicted.

Recommended fix: one sentence in the paragraph that already discusses the
tuple, moved up to just after the listing, e.g.

> `Directory` now takes its entries as one tuple rather than as varargs,
> which is what makes the tree immutable; the paragraph below says why a
> `list` would not do.

Alternative (cheaper, less useful): leave the code alone and add "note the
tuple" to the existing `entries` paragraph. I do not recommend renaming
anything back — `size` and `disk_usage` are both better names than what they
replaced.

---

[] Reject

**"A Composite of Data Classes," the lazy-alias paragraph: the cross-reference
points at a whole chapter.**

> `Node` is named in `Directory` before it is defined below,
> which works because annotations and `type` aliases are both evaluated lazily
> (see [Static Typing](08_Static_Typing.md)).

Every other cross-reference in this chapter names a section. This one names a
chapter of 640 lines, and a reader who follows it to check the claim has
nowhere to land: chapter 8 covers deferred evaluation only in one row of the
"Type Hint Summary" table, which itself forwards to
[Simulation](38_Simulation.md#a-robot-in-a-maze). The nearest thing to a
statement of the `type`-alias half is in
`Chapters/37_Pattern_Refactoring.md:78`.

Two options. I recommend the first.

- Point at the section that defines the construct being used, and let the
  laziness claim stand on its own:
  `(see [Naming Types: The `type` Statement](08_Static_Typing.md#the-type-statement))`.
- Drop the parenthetical entirely. The sentence is self-contained, and the
  link is currently doing no work.

There is a second-order item here that is not mine to fix: nowhere in the book
does a section actually *teach* PEP 649 deferred evaluation; four chapters
(8, 17, 34, 37) each assert it in passing. If that gap is ever closed, this is
one of the four call sites that should point at it.

---

[] Reject

**"The Classic Composite," `filesystem_classic.py`: three hand-written
`__init__()`s with no word about why.**

`Node`, `File`, and `Directory` each carry an `__init__()` that does nothing
but assign its parameters to fields, which is the exact shape
`thinking-in-python-skill.md` says to write as a `@dataclass`:

> A class whose `__init__()` only assigns parameters or defaults to fields is
> a `@dataclass` (frozen unless mutation is the point). Write the manual form
> only when the code is teaching it ... and then say why in an adjacent
> comment or prose: a deviation from this idiom is part of a lesson, never an
> accident.

Here it *is* part of a lesson — this is the Java/C++ translation the next
section replaces — but the prose only says "The traditional version puts the
operation in a class hierarchy," which explains the hierarchy, not the
constructors. A reader who has internalized the book's own rule reads three
constructors the book told them never to write.

Proposed change, one clause on the existing lead-in line:

> The traditional version puts the operation in a class hierarchy,
> hand-written constructors and all:

Cheap, and it turns an apparent lapse into a deliberate period piece.
(Making the classic version use dataclasses would be wrong: the point of the
listing is what a direct translation of the GoF diagram looks like.)

---

[] Reject

**"Evaluation Is a Tree Walk," `evaluate.py`: `#: True` is the least
informative line the demo could print.**

```python
    print(expr == by_hand)
#: True
```

The prose then has to carry the whole idea — "the demo confirms that the
operators build the tree you would assemble by hand" — because the output
shows a boolean and nothing about the tree. This is the mechanism-vs-outcome
test: a reader cannot narrate what `2 * x + 1` produced from the output alone.
They have to read `by_hand` in the source and trust the `True`.

`print(expr)` would be ideal but does not fit: the repr is 73 characters, so
the marker line is 76, over the 70-character limit that `#:` lines also have
to obey. This does:

```python
    print(expr == by_hand, expr.left)
#: True Mul(left=Num(value=2), right=Var(name='x'))
```

51 characters, and it shows the reader that `Add` really is holding a `Mul`,
which is the composite claim the whole chapter rests on. Reported rather than
applied because it changes an existing listing's output marker.

---

## Cross-chapter

[] Reject

**`Solutions/34_Composite_and_Interpreter.md`, exercise 6: the return
annotations contradict what chapter 32 teaches, in the same paragraph that
cites chapter 32.**

I checked both ends of the reflected-operator thread. Chapter 34's own prose
and exercise 6 agree with chapter 32 exactly: `expr.py` builds its nodes with
no `NotImplemented` guard, the chapter says so ("these reflected methods trust
their operand completely"), and exercise 6 sends the reader to
[One Type or Many](32_Multiple_Dispatching.md#one-type-or-many) for the idiom.
Nothing needs changing at the 32 end.

The solution is where the thread breaks. It writes all four operator methods
as `-> Any` and justifies it like this:

> The return annotations widen to `Any` for the reason
> [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)
> gives: the precise type is `Add | NotImplementedType`, and declaring
> that makes every downstream `.left` a checker error, even though the
> sentinel never reaches a caller.

Chapter 32 gives the first half of that and then explicitly rules out the
conclusion:

> Both methods declare `-> Meters` even though each can return
> `NotImplemented`, and that is the standard convention rather than a
> shortcut. ... Spelling the union out, `Meters | NotImplementedType`, makes a
> checker reject `(Meters(1) + Meters(2)).n` ... Widening the return to `Any`
> describes nothing at all and turns off checking for every caller.

`radd_dispatch.py` declares `-> Meters`, not `-> Any`, and it works because
`NotImplemented`'s type inherits `Any`, so the sentinel satisfies any declared
return type. A reader who does exercise 6 by following the chapter 32 idiom
writes `-> Add` / `-> Mul`, then finds the answer key doing the thing that
chapter called out by name.

I verified the correct version rather than assuming it. Taking the solution's
`exercise_6.py` verbatim and changing only the four annotations to `-> Add`,
`-> Add`, `-> Mul`, `-> Mul`: `ty` 0.0.65 reports "All checks passed!" and the
listing produces byte-identical output —

```
Add Num(value=1)
TypeError can only concatenate str (not "Var") to str
```

Change I would make in `Solutions/34_Composite_and_Interpreter.md`: swap the
four `-> Any` annotations for the concrete types, drop the now-unused
`from typing import Any`, and replace the justification paragraph with
something like

> Each method still declares the node type it builds. Returning
> `NotImplemented` from a function annotated `-> Add` type-checks, because
> the sentinel's type inherits `Any`;
> [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)
> explains why that convention beats both spelling out
> `Add | NotImplementedType` and widening to `Any`.

I did not touch `Solutions/`, per the scope rules.

---

[] Reject

**MANIFEST — not a proposal. Everything already applied to
`Chapters/34_Composite_and_Interpreter.md` in this pass, so you can find it in
the diff.**

- "Interpreter," `Operators`-vs-`Expr` paragraph: "which need the union to
  know when they are done" → "which need the union to know they have covered
  every case." ("Done" read as "finished traversing," which is the wrong
  reading in a section about recursive walkers.)
- "Interpreter," new final paragraph after the SymPy/Pandas/SQLAlchemy
  paragraph: the limits of operator overloading as a parser. `and`, `or`, and
  `not` cannot be overloaded, so `x and y` silently evaluates to `y` and
  builds no node; boolean expression languages borrow `&` and `|`; and `&`
  binds tighter than `>`, which is why the parentheses in a Pandas filter are
  load-bearing. All three verified on the pinned build (`x and y` returns
  `Var(name='y')`, `not x` returns `False`, and `ast.parse("a > 1 & b > 2")`
  gives `a > (1 & b) > 2`). This is the near-miss a reader who has met SymPy
  or Pandas is most likely to write.
- `test_evaluate.py`: added `test_e_is_available_as_a_variable()`, which
  exercises the positional-only `/` claim the prose makes and nothing checked.
- "Simplification Rewrites the Tree," new paragraph after the
  `(Num(a), Num(b))` sentence: why the rules match the pair of *simplified*
  children instead of the original node, using the demo's own
  `(1 * x) + (0 * y)` as the case that a top-level `case Add(Num(0), other)`
  would miss.
- `test_simplify.py`: added `test_unchanged_subtrees_are_shared()`, an `is`
  assertion for the structural-sharing claim, which until now appeared only in
  prose.
- "A Template Is a Tree," lead-in paragraph: added that iterating a `Template`
  produces `str | Interpolation` and that the `else` branch is the `str` case,
  so the chapter's one `isinstance` walker no longer looks like a lapse from
  its own `match`/`assert_never` idiom. (Confirmed with `reveal_type`: `ty`
  narrows the `else` branch to `str`.)

Gates after these edits: `validate_output.py` 1 ok / 0 failed with no marker
rewrites, `ruff` clean, `ty` clean, 19 tests passing (was 17),
`heading_links.py` and `banned_phrases.py` clean.
