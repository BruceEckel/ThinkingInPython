> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 34_Patterns--Composite_and_Interpreter (2026-09-25)

This review follows the five prose passes (literal, positive, straighten, cohesion, antecedents), each committed separately on `claude/prep-34`.
This run found nothing that needs your decision, so the file has no live blocks.
Everything below had one sensible fix.
Probes run for this review: `"a" + x` builds `Add(Num('a'), Var('x'))` at runtime, `evaluate()` on it raises `TypeError`, and `ty` reports the `+` as `unsupported-operator`; a 3,000-node left-deep `Add` raises `RecursionError` in `evaluate()` against the default limit of 1000; `list(t"{a}{b}")` yields two `Interpolation` objects while `.strings` is `('', '', '')`; the Pyright baseline carries the four `self: Expr` "must be a supertype of its class" entries the chapter describes; `ty` reports a `Symlink` passed to `filesystem.py`'s `disk_usage()`, or placed in a `Directory`'s entries, as `invalid-argument-type`.

## Applied directly

Chapter, corrections:

- "Evaluation Is a Tree Walk", `**env` paragraph: "the live dicts at any moment total the tree's depth times the number of bound variables" counted dicts where it meant entries. Now: one dict is live per level of recursion, holding depth × bound variables in entries.
- Interpreter intro: "sentences written as Python source, with operands that are already nodes" said every operand must be a node. The later `2 + 3` paragraph says one is enough. Now reads "in which every operator has at least one node operand".
- `Num(2) + 3` paragraph: "`simplify()` would then receive a `Num(5)` already folded" (positive/straighten passes). `(2 + 3) * x` would reach `simplify()` as `Mul(Num(5), x)`, not a bare `Num(5)`. Now reads "`simplify()` would receive `5 * x` with the fold already done". Also, "The folded `2 + 3` is the limit" became "`2 + 3` shows the limit".
- The `"a" + x` sentence now names `ty` and its diagnostic (`unsupported-operator`), which the probe confirmed, in place of "the type checker reports".
- The straighten pass's claim fix, "Python shrinks the classes and removes the parser" (it had said "removes both requirements", but a data class is still a class per construct), was checked and kept.

Chapter, prose:

- Classic Composite: after the listing, "The same call works on the whole tree, on a subtree, and on a single file" repeated the section's opening sentence almost word for word (the literal pass had expanded that sentence). It now points at the evidence: "The demo's first `print()` makes that one call on the whole tree, on the `src` subtree, and on a lone file."
- Simplification: the antecedents pass left "simplifying first" twice in two lines. The second is now "That order is how the demo's ... collapses to `x`."
- Closing paragraph: the antecedents pass's "The injection attempt makes the general argument" made the attack the argument. Now "That separation is the general argument", which points at the preceding paragraph's "receives the literal pieces and the values as separate things".
- Exercise 8: "the other alternative" (literal pass, from "the other escape") became "another way out".

Chapter, teaching:

- Simplification: added why the sharing guard is `is` and not `==`. Sharing means the same object, and a data class's `==` compares whole subtrees, so it would walk each subtree again at every level. A reader who has just learned that the nodes compare by value would plausibly write `lhs == left`.

Corrections made while reviewing the prose passes:

- Positive pass: "With no unslotted base class above them, the nodes become records" had become "The nodes drop their abstract base, so the nodes become records", which lost the reason. The original was restored.

Solutions:

- Exercise 9 said "The type checker cannot warn the plugin author, because from its side the union is complete." That is false: `ty` reports the `Symlink` at the call and at the `Directory` construction. It now says the checker warns, that the warning leaves the plugin nothing to fix because the union lives in your source, and that code the checker never sees reaches `assert_never()` at runtime.

## Considered and declined

- The three-walker paragraph ("Three walkers over one set of nodes is the pattern pair in full") still reads like a conclusion with a section after it. `deep_review_db.md` records the ruling that it stays, and the passes left it alone.
- "*Interpreter* is *Composite* applied to language" (Interpreter intro) repeats the opening's "*Interpreter* is *Composite* with meaning attached". The repetition reopens the thesis at the point where the chapter turns to it, so it stays.
- `template_query.py` runs its demo at module level with no `if __name__ == "__main__":` guard, unlike the chapter's other modules. No other listing imports it, and Solutions exercise 7 builds its own copy, so the guard would add a level of indentation and gain nothing.
- The coupling-panel caption (`tools/coupling_panels.py` `CAPTIONS[34]` and the panel's `alt`) still matches `filesystem.py`: `disk_usage()` and `walk()` each name `File` and `Directory` in their patterns, and `Directory` annotates only `Node`. No change was made there.
- "the deep trees this chapter warns about later" (`**env` paragraph) is a forward reference with no heading to link, since the recursion-limit warning sits in the untitled paragraph after `test_simplify.py`. It is eight paragraphs away in the same chapter, so a relative phrase can't go stale through a chapter split.
