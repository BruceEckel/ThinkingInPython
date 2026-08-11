[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/14_Decorators.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty` and ruff are clean on `build/examples/14_Decorators`,
all 20 tests pass, and every script runs. The chapter's checker claims
were re-verified with probes on the pinned toolchain: paren-less
`@repeat` draws two `ty` diagnostics, the first at the `@` line
("Expected `int`, found `def greet(...)`") and the second at the call,
matching the prose; decorating a method with `trace_class.trace` draws
`missing-argument` plus `invalid-argument-type`, matching "a missing
argument and a type mismatch"; and `@decorator` above a bare assignment
or a `type` alias is a `SyntaxError` on the pinned 3.15. One probe
overturned a prose claim instead of confirming it (the paren-less
`@repeat` runtime story; see the applied list). This review inherited an
uncommitted edit from an interrupted earlier pass: it deleted the intro
paragraph about zero-parameter wrappers. The deletion was half right,
so the paragraph is not back where it was (details below). No findings
met the bar for a live block.

## Applied directly

- "Decorators That Take Arguments": the forgotten-parentheses paragraph
  claimed `@repeat` without parens binds `greet` to `decorate` and
  "Nothing raises an exception, so the only symptom is missing output".
  False for the shown listing: its own `times < 1` validation makes
  `repeat(greet)` raise `TypeError: '<' not supported between instances
  of 'function' and 'int'` at decoration (verified on the pinned
  interpreter). Rewrote the paragraph: the validation turns the mistake
  into a decoration-time `TypeError` whose message says nothing about
  parentheses, a `repeat` without the comparison would fail silently as
  originally described, and the annotations catch it either way.
- Kept the inherited deletion of the zero-parameter-wrapper paragraph
  from the intro (its "Every wrapper from here on takes that shape" was
  contradicted two lines later by `decoration_time.py`'s zero-parameter
  wrapper, and it interrupted the forgotten-return-to-decoration-time
  flow), but restored its teaching content, reworked, as the opening of
  "Maintaining the Wrapped Interface": the near-miss (a zero-parameter
  wrapper applied to `def add(a, b)` raises a `TypeError` at the call)
  now motivates the `*args, **kwargs` shape `tracer.py` introduces,
  which that section previously used without a bridge. The exact
  message is paraphrased, not quoted: on 3.15 it reads
  `add_behavior.<locals>.wrapper() takes 0 positional arguments...`,
  so the old text's quoted `wrapper() takes 0...` was already stale.
- "Decorating Classes" opener: added a disambiguation sentence ("Do not
  confuse this with [Decorators as Classes](#decorators-as-classes),
  where the decorator was written as a class; here the decorator is an
  ordinary function, and the class is the thing decorated"). The
  chapter's own headings create this lookalike pair and nothing marked
  the difference at the point of collision.
- "A Limitation": "decorated a method, only to a bare function" is now
  "only bare functions" (broken grammar, stray "to").
- Same section: "A fully typed class decorator, like
  `trace_class.trace`" is now "class-based decorator"; "class
  decorator" elsewhere in the chapter means a decorator applied to a
  class, and this sentence used it for the other meaning.
- Closure paragraph: "Defined inside `add_behavior()`" and "even after
  `add_behavior()` has already returned" now say "its decorator" / "the
  decorator"; the paragraph sits directly under `decoration_time.py`,
  whose decorator is `announce`, so the named referent was two listings
  back. Also dropped "already".
- "Function Form or Class Form?": the dangling participle "at
  `__call__()`, moving from `__init__()` to `__call__()` as soon as the
  decorator gains arguments" is now its own sentence with a gerund
  subject ("Gaining arguments moves the function's arrival from
  `__init__()` to `__call__()`").
- "A Class Decorator with Arguments": swapped two sentences so "This
  validates `times`..." directly follows the listing it describes; the
  form-comparison judgment sat between them and broke the referent.
- "`wraps` is optional but there is rarely a reason to omit it" is now
  "`wraps` is optional; reasons to omit it are rare" (expletive
  "there is").
- `run_once` prose: "Calling `greeting()` again fails" is now "now
  fails"; the reader never called it a first time, `run_once` did.
- "That is the object-oriented *Decorator* pattern" drops the italics;
  the term was introduced, italicized, in the chapter intro.
- Ran `make reflow CH=14` over the edited prose.

## Considered and declined

- Renaming the "A Stateless Class Decorator" / "A Class Decorator with
  State" / "A Class Decorator with Arguments" headings to
  "Class-Based...": under the "Decorators as Classes" parent heading
  the meaning is unambiguous, the added disambiguation sentence covers
  the one real collision point, and the rename would churn anchors for
  no reader gain.
- `ClassVar[float]` annotations on `Margherita.cost` and its neighbors,
  for consistency with `Topping.add_cost`: the bare form keeps the
  pattern listing minimal, the prose explicitly calls it "a class
  attribute", and the listing's point is the structural `Protocol`
  match, not attribute-declaration style.
- A warning that a sync wrapper breaks a decorated `async def`
  (the coroutine gets created but the wrapper's timing or handling
  misses the actual awaited work): a real near-miss, but concurrency
  is chapter 19 (`Chapters/19_Concurrency.md`) and nothing
  before it teaches `async def`, so the warning cannot be stated here
  without using an untaught construct.
- "`@` constrains the statement below it and nothing else" keeps its
  tag: the sentence otherwise excludes nothing, and the exclusion is
  the section's point.
