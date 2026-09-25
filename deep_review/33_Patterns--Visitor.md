> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 33_Patterns--Visitor (2026-09-25)

This review follows the five prose passes (literal, positive, straighten, cohesion, antecedents), each committed separately on `claude/prep-33`.
This run found nothing that needs your decision, so the file has no live blocks.
Everything had one sensible fix and is listed below. The closest call, whether the classic listing should keep its operations in the visitor, is the first item under "Considered and declined".
Probes run for this review: `ty` and Pyright both report `visitor.visit` on a `Visitor`-typed parameter and accept `nectar(42)`; `Gladiolus().accept(Bug())` raises `'Bug' object has no attribute 'visit'` at runtime; with its `# type: ignore` stripped, Solutions exercise 3 draws `invalid-argument-type` from `ty`, as that solution says.

## Applied directly

Chapter, corrections:

- "The Price of the Empty Base", last paragraph: "So in Python the primary hierarchy holds the operations" presented the listing's choice as a language constraint. `ast.NodeVisitor` keeps operations in the visitor by building `"visit_" + node.__class__.__name__` and calling `getattr()`. The sentence now names `flower_visitors.py` and adds the `NodeVisitor` alternative with its cost (the checker cannot follow a string).
- Classic Visitor intro: "A genuinely new operation does add code" (from the literal pass) now reads "a new operation whose behavior varies by flower type also needs a new method on `Flower`". Every new operation adds code somewhere; the claim is about *where*. The example of a reused operation now names `Fly`.
- `singledispatch` intro: "Python can add a *method*" and "Adding a *method* from outside" now say *operation*. `singledispatch` builds a function, and chapter 37 and this chapter's close both say "operation".
- Straighten and cohesion left the `match`/`assert_never()` remedy split over four short sentences with the union mentioned after its price. Now two sentences, with the union in the subject.
- "Nothing edits `Flower`" paragraph: "the default handles every type with no registered ancestor" was circular, since `object` is a registered ancestor of everything. Now reads "a type with no other registered ancestor gets the default." The later `nectar(42)` sentence opens "Because the default sits under `object`" instead of stating the registration a second time.
- "Where Visitor Still Fits": "the loop over the elements must run inside their own `accept()`" put the loop in the elements. It runs in the container's `accept()` (`Corsage`). Now reads "an object must loop over its own elements inside `accept()`".
- "One Dispatch Is Enough": "selects the operation before anything runs" is now "the call site names the operation, so writing `nectar()` rather than `fragrance()` selects it before the program runs."
- Corrections made while reviewing the prose passes: the positive pass's "When every type deserves its own answer" changed the condition, so it was restored as "When the default answer would be wrong for an unregistered type". The literal pass's "adds a method to a class from outside" was corrected at the same time.

Chapter, teaching:

- Classic Visitor intro: added the catch a first-time reader hits right after "a hierarchy you cannot change": `accept()` has to be in that hierarchy already, and you cannot add it to a vendor's classes yourself. That sets up the `singledispatch` section's "without the `accept()` method".
- Near-miss: after "a second `def visit()` replaces the first", added that `@overload` (linked to chapter 14) does not supply overloading. It declares signatures for the checker, and the one implementation still branches on type. A reader who knows `@overload` would reach for it here.
- `accept()` "passes the element in" (antecedents pass) became "passing `self`", which is what the listing does and needs no new term.
- The opening's first mention of *Multiple Dispatching* now links to chapter 32.
- "Where Visitor Still Fits" was an H3 under "The Pythonic Visitor: singledispatch", but it is about the classic pattern, not `singledispatch`. It is now an H2, and its anchor did not change. No other chapter links to it.

## Considered and declined

- **The classic listing keeps its operations on `Flower`.** `flower_visitors.py` puts the type-specific behavior on the flowers (`pollinate()`, `eat()`), and "The Price of the Empty Base" says this defeats the pattern's purpose, so the reader never sees a Python *Visitor* that adds an operation with no edit to `Flower`. The alternative is to have `Pollinator.visit()`/`Predator.visit()` dispatch with `match flower:` (or `NodeVisitor`-style `getattr`) and drop `pollinate()`/`eat()` from `Flower`. Declined: the chapter's claim is about why the second dispatch exists, and the current listing shows that mechanism best. `dispatch_trace.py`'s two-hop trace depends on `eat()` living on the flowers. The rewrite would also touch the "both dispatches change the result" paragraph, the coupling panel spec and caption, and Solutions exercises 1 and 3. The new `ast.NodeVisitor` sentence now tells the reader the alternative exists. If you want the fairer comparison anyway, say so and it becomes a rewrite of the chapter's first half.
- `test_visitor.py` wraps its import one name per line, where CLAUDE.md describes packed parentheses. The one-per-line form appears in 15 listings book-wide, so this is a book-wide question, not this chapter's.
- `Corsage` has a hand-written `__init__`. It exists to take `*elements`, which a dataclass field cannot express, so the deviation carries its reason.
- The coupling-panel caption (`tools/coupling_panels.py`) still matches the listing: `Flower` annotates only `Visitor` (plus `Any`), and `Pollinator.visit()` annotates only `Flower`. No change was made there.
- `flower_gen()` uses `Flower.__subclasses__()`, which sees direct subclasses only. The linked Factory section says so, and all three flowers are direct subclasses.
