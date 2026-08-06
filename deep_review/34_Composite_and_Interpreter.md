# Deep review: 34_Composite_and_Interpreter.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Explain why `expr.py` needs both a base class and a union

**Kind:** teaching
**Where:** section "Interpreter" (line ~242, the paragraph beginning "The four node classes are the grammar.")
**Problem:** `expr.py` is the first listing in the chapter that uses inheritance and a union at the same time, and it never says why. `Operators` is a base of all four node types but is deliberately *not* a member of `Expr`. A reader who just absorbed "Match over a closed set, use polymorphism for an open one" three pages earlier will read `class Num(Operators)` and ask whether the base class is now the type, why `type Expr = Num | Var | Add | Mul` repeats what the base class already groups, and what would break if `evaluate()` were annotated `e: Operators`. The answer is the chapter's own thesis reappearing in a sharper form, and it is left on the floor.

The consequence is concrete. `Expr` is what makes `assert_never()` work: a fifth subclass of `Operators` that never joins the union type-checks fine at its definition, and the walkers do not complain until something hands one to `evaluate()`. The union is the contract; the base class is only shared behavior.

**Proposal:** add a short paragraph after "The four node classes are the grammar. / An expression is a number, a variable, a sum, or a product. / `Add` and `Mul` hold expressions themselves, which makes it a composite." Suggested text:

```
`Operators` is a base class but not a member of `Expr`,
and the split is on purpose.
Every node shares the operator methods, so those live on a base and are inherited.
No node shares its meaning, so meaning lives in the walkers,
which need the union to know when they are done.
`Expr` is the contract: annotate `evaluate()` with `Operators`
and `assert_never()` stops working,
because a base class is an open set and any new subclass silently belongs to it.
```

**Cost:** none structurally; it adds four or five lines to the Interpreter section. It leans on "Match over a closed set, use polymorphism for an open one" from the previous section, which is already there, so nothing new has to be introduced.

---

## 2. State the or-pattern same-bindings rule where `simplify.py` first relies on it

**Kind:** teaching
**Where:** section "Simplification Rewrites the Tree" (line ~431, "The patterns read like the algebra they implement.")
**Problem:** `case (Num(0), other) | (other, Num(0)):` is doing three things the reader has not been shown. It matches on an ad-hoc tuple built for the `match`; it nests a class pattern inside a sequence pattern; and it captures a name inside an alternative. Confirmed by grep: chapter 13 never nests a pattern in any listing (its only nested example is exercise 3, unsolved in the text), and its "Alternatives and Capture" section shows alternatives without captures (`case "up" | "u"`) and a capture without alternatives (`case other`), never the two combined. This chapter is where they meet.

The chapter's one line about it, "with the alternatives binding the same name," reads as an observation about this particular code. It is a hard rule. Every alternative in a `|` must bind the identical set of names or the file will not compile:

```
>>> case (0, other) | (other2, 0):
SyntaxError: alternative patterns bind different names
```

A reader who writes `case (Num(0), left) | (right, Num(0)):` gets a `SyntaxError` at import time with no idea it was a language rule rather than a typo.

**Proposal:** replace the sentence "`(Num(0), other) | (other, Num(0))` says "zero on either side, / keep the other side," with the alternatives binding the same name." with:

```
`(Num(0), other) | (other, Num(0))` says "zero on either side,
keep the other side."
Both alternatives bind `other`, and they have to:
every alternative in a `|` must bind the same set of names,
so binding `left` in one and `right` in the other is a `SyntaxError`
rather than a runtime surprise
(see [Alternatives and Capture](13_Pattern_Matching.md#alternatives-and-capture)).
```

Alternatives, if the rule feels like too much detail for the flow: state it in one clause ("both alternatives bind `other`, which the language requires") and drop the `SyntaxError` sentence; or say nothing here and add an exercise that asks the reader to rename one binding and read the error.

**Cost:** none. Chapter 13's `#alternatives-and-capture` anchor exists and `heading_links.py` gates it. This does not require touching chapter 13.

---

## 3. Say what `self: Expr` is doing in `Operators`

**Kind:** teaching
**Where:** section "Interpreter", `expr.py` (line ~206) and the prose at line ~246
**Problem:** all four operator methods annotate `self` explicitly, which happens exactly one other time in the book (chapter 17's metaclass-injected `init`), and the reader has been taught `Self` as the annotation for this position in [The `Self` Return Type](08_Static_Typing.md#the-self-type). Nothing says why `Self` is wrong here or what the annotation buys. It is not decoration: dropping it produces two errors per method.

```
error[invalid-argument-type]: Argument is incorrect
  return Add(self, wrap(other))
             ^^^^ Expected `Expr`, found `Self@__add__`
```

`Self` at `Operators` means "some subclass of `Operators`," and the checker has no way to know that every subclass of `Operators` is in `Expr`. Writing `self: Expr` states it. This is the same "the base class is open, the union is closed" fact as proposal 1, seen from the type checker's side, so the two additions reinforce each other.

**Proposal:** add to the "The `Operators` base class is the clever part" paragraph, after "They build nodes.":

```
Annotating `self` as `Expr` rather than leaving it implicit is what lets
`Add(self, ...)` type-check.
`Self` would mean "some subclass of `Operators`,"
and the checker cannot know that every such subclass is in the `Expr` union.
The annotation says so.
```

(Reword the first line to avoid "is what": "Annotating `self` as `Expr` rather than leaving it implicit lets `Add(self, ...)` type-check.")

**Cost:** none. `Solutions/34` uses the same `self: Expr` form in four listings, so the explanation covers those too.

---

## 4. `evaluate()` cannot bind a variable named `e`

**Kind:** code
**Where:** section "Evaluation Is a Tree Walk", `evaluate.py` (line ~284)
**Problem:** `def evaluate(e: Expr, **env: int) -> int:` puts the tree parameter and the variable names in the same keyword namespace. In an arithmetic language, `e` is a plausible variable name, and it is the one name the function cannot accept:

```
>>> evaluate(Var("e"), e=5)
TypeError: evaluate() got multiple values for argument 'e'
```

The chapter presents `**env` as the environment with no caveat, and a reader adapting the code will hit this with a message that points at the wrong thing. (Reserved words are fine, incidentally: `evaluate(Var("class"), **{"class": 5})` returns `5`.)

**Proposal:** make the tree parameter positional-only:

```python
def evaluate(e: Expr, /, **env: int) -> int:
```

Verified: `evaluate(Var("e"), e=5)` returns `5`, and `ty` passes. Add one sentence to the paragraph after the listing, near "An unbound variable raises `KeyError`, naming the variable.":

```
The `/` makes the tree positional-only
(see [Positional-Only and Keyword-Only Parameters](05_Functions.md#positional-only-and-keyword-only-parameters)),
which keeps the parameter name `e` out of the variable namespace
so an expression can use `e` as a variable.
```

Alternatives: rename the parameter (`node`, `tree`) so the collision moves to a less likely name, which does not remove it; or replace `**env` with an explicit `env: dict[str, int]` mapping, which removes the collision entirely but costs the `evaluate(expr, x=3)` call style the demo and tests are built on.

**Cost:** `Solutions/34` defines `evaluate()` in exercise 3 and calls it in exercises 3 and 5; those need the same `/`. `test_evaluate.py` and both `__main__` demos call it positionally, so they are unaffected. Chapter 5's anchor already exists.

---

## 5. Solutions is missing exercise 6

**Kind:** exercise
**Where:** `Solutions/34_Composite_and_Interpreter.md`
**Problem:** the solutions file has sections 1, 2, 3, 4, 5, and 7. Exercise 6, the `NotImplemented` rewrite, has no solution. It is the exercise the chapter itself points at twice (line ~266, "Exercise 6 closes the hole with the declining-`NotImplemented` idiom," and again in the exercise text), so a reader following that thread finds nothing.

**Proposal:** write solution 6. It is a small listing: `__radd__`/`__rmul__` gain an `isinstance(other, int)` guard and return `NotImplemented` otherwise, with the return annotation widened. Verified behavior to reproduce: as the code stands, `"a" + x` builds `Add(left=Num(value='a'), right=Var(name='x'))` at runtime while `ty` flags the same line as `unsupported-operator` when it can see it, which is exactly the gap the exercise names.

**Cost:** I could not do this myself: this review is scoped to `Chapters/34` and `deep_review/34`, and `Solutions/` is off limits. Filing it so it does not get lost.

---

## 6. The two-pattern summary reads as the chapter's ending, one section early

**Kind:** structure
**Where:** end of section "Simplification Rewrites the Tree" (line ~476, "The full shape of the two patterns is now visible.")
**Problem:** that paragraph sums up the whole chapter (Composite is the data, Interpreter is the behavior, here is what Python compresses them into) and then tacks on the recursion-limit caveat. A whole section follows it. A reader arriving at "The full shape of the two patterns is now visible" reasonably stops there, and "A Template Is a Tree" then has to restart the chapter. The Template section ends with its own, better closing insight ("a way to keep a decision available to whoever is qualified to make it"), so the chapter currently has two endings and the weaker one comes first.

**Proposal:** keep the paragraph where it is but re-aim it at the `Expr` arc rather than the chapter, by replacing "The full shape of the two patterns is now visible." with something that closes the expression thread and does not sound terminal, for example "Three walkers over one set of nodes is the pattern pair in full." Then move nothing else.

Alternatives: split the recursion-limit sentences into their own short paragraph so the synthesis and the caveat stop sharing a breath; or leave it alone, on the grounds that the Template section is explicitly a coda and its opening line ("Python has a composite of its own with no walker supplied") signals that.

**Cost:** no anchors or cross-references touch this paragraph. Chapter 2 links to `#a-template-is-a-tree`, which this does not move or rename.

---

## 7. Make `simplify()` actually share unchanged subtrees

**Kind:** code
**Where:** section "Simplification Rewrites the Tree", `simplify.py` (lines ~406 and ~417, the two `case _:` branches)
**Problem:** the chapter claimed the returned tree "shares unchanged subtrees with the original," which is not what the code does. `case _: return Add(lhs, rhs)` builds a fresh node even when `lhs is left` and `rhs is right`, so only leaves are shared. I corrected the prose to match the code (see "Already fixed" below). The other direction is available and is arguably the better lesson, since structural sharing is the payoff frozen nodes exist for.

**Proposal:** add the identity guard to both `case _:` branches:

```python
                case _:
                    if lhs is left and rhs is right:
                        return e
                    return Add(lhs, rhs)
```

and restore the stronger prose claim: "It returns a new tree that shares unchanged subtrees with the original." Optionally show the sharing in the demo (`simplify(unchanged) is unchanged`).

Alternatives: leave the code alone and keep the corrected prose, which is what stands now. The guard adds two lines to each branch and a little noise to a listing whose current virtue is that every case is one line, so this is a real trade rather than a free win.

**Cost:** `Solutions/34` exercise 3 extends `simplify()` with `Neg` and `Div` cases and would want the same guard for consistency. `test_simplify.py` compares by value and passes either way.

---

## 8. Say why `entries` has to be a tuple

**Kind:** teaching
**Where:** section "A Composite of Data Classes" (line ~147)
**Problem:** "The `entries` field is a tuple of `Node`, so the whole tree is immutable." A reader who writes `entries: list[Node]` still gets a frozen dataclass that refuses attribute assignment, and will conclude the tuple was stylistic. It is not: `frozen=True` stops rebinding the field, not mutating what the field holds. The book demonstrates this in [Rethinking Objects](20_Rethinking_Objects.md) with `frozen_leaky.py`, and this chapter's immutability argument depends on that lesson without naming it.

**Proposal:** extend the sentence:

```
The `entries` field is a tuple of `Node`, so the whole tree is immutable.
A `list` there would not do:
`frozen=True` stops the field from being rebound, not the object it holds from being mutated,
which [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution) demonstrates.
```

Anchor verified: `frozen_leaky.py` sits in chapter 20's "The Immutability Solution" section, and other chapters already link that slug.

**Cost:** none. Reinforces an existing cross-chapter thread rather than opening a new one.

---

## 9. Note that the union alias is defined after the classes that use it

**Kind:** teaching
**Where:** `filesystem.py` (line ~90, `entries: tuple[Node, ...]` above `type Node = ...`) and `expr.py` (line ~228, `left: Expr` above `type Expr = ...`)
**Problem:** both listings annotate a field with a name defined lower down, with no quotes and no `from __future__ import annotations`. This is correct under PEP 649 plus PEP 695's lazy alias evaluation, and it is the natural way to write a recursive union, but it is the kind of thing that stops a reader cold: the obvious reading is that the file cannot possibly import. The book mentions deferred evaluation once, in chapter 8's reference table, pointing at chapter 38. This chapter uses it twice in its two central listings and says nothing.

**Proposal:** one sentence in the paragraph after `filesystem.py`, where the union is first introduced:

```
`Node` is named in `Directory` before it is defined below,
which works because annotations and `type` aliases are both evaluated lazily
(see [Static Typing](08_Static_Typing.md)).
```

Linked without a fragment on purpose: chapter 8's "Self and forward references" heading is raw HTML wrapping an external `href`, so it has no dependable slug. If a fragment is wanted, give that heading an explicit `{#id}` first.

**Cost:** none.

---

## 10. "adding a third costs nothing that already exists" is hard to parse

**Kind:** prose
**Where:** section "A Template Is a Tree" (line ~539)
**Problem:** the sentence reads as a garden path. "Costs nothing that already exists" wants to mean "requires no change to anything that already exists," and the compression loses the verb the reader needs.

**Proposal:** "and adding a third changes nothing that already exists."

**Cost:** none.

---

## 11. Point at Python's own `ast` module

**Kind:** teaching
**Where:** section "Interpreter" (line ~190, "A tree whose shape follows a grammar is an *abstract syntax tree* (AST).")
**Problem:** this is the only place in the book that defines "abstract syntax tree," and Python ships one, along with a Visitor for it. Grep confirms `ast`, `ast.NodeVisitor`, and `literal_eval` appear in no chapter. A reader who has just built four node classes and three walkers is one sentence away from knowing that `ast.parse()` hands them the same shape for real Python, and that `ast.NodeVisitor` is chapter 33's pattern in the standard library.

**Proposal:** one sentence after the "This technique is used in SymPy expressions..." paragraph:

```
Python's own compiler builds one of these for every source file,
and `ast.parse()` hands it to you as node objects
that `ast.NodeVisitor` walks in the style of [Visitor](33_Visitor.md).
```

**Cost:** none, but it does open a topic the book otherwise avoids, and the chapter is already long. Reject freely if the "language, not stdlib tour" line applies.

---

## 12. "already ... ever" in one sentence

**Kind:** prose
**Where:** section "Interpreter" (line ~255)
**Problem:** "Python has already parsed it, honoring precedence, / before the interpreter ever runs." Two watch-list words holding up one short claim. "Before the interpreter runs" already carries the "already."

**Proposal:** "Python has parsed it, honoring precedence, / before the interpreter runs."

**Cost:** none.

---

## 13. Iterating a `Template` skips empty literal pieces

**Kind:** teaching
**Where:** section "A Template Is a Tree" (line ~493)
**Problem:** "a sequence of two node kinds, the literal `str` pieces the author typed and the `Interpolation` objects holding the values" invites the reader to expect strict alternation. Iteration drops the empty strings:

```
>>> list(t"{a}{b}")
[Interpolation(1, 'a', None, ''), Interpolation(2, 'b', None, '')]
>>> t"{a}{b}".strings
('', '', '')
```

Neither walker in the listing cares, and neither does exercise 7, so nothing here is wrong. But a reader writing a walker that pairs each string with the interpolation after it will be surprised, and `.strings` and `.values` are the attributes that preserve the alternation.

**Proposal:** low priority. If it goes in, one clause: "Iteration skips the empty literal pieces, so `t"{a}{b}"` yields two `Interpolation` objects and no strings; `template.strings` keeps the empty slots when the alternation matters." Chapter 2's t-string section has the same gap, so the alternative is to put it there instead and leave this chapter alone.

**Cost:** none here; if it goes in chapter 2 instead, that is outside this review's scope.

---

## Already fixed directly (no decision needed)

- line ~142: "`walk()` is a generator, so a composite is also iterable" was wrong as written. A `Directory` is not iterable: `for e in root:` raises `TypeError: 'Directory' object is not iterable`, since nothing defines `__iter__`. What is iterable is the generator `walk()` returns. Changed to "`walk()` is a generator, so traversing a composite is lazy," which keeps the sentence's job of setting up the `yield from` line and the Iterators cross-reference.
- line ~436: "It returns a new tree that shares unchanged subtrees with the original" was wrong. `case _: return Add(lhs, rhs)` rebuilds an interior node even when neither child changed; verified that `simplify(Add(Mul(x, x), Num(0)))` returns a `Mul` that is *not* the input's `Mul` object, while the leaf `x` inside it *is* the original. Changed to "It returns a new tree, / and the leaves it keeps are the same objects as in the input." Proposal 7 offers the other repair, making the code match the original claim; accepting it means reverting this sentence.

## Checks run (all clean, before and after the edits)

- `ruff check`, `ty check`, `pytest` (17 passed) over `build/examples/34_Composite_and_Interpreter`
- every listing executed; all six `#:` marker sets match stdout
- `heading_links.py` and `banned_phrases.py`
- verified independently: `assert_never()` does flag both walkers when `Symlink` joins the union (two `type-assertion-failure` diagnostics); `ty` does reject `"a" + x` (`unsupported-operator`) while the runtime builds `Add(Num('a'), Var('x'))`; the recursion limit is 1000 on the pinned 3.15.0b4 and a 5,000-node chain does raise `RecursionError`; the or-pattern binding mismatch is a compile-time `SyntaxError`
