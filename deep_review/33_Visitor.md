When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/33_Visitor.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on
`build/examples/33_Visitor` (9 tests), and all three runnable scripts
run. Every checker and runtime claim was probed individually on the
pinned toolchain and all hold: `Gladiolus().accept(Bug())` fails with
`AttributeError: 'Bug' object has no attribute 'visit'`, matching the
prose verbatim; annotating `accept()`'s parameter as `Visitor` is an
`unresolved-attribute` under `ty`, matching "fails the type checker";
the sketched `Visits` protocol version passes `ty` and flags a
visit-less `Beetle` at the `accept()` call as `invalid-argument-type`
(exercise 3's promised outcome); `nectar(42)` returns `42: no nectar`;
and `nectar` reveals as `_SingleDispatchCallable[str]`, whose `Any`
parameters let `nectar(42)` through with no diagnostic, matching "the
dispatcher it builds declares its parameters as `Any`". The
registry/dispatch output lines are deterministic. Incoming and
outgoing links check out: chapter 21's Behavioral roster links here,
the anchors into 32 (`#one-type-or-many`), 34
(`#a-composite-of-data-classes`), 37
(`#adding-operations-visitor-and-why-python-skips-it`), and 41
(`#singledispatchmethod`) all resolve, chapters 34 and 37 link back
into this chapter's headings (so those headings must not be retitled),
and `Flower.__subclasses__()` is taught in chapter 27 before this use.
The 22 → 33 load-bearing-`Any` thread was re-verified against the
current text of both chapters and left untouched, per the standing
exemption in `deep_review_db.md`; the chapter-22 link deliberately
carries no anchor. `Solutions/33_Visitor.md` covers all three
exercises and its claims match the probes (including the
`ty: ignore[invalid-argument-type]` in exercise 3). No finding needed
a decision, so this file has no live blocks.

## Applied directly

- `flower_visitors.py`: both `__str__()` bodies now use
  `type(self).__name__` instead of `self.__class__.__name__`. The
  chapter's own `visitor_singledispatch.py`, `dispatch_trace.py`
  (`type(worm)`, `type(flower)`), and chapters 14, 31, and 32 all use
  the `type()` form; these two were the book's only `__class__`
  holdouts. `Solutions/33_Visitor.md`'s `exercise_3.py`, which copies
  this code, updated to match. Output unchanged.
- Registration paragraph: added the mechanism the listing only
  implies, "`@nectar.register` reads the annotation on the
  implementation's first parameter: `flower: Gladiolus` files that
  implementation under `Gladiolus`", and moved the union-annotation
  sentence next to it so the annotation material sits together; the
  `_`-naming discussion follows. Without this, the bare
  `@nectar.register` is the most magic-looking line in the listing and
  the reader must infer where the type comes from.
- "That's how *Visitor* works, but without the `accept()` method..."
  is now "That is what *Visitor* does, without...": the original
  invited a second reading ("works how, but without what?").
- Empty-base paragraph: "types its visitor as `Any`, because the
  `Visitor` base class declares no `visit()` method, so declaring that
  parameter as `Visitor` instead of `Any` fails the type checker"
  recast with a colon in place of the stacked "because... so...", and
  the duplicate "of `Any`" dropped.
- `NotImplementedError` advice split into advice plus consequence
  ("...instead of a fallback string. The omission then fails at the
  first call."), removing the imperative-plus-consequence shape.
- Watch-list words: "never by its own name" is now "not by its own
  name"; "`Ranunculus` was never registered" is now "was not
  registered"; "have to interact" is now "must interact".
- "That is the intent difference the chapter opened with" is now
  "...from the chapter's opening" (stranded preposition).
- Ran `make reflow CH=33`; it reported no further changes.

## Considered and declined

- The comment "# The Flower hierarchy cannot be changed:" stays,
  although the class below it visibly carries `accept()`,
  `pollinate()`, and `eat()`. The prose two sentences earlier requires
  `accept()` on the primary hierarchy, and "Notice where the behavior
  lives" interrogates the remaining tension deliberately; softening
  the comment would blunt the point that paragraph makes.
- "The trade loses nothing" (One Dispatch Is Enough) does not
  contradict the exercise-1 solution's "The one thing lost is the
  ability to hold a visitor in a variable": the chapter's sentence
  weighs the dispatch count, the solution's weighs visitor-as-object,
  and the solution shows the recovery (`op = eat`). Both stay.
- No forward mention of `ast.NodeVisitor` in "*Visitor* still has a
  place": chapter 34 introduces it beside the trees it walks and links
  back to this chapter, which is the better home.
- The explicit registration form `@nectar.register(Gladiolus)` is not
  shown: the chapter teaches the annotation idiom its listing uses,
  and the new mechanism sentence covers how registration learns the
  type.
- "Python can add a method to a fixed hierarchy from outside" stays:
  `singledispatch` builds a function, not a method, but the sentence
  mirrors the opening's "add new polymorphic methods" and the closing
  "open-method mechanism", and the chapter says "function" everywhere
  it is being precise.
