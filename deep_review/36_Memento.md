[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

**Chapter-level, the biggest item: the intro promises the classic form "when
you need it" and the chapter never says when.**

The opening sets up a two-sided claim:

> Python offers the classic form when you need it,
> and obviates the pattern when state is immutable.

The chapter delivers one side in full.
"The Classic Memento" shows the copying form, "Immutability" dissolves it, and
every section after that (`History`, partial restore, pickle, git) builds on the
immutable form only.
`sketch.py` is never mentioned again after line 161 except as the thing exercise
1 and exercise 4 modify.
A reader who has a mutable state object they cannot freeze — a large NumPy
array, a GUI widget tree, an ORM row, a third-party object they do not own —
finishes the chapter with the classic form demonstrated but no statement of when
it is the right answer, and with a strong implied verdict that it is never the
right answer.

That verdict is not what the chapter means.
The honest answer is that freezing costs a full copy of the changed field on
every edit, so the classic form survives wherever the state is big enough that
copy-on-write is unaffordable, or wherever the object is not yours to redesign.

Proposed change: a short paragraph at the end of "Immutability", right after
"Memento shares them across time", something like

> The classic form has not disappeared, it has narrowed.
> Freezing rebuilds the changed field on every edit,
> so a state large enough that copying it per keystroke is unaffordable still
> wants a mutable originator and an explicit `save()`.
> So does a state you do not own: a widget tree, a database row, or any object
> whose class you cannot redesign.
> Everywhere else, prefer the frozen value.

Alternatives, in case you would rather not add to that section: put the same
three sentences in "Snapshots in the Wild" before the git paragraph, or fold a
clause into the intro's second paragraph so the promise names its own limit.
I recommend the first, because the reader asks the question the instant
`frozen_sketch.py` deletes `save()` and `restore()`, not two sections later.

Cost of the addition: nothing else moves, no anchors change, no listing changes.

[] Reject

---

**Chapter-level, order: the cost objection arises at `frozen_sketch.py`
(line 195) and is answered at line 339, one and a half sections later. The
answer is also asserted rather than shown.**

`frozen_sketch.py` makes a new `Sketch` per stroke.
The first thing a reader thinks is "so every keystroke allocates, and the
history keeps every allocation."
The chapter's answer is a single sentence at the very end of the `History`
section:

> Each `Sketch` above shares almost all of its strokes with its neighbors in
> the history.

That is 140 lines after the question, it is buried in a paragraph about the
Command alternative, and nothing demonstrates it.

Two problems, one fix each.

**The gap.** Either move the sharing sentence up to the paragraph under
`frozen_sketch.py` (it belongs next to "`after` shares the two original stroke
strings with `before`", which is the same fact stated smaller), or leave it and
add a forward pointer where the question arises. I recommend moving it, and
leaving the Command paragraph to be about Command.

**The assertion.** A listing would carry it. Draft, verified on the pinned
3.15 build (`ruff`, `ty`, and the markers all clean in `build/private/36`):

```python
# sharing.py
from frozen_sketch import Sketch

stroke = "".join(["cir", "cle"])
before = Sketch("Duck", (stroke,))
after = before.draw("beak")
print(after.strokes[0] is stroke)
#: True
print(after.strokes is before.strokes, len(after.strokes))
#: False 2
```

with prose along the lines of:

> The stroke strings are shared, the tuple holding them is not.
> Each `draw()` builds a fresh tuple of `n + 1` pointers and copies nothing
> else, so a history of `k` edits costs pointers, not `k` copies of the text.
> That is why snapshots stay cheap, and also why they are not free: a state
> whose changed field is large pays for that field on every edit.

Note on why `stroke` is built with `"".join([...])` rather than written as the
literal `"circle"`: a literal is interned at compile time, so the identity check
would print `True` whether the tuple shared the string or rebuilt it, and would
prove nothing. This is the same hazard as the small-int cache noted in
`CLAUDE.md` — an identity demo has to use a value the interpreter has not
already deduplicated. If this listing is added, keep the `"".join` and say why
in one clause, or the demo silently stops demonstrating.

Reported rather than applied because it adds a listing and decides where it
goes.

[] Reject

---

**Lines 117-118: `frozen=True` does not stop the mistake the sentence
attributes to it.**

> In Python it is a convention,
> though freezing the memento means an honest mistake (mutating the snapshot)
> fails loudly.

Mutating the snapshot is impossible because `strokes` is a *tuple*.
What `frozen=True` stops is *rebinding* `checkpoint.strokes`.
The chapter gets this exactly right ten lines later — "`frozen=True` makes
reassigning `checkpoint.strokes` fail instead of silently succeeding. The tuple
inside was already immutable, but the attribute was not" — so the earlier
sentence contradicts the later one about which mechanism does which job.

Proposed change: make the parenthetical name the right mistake.

> though freezing the memento means an honest mistake, swapping the snapshot's
> strokes for different ones, fails loudly.

[] Reject

---

**"Mementos That Outlive the Process": the quieter half of the drift story is
prose-only, and it is the half that matters. Proposed listing (verified).**

The chapter now says (after this pass's correction) that deleting a field
loads with no error, leaves a ghost in `__dict__`, and produces an object that
compares equal to a correct one. The dangerous case is therefore the one with
no listing, while the case that at least fails loudly gets `pickle_drift.py`.

I verified all of it on the pinned 3.15 build and drafted the listing.
It needs one refactor first: move `SketchV2` out of `pickle_drift.py` into its
own module, so the two directions of drift share the same pair of versions.

```python
# sketch_v2.py
from dataclasses import dataclass

@dataclass(frozen=True)
class SketchV2:
    strokes: tuple[str, ...]
    title: str
```

`pickle_drift.py` then loses its inline class and gains an import:

```python
# pickle_drift.py
import pickle
import sketch_v1
from exceptions import ignore
from sketch_v1 import SketchV1
from sketch_v2 import SketchV2

blob = pickle.dumps(SketchV1(("circle", "beak")))
sketch_v1.SketchV1 = SketchV2  # type: ignore
restored = pickle.loads(blob)
print(restored.strokes)
#: ('circle', 'beak')
with ignore(AttributeError):
    print(restored.title)
#: AttributeError("'SketchV2' object has no attribute 'title'")
```

Output and markers are unchanged. The new listing then runs the same
substitution backwards:

```python
# ghost_field.py
import pickle
import sketch_v2
from sketch_v1 import SketchV1
from sketch_v2 import SketchV2

blob = pickle.dumps(SketchV2(("circle",), "Duck"))
sketch_v2.SketchV2 = SketchV1  # type: ignore
restored = pickle.loads(blob)
print(restored, restored.__dict__)
#: SketchV1(strokes=('circle',)) {'strokes': ('circle',), 'title': 'Duck'}
print(restored == SketchV1(("circle",)))
#: True
```

Verified: `ruff check` clean at width 70, `ty check` clean (the only escape is
the same `# type: ignore` on the module reassignment that `pickle_drift.py`
already carries), and the markers are exact and stable across runs.

The two prints are the whole lesson side by side. The `repr()` shows a
one-field object; the `__dict__` shows two entries; and the loaded object is
`==` to a `SketchV1` that never had a title, so nothing downstream can tell
them apart. It also hashes the same, which I confirmed but left out of the
listing to keep it to one point.

Placement: immediately after the "Drift in the other direction" paragraph, so
the paragraph describes the behavior and the listing shows it. Reported rather
than applied because it adds a listing, edits an existing one, and adds a file
to the chapter directory.

[] Reject

---

**"The Caretaker: a Generic History": the near-miss is forgetting `do()`, and
nothing warns about it.**

The demo reads `history.do(history.present.draw("circle"))`, which is a mouthful
and invites the shorter thing a reader will write:

```python
sketch = history.present
sketch = sketch.draw("circle")   # never recorded
```

With the classic mutable memento, forgetting to call `save()` costs you a
snapshot and the object still changes. With the immutable form the failure is
the other way round and quieter: the state changes only in the caller's local
name, and `history.present` is still the old one, so undo appears to work while
the drawing appears to vanish. That inversion is worth one sentence, and it is
the kind of thing only a chapter that has just switched idioms can point out.

Proposed sentence after "`undo()` and `redo()` just shuttle the present between
the two stacks":

> Every change must go through `do()`.
> A new state built from `history.present` and never handed back is simply not
> in the history, and since nothing mutated, nothing else shows it is missing.

An alternative worth considering instead of the sentence: give `History` an
`apply()` that takes a callable, `history.apply(lambda s: s.draw("circle"))`,
so the round trip cannot be broken. I would not add it to the class — it makes
`History` less obviously a pure store of states, which is the point of the
section — but it is a good exercise (see the exercises block below).

[] Reject

---

**Exercises: two sections have none, and the set clusters on the two `Sketch`
classes.**

Coverage as it stands: exercise 1 hits both sketches, 2 and 5 hit `History`,
3 hits serialization, 4 hits the aliasing bug. Nothing exercises "Restoring
Part of a State" — the only section whose technique (`copy.replace()` on a past
state) the reader would have to invent from scratch — and nothing exercises
pickle drift, which the chapter spends its longest stretch of prose on.

Proposed additions:

> 6.  A `History` of `Sketch` states records a rename and three strokes.
>     Write `restore_field(history, name, past)` that pushes a new state
>     taking one named field from `past` and the rest from `history.present`.
>     Why must it go through `do()` rather than editing `_past` directly?

> 7.  Save a `Sketch` with `pickle`, then add a field with a default to
>     `Sketch` and load the old bytes. Does the default appear? Now add a
>     `__post_init__()` that rejects an empty title, and load again. What did
>     pickle skip, and what would `copy.replace()` have caught?

Exercise 7 also closes the loop with
[Data Classes as Types](12_Data_Classes_as_Types.md#the-general-form-of-replace),
which forward-links to this chapter for exactly that question.

A third candidate, if you want one against `History`'s contract rather than its
mechanics: add `apply(fn)` (see the `do()` block above) and say what it buys and
what it costs.

[] Reject

---

**"A Snapshot Is Not a Reference": `nested_mutation.py` teaches
`copy.deepcopy()` and nothing in the chapter ever uses it.**

`deepcopy()` appears in that one listing, is explained well, and then never
returns. `Sketch.save()` uses `tuple(self.strokes)`, one level; `History`
stores whole immutable values; nothing else copies at all. By the deep-review
test — a section that could be cut with nothing downstream noticing — that
listing currently has no downstream.

It should not be cut, because the shallow/deep distinction is exactly the trap
the pattern exists around. It should be connected. Proposed one-sentence bridge
under `sketch.py`, after "rebuilding a fresh list so the sketch and the memento
never share one":

> One level is enough because a stroke is a string.
> An originator holding containers inside containers needs `copy.deepcopy()` in
> `save()`, at the cost the previous section showed.

That makes the earlier listing pay for itself and warns the reader whose state
is not flat.

[] Reject

---

**`sketch.py` and `frozen_sketch.py` both define a class named `Sketch`, with
different fields, and the chapter never says so.**

They are two different classes: `Sketch()` takes no arguments and holds a
`list`; `Sketch("Duck")` takes a title and holds a tuple. Both files sit in the
same extracted directory, `from sketch import Sketch` and
`from frozen_sketch import Sketch` are both live imports in this chapter, and
exercise 1 asks the reader to modify "both sketches", which is the only place
the duplication is acknowledged.

Related, and the reason the reuse costs something: `title` is a brand-new field
that `frozen_sketch.py` introduces silently. It does no work in that listing
(`Sketch("Duck")` could as easily be `Sketch()`), no work in `history.py`, and
only earns its keep in "Restoring Part of a State" 170 lines later, where a
second field is needed so one can be restored without the other. That is a
"one new thing per listing" split: the listing is teaching the frozen-value
idiom, and the reader has to also absorb an unmotivated field.

Two fixes, either is fine, I marginally prefer the first:

- Add half a sentence under `frozen_sketch.py`: "`title` is a second field so a
  later section can restore one field and keep the other." That costs one line
  and removes the puzzle.
- Rename the frozen class (`Drawing`, say) so the two are visibly different
  objects, and note in one clause that it is the same idea with the mutation
  removed. This costs edits to `frozen_sketch.py`, `test_frozen_sketch.py`,
  `history.py`'s demo, `partial_restore.py`, `round_trip.py`, exercise 1,
  exercise 3, and `Solutions/36_Memento.md`, so it is only worth it if the
  name collision bothers you independently. [[do this]]

[] Reject

---

**Line 120: the alias paragraph opens with a garden-path sentence, and skips
the near-miss a typed-Python reader would actually write.**

> A `type Memento = tuple[str, ...]` alias would type-check at every call site
> instead of the class.

"instead of the class" attaches to "call site" on the first reading, which is
not the meaning. Suggested rewrite:

> You could skip the class and write `type Memento = tuple[str, ...]`.
> Every call site would still type-check.

Second item in the same paragraph: the reader who knows the typing toolkit
does not stop at a `type` alias, they think of `NewType("Memento",
tuple[str, ...])`, which *is* nominal for the checker and is the obvious
counter to "an alias is structural, not nominal". The paragraph's argument
survives, but it has to be made, and it is the stronger version of the point:

> `NewType("Memento", tuple[str, ...])` answers the checker but nothing else.
> It vanishes at runtime, so the caretaker still holds a plain tuple it can
> index, unpack, or build from scratch.
> Wrapping the tuple in a one-field data class gives `Memento` an identity that
> exists while the program runs.

This also lines up with the book's own rule (`thinking-in-python-skill.md`:
prefer a frozen data class over `NewType`, because `NewType` only satisfies the
checker), so the chapter would be demonstrating a rule the skill states.

Minor, same paragraph: "an alias is *structural*, not *nominal*" is doing the
job but is slightly off — a `type` alias is not a structural type, it is a
transparent second name for the same type. "An alias creates no new type" is
the literal statement and needs no italics.

[] Reject

---

**Prose pass, five small items outside the blocks above.**

Each stands alone; reject individually by striking the line.

1.  Line 15, "and obviates the pattern when state is immutable."
    "Obviates" appears exactly once in the whole book and reads as inflated
    diction next to "Undo is a feature users expect and programmers dread."
    Suggest "and removes the need for it when state is immutable."

2.  Line 298, "That works for any state type, `int` to full `Sketch`, with one
    condition". Reads as a dropped word. Suggest "from `int` to a full
    `Sketch`".

3.  Line 301, "It is a stack of aliases, the bug with which this chapter
    opened." The pied-piped "with which" is out of character for the
    surrounding prose. Suggest "the bug this chapter opened with."

4.  Line 349, "The state has to answer it, / and `copy.replace()` is how any
    immutable value does:" The elliptical "does" leaves the verb two lines
    back. Suggest "and `copy.replace()` is how any immutable value answers it". [[yes and get rid of "answers it"]]

5.  Line 492, "When either limitation rules out `pickle`, there are open-source
    libraries." Vague, and it does not say which library answers which
    limitation. Suggest "When either limitation rules out `pickle`, other
    libraries answer them separately." followed by the existing sentences,
    which already do the pairing (`msgspec`/`pydantic` for drift, Protocol
    Buffers for drift across languages, all three for the security half).

[] Reject

---

## Cross-file (not touched, per the review's scope rules)

**`tools/validate_output.py`: a relative `--tree` silently breaks every block
that imports a sibling.**

Running

```
uv run python tools/validate_output.py --tree build/private/36 Chapters/36_Memento.md
```

fails with four `ModuleNotFoundError`s (`frozen_sketch`, `sketch_v1`) that have
nothing to do with the chapter. `run_location()` does
`sys.path.insert(0, str(rundir))` and then `os.chdir(rundir)`, so a relative
`rundir` stops resolving the moment the chdir happens. The default tree comes
from `tools_config.EXAMPLES_TREE` and is absolute, so this only bites when
`--tree` is passed by hand — which is exactly what a per-chapter or parallel
workflow does. Passing `--tree /tmp/tip/build/private/36` works.

`CLAUDE.md` already documents the identical trap for `run_examples.py`
("never pass a relative `--tree`"); this one is undocumented.

Change I would make in `tools/validate_output.py`: resolve the tree once in
`main()`, `args.tree = args.tree.resolve()`, which fixes it for every caller
rather than adding a second warning to `CLAUDE.md`. I did not touch the tool,
per the scope rules.

[] Reject

---

**MANIFEST — not a proposal. Everything this pass applied to
`Chapters/36_Memento.md`, so you can find it in the diff.**

1.  Line 159: "as in the variant exercise 4 explores" gained the missing
    relative pronoun, "as in the variant that exercise 4 explores".
2.  After line 203 ("This is the argument made by [Rethinking Objects]"):
    three new lines saying why `strokes` is a tuple and not a list, that
    `frozen=True` guards the binding rather than the object, and pointing at
    `frozen_leaky.py` in the section already linked. This closes the
    frozen-is-shallow thread from chapter 20, which the whole "Immutability"
    argument silently assumes.
3.  Line 417 (was 413): "What breaks is everything that touches the missing piece."
    became "What breaks is whatever later touches a field the bytes never
    carried." The old sentence claimed a break for the "loses a field" case
    listed one line above it, where nothing breaks.
4.  The "Drift in the other direction" paragraph was factually wrong and is
    rewritten. It conflated deleting a field with renaming one and then
    claimed "The removed-field drift never raises an exception," which is
    false for the rename half: the new name is absent, so touching it raises
    `AttributeError`, and even `repr()` raises. Verified both cases by running
    them on the pinned 3.15 build. The replacement separates the two, states
    what the delete case actually does (ghost in `__dict__`, invisible to
    `repr()` and `==`, equal and equal-hashing to a correctly built object),
    and gives the rename one sentence as "a delete and an add at once".
5.  Line 505: "Version control is the memento pattern at industrial scale"
    became "the Memento pattern", per the house rule that pattern names are
    capitalized as proper nouns.

Verified after the edits, with `UV_PYTHON=/opt/py315/python/bin/python3` and
the private tree `build/private/36`: `extract_examples.py --write -o`,
`validate_output.py --tree` (1 ok, 0 failed, no marker rewrites in
`git diff`), `ruff check` (clean at width 70), `ty check` (clean),
`pytest` (9 passed), `heading_links.py` (OK), `banned_phrases.py` (none), and
`reflow_prose.py --diff` (0 paragraphs, so the new prose is already on
semantic line breaks).

[] Reject
