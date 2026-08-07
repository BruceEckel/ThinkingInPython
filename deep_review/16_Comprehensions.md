When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

## Verification notes (not a finding)

`ty` here is 0.0.65, newer than the 0.0.63 CLAUDE.md's notes were written
against. The `filter(lambda ...)` story still holds exactly as recorded:
deleting the two `# type: ignore` comments in `mapping.py` and
`map_and_filter.py` reproduces two `unsupported-operator` errors
(`Has type int | str`), so both comments are still load-bearing. The prose
claim that a named function annotated `-> TypeIs[int]` does narrow was probed
and confirmed (`reveal_type` gives `list[int]`); a named function returning
plain `bool` does not (`list[int | str]`).

Every gate passes: extract sync, `validate_output`, `ty`, `ruff`, `pytest`,
`run_examples` (22/22), `heading_links`, `banned_phrases`, `codespell`,
`reflow_prose`. No timing markers exist in this chapter, so nothing here was
at risk from the shared-CPU environment.

Both listings proposed below (`flatten.py`, `genexp_timing.py`) were written
into `build/examples/16_Comprehensions/`, run, and checked with `ty` and
`ruff` before being proposed; their `#:` markers below are the real output.

---

[] Reject

**Section: List Comprehensions, line 27.**
"Select the integers from a mixed list and square them." is a task statement
that the listing immediately below does not carry out: `a_list.py` is just the
data. Line 35 then says the same thing again, correctly, right above the
listing that does it ("The list comprehension selects integers from the list
and squares them"). The first sentence is a leftover.

Proposed change: delete line 27, leaving the paragraph as "Several examples in
this chapter use the same input list:".

[] Reject

**Section: List Comprehensions, line 91.**
"The nested form funnels every element through `lambda` calls" uses "nested"
for `map(..., filter(...))`. Two sections later the chapter gives "nested" a
precise and different technical meaning: "Nesting one comprehension inside
another builds a list of lists." Two other uses of "nested" for the flattening
form were corrected in this pass; this one was left because it is not wrong,
only overloaded.

Proposed change: "The `map()`/`filter()` form funnels every element through
`lambda` calls, and is harder to read."

[] Reject

**Section: List Comprehensions, lines 100-101.**
"`filter()` can narrow, but only when its predicate is a named function
annotated to return `TypeIs[int]` rather than `bool`." The "only when" is
slightly too strong: `filter(None, iterable)` also narrows, and it is a common
idiom. Probed under `ty` 0.0.65: `list(filter(None, [1, None, 2]))` reveals as
`list[int]`.

Proposed change: append one sentence rather than rewriting the existing one,
so the `TypeIs` point keeps its emphasis:
"`filter(None, items)` is the other narrowing form; it drops the falsy values
and the checker knows `None` is gone."

Alternative, if that feels like a detour this early in the chapter: leave the
text alone and accept the mild overstatement.

[] Reject

**Section: List Comprehensions, lines 55-93.**
The chapter's verdict on `map()`/`filter()` is unqualified: they are harder to
read, and the comprehension inlines the test and the expression. Chapter 40
(Functional Foundations, line ~275) states the nuance the reader needs and
this chapter never gives them: "`map()` and `filter()` earn their keep when
the function already exists: `map(str.strip, lines)` beats
`[line.strip() for line in lines]` because the name is the whole story." A
reader who only meets chapter 16 leaves believing `map()` is always the worse
choice.

Proposed change: after line 93 ("The comprehension inlines the test and the
expression."), add:
"`map()` and `filter()` do earn their keep when the function already exists,
`map(str.strip, lines)` rather than `[line.strip() for line in lines]`;
[Functional Foundations](40_Functional_Foundations.md) returns to the choice.
The `lambda` is what makes the versions above worse, not `map()` itself."

No change is needed in chapter 40; it already says this. The link is one-way
on purpose, since chapter 16 comes first.

[] Reject

**Section: List Comprehensions, lines 128-131 (the walrus paragraph).**
The paragraph presents the walrus as a plain exception to comprehension
scoping, with no boundaries. Two of them are hard errors a reader will hit
when they try it, both verified on this 3.15 build:

- In a class body it is a `SyntaxError`: "assignment expression within a
  comprehension cannot be used in a class body".
- Rebinding the iteration variable is a `SyntaxError`:
  `[(n := n + 1) for n in range(3)]` gives "assignment expression cannot
  rebind comprehension iteration variable 'n'".

Proposed change: add one sentence to the end of that paragraph:
"Two things it cannot do: rebind the comprehension's own iteration variable,
and appear in a comprehension inside a class body. Both are a `SyntaxError`."

[] Reject

**Section: Nested Comprehensions, and Feeding the Iterator Clause.**
The chapter now states that "Writing two `for` clauses in one comprehension
flattens instead" and gives an inline example, but the first *listing* of the
form is inside `path_walk_comprehension.py`, which introduces
`tempfile.TemporaryDirectory`, `Path.mkdir`, `write_text`, `Path.walk`,
`relative_to`, `as_posix`, and a filter on the innermost clause all at once.
That is a lot of unfamiliar machinery wrapped around the one construct being
introduced, and it breaks "one new thing per listing".

Proposed change: add a three-line listing at the end of Nested Comprehensions,
immediately after the two-`for` paragraph, so the form is seen bare before it
is seen applied:

```python
# flatten.py
rows = [[1, 2], [3, 4], [5]]
print([x for row in rows for x in row])
#: [1, 2, 3, 4, 5]
```

`rows` deliberately matches the `rows` in `unpacking_comprehensions.py`, so
the PEP 798 section later reads as a direct rewrite of a listing the reader
already met. `path_walk_comprehension.py` then stays where it is and keeps its
role as the realistic application.

Cost: one more listing (the chapter has 22), and the sentence
"`[x for row in matrix for x in row]` turns the identity matrix into 36
numbers" would become redundant and should be dropped when the listing lands.

[] Reject

**Section: Feeding the Iterator Clause, line 269.**
"Unpack a tuple in the iterator, here a `(name, function)` pair applied to a
value". The unpacking happens in the `for` clause's target, not in the
iterator; the iterator is `zip(all_slots, values)`, and it is not what gets
unpacked.

Proposed change: "Unpack a tuple in the `for` clause's target, here a
`(name, function)` pair applied to a value:"

[] Reject

**Section: Feeding the Iterator Clause, `zip_unpack.py`.**
Two small things in one listing.

First, `values = [10, 3, 42]` against a two-element `all_slots`, so `42` is
silently dropped and never appears in the output. That is the exact behavior
the paragraph two listings earlier warns about, but nothing connects them, and
a reader who counts the inputs against the outputs is left to guess whether it
was deliberate.

Second, `all_slots` is a misleading name in a Python book: `slots` reads as
`__slots__` / `dataclass(slots=True)`, which this listing has nothing to do
with. It is a list of named operations.

Proposed change: rename `all_slots` to `operations` in the listing (and in the
`for (name, f), v in zip(operations, values)` line), and add one sentence
after the listing:
"`values` has a third element, and `zip()` drops it, exactly as above."

[] Reject

**Section: Feeding the Iterator Clause, `path_walk_comprehension.py`,
lines ~322-330.**
The chapter carefully explains why the eager list is safe here: "The
comprehension finished building `py_paths` as strings while the directory
still existed, so nothing later needs the files." That is the setup for a
near-miss it never delivers. Change `[...]` to `(...)` and the listing breaks:
the generator would not start walking until `sorted()` pulls it, by which
point `TemporaryDirectory` has deleted the tree. This is the strongest
motivation in the chapter for *not* defaulting to laziness by reflex, and it
sits three sections before Generator Expressions, where the reader would use
it.

Proposed change: add one sentence at the end of that paragraph:
"Turning those brackets into parentheses would break it: a generator
expression would not walk the tree until `sorted()` pulled on it, and by then
the directory is gone. [Generator Expressions](#generator-expressions)
returns to this."

[] Reject

**Section: Comprehensions Build, Loops Execute, lines 430-434.**
Three consecutive sentences take `wasted` as their subject, and the first says
something a name cannot do ("`wasted` runs `print()` for its side effect" —
the comprehension runs it). The last line, "not a loop wearing a disguise", is
a metaphor where a literal statement would do.

Proposed change:
"The comprehension calls `print()` for its side effect.
`print()` returns `None`, so `wasted` ends up holding three `None`s, a list
built only to be thrown away.
Worse, a reader scanning `[...]` expects a meaningful collection, and this is
a loop written with the wrong punctuation."

[] Reject

**Section: Generator Expressions.**
The section teaches that a generator expression defers its work, but never
says which part is *not* deferred: the outermost iterable is evaluated
immediately, when the generator expression is created. Everything else,
including the output expression and any later `for`/`if` clause, is deferred
until consumption. Verified on this build: `(x for x in src())` calls `src()`
at creation, while `(x * factor for x in [1, 2, 3])` picks up whatever
`factor` holds at consumption time.

This is the mechanism behind two bugs readers actually write: passing a
generator expression over a resource that is closed before consumption (see
the `path_walk_comprehension.py` finding above), and building a generator
expression in a loop that closes over the loop variable.

Proposed change: add a listing after `spent_generator.py`, before the
cross-reference paragraph:

```python
# genexp_timing.py
def source() -> list[int]:
    print("source() called")
    return [1, 2, 3]

factor = 2
gen = (n * factor for n in source())
#: source() called
print("generator created")
#: generator created
factor = 10
print(list(gen))
#: [10, 20, 30]
```

with prose: "Creating the generator expression evaluates only the outermost
iterable, so `source()` runs immediately. The output expression waits, so
`factor` is read when `list()` pulls the values, not when the generator was
written. A list comprehension has no such gap: it reads everything at once."

Alternative, if a listing is too much here: two sentences of prose stating the
rule, with no example. I recommend the listing, because the rule sounds like a
detail until you watch `source()` print before `list()` runs.

[] Reject

**Section: Unpacking in Comprehensions, `unpacking_comprehensions.py`,
lines 566, 570, 574.**
The three comments (`# * splices each iterable into the result:`,
`# ** merges each mapping. Later keys win, order preserved:`,
`# The same syntax works in a generator expression:`) each narrate the line
below them, which the house style rules out ("Never narrate what the next
line does"; new descriptions belong in prose). The prose after the listing
already carries all three points. Raising it because the style audit is
supposed to catch exactly this, not because the listing reads badly: the
comments do work as labels for three parallel cases.

Proposed change: either leave them (they are labels for parallel variants,
which is the defensible reading) or cut them to bare labels: `# *`, `# **`,
`# In a generator expression`. I lean toward leaving them.

[] Reject

**Section: Exercises.**
Exercises 3, 4, and 5 are all "predict the output before running it," three in
a row, and together with 1 and 2 the set leaves three of the chapter's claims
untested:

- set comprehensions (the whole section has no exercise)
- the comprehension-versus-loop rule from "Comprehensions Build, Loops
  Execute", which is one of the chapter's few pieces of actual advice
- breaking up a dense comprehension, which is the chapter's other piece of
  advice and the one a reader is most likely to need at work

Exercise 4 is also nearly a duplicate of the reasoning in exercise 3, and its
answer is mechanical once you know the generator's position.

Proposed change: replace exercises 4 and 5 with:

4.  In `set_comprehension.py`, change the filter to keep names of any length,
    and predict how many entries `unique` holds before running it. Explain
    why `"J"` does not collide with `"JOHN"`.
5.  `comprehension_side_effects.py` builds a list of `None`s. Write a version
    that keeps the printing but produces a list the caller would actually
    want, then say whether a comprehension or a `for` loop is the right shape
    for it.

and keep the PEP 798 prediction as a sixth exercise rather than dropping it,
since it is the only exercise touching the newest material.

Cost: `Solutions/16_Comprehensions.md` would need matching solutions for the
two replacements, and its existing solutions 4 and 5 would move or go.

## Cross-chapter

No changes are proposed in any other chapter. The one adjacent item, chapter
40's `map()`/`filter()` rule of thumb, is already correct where it stands; the
proposed fix is a forward link added in this chapter (see the finding at lines
55-93). `Solutions/16_Comprehensions.md` is consistent with the chapter as it
now stands, including the term "conditional expression", which this pass
introduced into the chapter itself and which solution 2 was already using.
