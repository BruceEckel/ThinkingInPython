When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter-level, "one claim, one arc": the chapter's stated claim covers two
of its three topics.**

The intro says

> This chapter covers the two channels an Effect declares:
> the dependencies it needs and the ways it can fail.

and the conclusion, "Emptying the Channels," opens with "The two halves of
this chapter taught two vocabularies."
Between them sit [Where `run()` Can Be Called](#where-run-can-be-called) and
[Waiting on a Coroutine](#waiting-on-a-coroutine), about 190 lines that teach
`run_async()`, `Async`, `wait()`, `stateless.time.sleep()`, `Time`, and
`test_instant_clock.py`.
None of that is a dependency and none of it is a failure, and the conclusion
never mentions any of it.

The material belongs in the chapter; the framing has not caught up with it.
`Async` really is in the Ability channel, so the two-channel claim *can* cover
it, but only if the chapter says so, and right now the only place that says so
is one sentence 400 lines earlier ("So `Async` is answered rather than
supplied").

There is a related precision problem in the conclusion.
It says

> An Effect with both channels emptied is a `Success`, which `run()` accepts.

`Success` is sufficient, not necessary.
`run()`'s parameter is `Effect[Async, Exception, R]`, so it also accepts an
Effect that still declares `Async` and one that still declares a failure ---
the chapter established both, in
[Supplying the Dependency](#supplying-the-dependency) ("That `Success` is a
consequence, not a requirement") and in
[Declaring Is Not Handling](#declaring-is-not-handling).
As written the conclusion quietly walks that back.

Recommended fix, the cheaper of the two: leave the intro alone and add a third
numbered item plus one sentence to "Emptying the Channels":

> 3. An Ability the driver answers itself needs no vocabulary at all.
>    `Async` sits in the same channel as a `Need` and is never supplied,
>    because `run()` owns the event loop that answers it.
>
> An Effect with both channels emptied is a `Success`.
> `run()` accepts more than that: its parameter is
> `Effect[Async, Exception, R]`, so an `Async` request or a declared failure
> can still be in flight when it is called.

The alternative is to widen the intro's claim to "two channels and the driver
that answers what is left," which costs a rewritten opening paragraph and
still leaves the conclusion silent on `Async`.
I prefer the conclusion fix: the intro's sentence is a good short claim and
the conclusion is where the reader is counting what they learned.

---

[] Reject

**"The Simplest Effect": "Nothing computes until `run()` is called" is
contradicted by the listing it annotates.**

`double(21)` evaluates `21 * 2` and hands the result to `success()`, all
before `run()` is reached.
The sentence is about Effects and `n * 2` is arguably not part of what the
Effect describes, but this is the chapter's opening statement of its central
idea and the reader has exactly one listing in front of them, in which
something plainly does compute.

Proposed change: make the subject the Effect rather than the program.

> Nothing the Effect describes happens until `run()` is called,
> and a program calls `run()` only once, at its outermost edge.

Same paragraph, second half: "a program calls `run()` only once, at its
outermost edge" is stated absolutely here and then qualified 800 lines later
in [Where `run()` Can Be Called](#where-run-can-be-called): "A synchronous
program calls `run()` once at its outermost edge. A program that is already
asynchronous, a web service or a bot, awaits `run_async()` at the edge of each
request."
Adding "synchronous" here would cost one word and remove the contradiction:
"and a synchronous program calls `run()` only once, at its outermost edge."

---

[] Reject

**`unsupplied.py`: the marker prints a type name where the message names the
missing Ability.**

The listing ends

```python
except MissingAbilityError as e:
    print(type(e).__name__)
#: MissingAbilityError
```

`print(e)` gives `Need(t=<class 'greeter.Console'>)`, which names *which*
Ability went unanswered.
That is the whole content of the error, and it is the same information the
`ty` diagnostic under the listing carries, so the two halves of the section
would line up: the checker says `Need[Console]` is left over, and the runtime
says the same thing.

I checked determinism specifically, since CLAUDE.md recommends
`type(e).__name__` for messages that can vary.
`MissingAbilityError`'s argument is the frozen dataclass `Need`, so `str(e)` is
its generated `repr`, with the module-qualified class inside.
Two consecutive runs on the pinned 3.15 build produced the identical string.

Proposed change: `print(e)` and `#: Need(t=<class 'greeter.Console'>)`.
Reported rather than applied because it changes an existing output marker.

Note if you take it: `MissingAbilityError` then no longer appears in the
output, only in the `except` clause, which is fine because the prose names it
in the very next line.

---

[] Reject

**Order: "Where `run()` Can Be Called" opens by re-establishing context from
eight sections back, and would read better after "Waiting on a Coroutine."**

Its first line is

> The error message in `unsupplied.py` said `run()` handles `Async` on its own.

`unsupplied.py` is in [Forgetting to Supply](#forgetting-to-supply), roughly
700 lines earlier, and the section before this one is "A Default Binding,"
with which it shares nothing.
This is the tell the review procedure names: a section that opens by
re-establishing context from three sections back.

Swapping the two sections fixes it.
"Waiting on a Coroutine" already opens on its own terms ("`Async` has appeared
so far only inside error messages, answered by `run()` without anyone asking
for it"), and "Where `run()` Can Be Called" then opens from the fact the
reader just met rather than from a message they have forgotten:

> `run()` answers `Async` because its entire body is
> `return asyncio.run(run_async(effect))`.
> That has a consequence worth knowing before you incorporate Stateless into
> an existing application.

Price of the move, checked:

- Nothing in `Chapters/` or `Solutions/` links
  `#where-run-can-be-called`; the anchor itself does not change, only its
  position. Chapter 47 line 1692 links `#waiting-on-a-coroutine`, also
  unaffected.
- "Waiting on a Coroutine" currently says "`run()` does that with the event
  loop it already owns," which leans on the moved section. It needs one word:
  "with the event loop `run()` starts."
- "Waiting on a Coroutine" ends on `test_instant_clock.py`, and "The Error
  Channel" opens "Dependencies are one half of the `Effect` type. The other
  half is failure." That transition works from either section, since neither
  is about failure.
- `inside_a_loop.py` imports only `greeter`, so it has no new dependency in
  the later position.

Total cost is two rewritten sentences. I recommend the swap.

---

[] Reject

**New listing: the chapter now says `try`/`except` is not `catch()`, but does
not show it.**

I added a paragraph to [Declaring Is Not Handling](#declaring-is-not-handling)
stating the three facts (an ordinary `try`/`except` around a `yield from` does
fire, the signature keeps the failure anyway, and a `catch()` further out
makes the inner `except` never run).
Placement of a listing is your call, so here is the verified one if you want
the demonstration rather than the claim.

This is the near-miss a reader is most likely to write.
Everything they know about Python says `try`/`except` handles an exception,
and here it half-works: the driver throws the yielded failure back into the
generator, so the `except` clause really does run, and the reader concludes
they have handled the error while the type still says otherwise.

```python
# except_vs_catch.py
from typing import assert_never
from scores import score
from stateless import Success, Try, catch, run

def guarded(name: str) -> Try[KeyError, str]:
    try:
        value = yield from score(name)
    except KeyError:
        return f"{name}: unknown"
    return f"{name}: {value}"

def moved(name: str) -> Success[str]:
    value: int | KeyError = yield from catch(KeyError)(score)(name)
    match value:
        case KeyError():
            return f"{name}: unknown"
        case int():
            return f"{name}: {value}"
        case _:
            assert_never(value)

print(run(guarded("Carol")), run(moved("Carol")))
#: Carol: unknown Carol: unknown
print(repr(run(catch(KeyError)(guarded)("Carol"))))
#: KeyError('Carol')
```

Verified in `build/private/46`: runs, markers exact, `ruff` clean at 70,
`ty` clean.
The two functions behave identically at the edge and differ in their types:
`guarded()` must keep declaring a `KeyError` it can no longer emit, and
`moved()` is a `Success`.
The last two lines are the sharp part: wrap `guarded()` in a `catch()` and the
inner `except` is dead code, because `catch()` matches the yielded value
before the driver ever gets it and abandons the inner generator where it
stands.

Where it goes: end of [Declaring Is Not Handling](#declaring-is-not-handling),
after the paragraph I added, which then becomes the lead-in.
It is the only place the two constructs sit side by side, and it hands off to
"Turning an Error Into a Value" with the reader already knowing why `catch()`
exists.

One alternative if you would rather not add a listing here: move the pair into
[Turning an Error Into a Value](#turning-an-error-into-a-value) as a
counterexample under `catch_score.py`. That costs the setup, since
`catch_score.py` also drags in `Console` and `supply()`, and the contrast gets
buried under the parts that are not the point.

---

[] Reject

**"Builtin Abilities": `Files` is the library's own example of both channels
at once, and the bullet hides it.**

The bullet reads

> - `Files` in `stateless.files` that reads a whole file,

`stateless/files.py`'s accessor is

```python
@throws(FileNotFoundError, PermissionError)
def read_file(path: str) -> Depend[Need[Files], str]:
```

so its signature is `Effect[Need[Files], FileNotFoundError | PermissionError,
str]`: an Ability and two declared failures, written by the library authors,
in nine lines.
It is also the chapter's only example of `@throws` applied to a function that
already returns an Effect --- every `@throws` in the chapter decorates a plain
function.

Proposed change: extend the bullet.

> - `Files` in `stateless.files` that reads a whole file,
>   whose accessor is `@throws(FileNotFoundError, PermissionError)` and so
>   declares both channels at once,

That is a forward reference to [The Error Channel](#the-error-channel) from a
section in the Ability half, which is why I did not just apply it; if you
would rather not point forward here, the same fact would fit as a sentence in
[Declaring a Failure with `@throws`](#declaring-a-failure-with-throws), where
it also answers "does `@throws` work on something that is already an Effect?"

---

[] Reject

**Five different types named `Console`, and the chapter never counts them.**

By the end of the chapter the reader has met:

| Where | What |
|---|---|
| `utils/greeter.py` | concrete class, the chapter's workhorse |
| `greet_all.py` | a verbatim copy of that class, so the listing stands alone |
| `console_protocol.py` | a `@runtime_checkable` `Protocol` |
| `default_console.py` | a dataclass with a `tag` field |
| `stateless.console` | the library's own, with `print()` *and* `input()` |

They are five distinct runtime types, and the distinction is load-bearing
twice: `Recorder` passes `isinstance()` only because it inherits
`greeter.Console`, while `Capture` passes only because
`console_protocol.Console` is structural.
A reader who has merged them in their head cannot follow
[Supplying an Interface](#supplying-an-interface) at all.

I applied one sentence, on `greet_all.py`'s copy.
The remaining gap is `default_console.py`, which introduces a *fourth*
`Console` with a constructor parameter, in a section about defaults, with no
comment.

Proposed change: one clause in "A Default Binding," after
"Layering produces one all the same:"

> This `Console` carries a tag so the output says which handler answered.

Not applied because it edits the lead-in of a listing you may have deliberately
left bare.

---

[] Reject

**"Dependency Injection": "Type checking is the optimal time to discover
errors."**

Two problems with *optimal*.
It is inflated where the surrounding paragraphs are plain, and the chapter
does not believe it: [Effect Management](44_Effect_Management.md#make-the-bad-value-impossible)
argues for removing the failure at construction, which is earlier than type
checking, and this chapter's own
[Turning an Error Into a Value](#turning-an-error-into-a-value) ends on making
an error impossible to ignore rather than impossible to have.

Proposed change:

> Type checking is the earliest practical time to discover these errors.

"these errors" also narrows the claim to the ones under discussion, which is
what the next sentence ("The trade is not about correctness, but churn and
coupling") assumes.

---

[] Reject

**`test_instant_clock.py`: a wall-clock assertion with a 30 ms budget.**

```python
assert time.perf_counter() - start < 0.03
```

The work being timed is three appends to a list, so the honest margin is
enormous, but 30 ms of wall clock is not much when `make sweep` is running
`pytest`, `ty`, and `ruff` over two trees at once, and this is a `pytest`
assertion rather than a `#:` marker, so nothing self-heals it --- it just goes
red with a message that looks like a real failure.

The number is presumably 0.03 because that is what `real_clock.py` asserts the
real clock exceeds, which is a nice symmetry.
The symmetry survives a looser bound: `real_clock.py` proves
`elapsed >= 0.03`, and this test only needs to prove the instant clock is
nowhere near it.

Proposed change: `< 0.5`, and if you want the symmetry stated, say it in the
prose ("the same three sleeps take at least 30 milliseconds in
`real_clock.py`" already does) rather than in the threshold.
Reported rather than applied because loosening a test's bound is a judgment
call about what the test is for.

---

[] Reject

**Exercises: nothing exercises "When Two Implementations Match."**

Ten exercises cover the interface (1), the propagation check (2, 7), `catch()`
(3), a `Protocol` ability (4), the environment matrix (5), `handle()` (6), the
one-shot Effect (8), `Async` (9), and the error channel (10).
[When Two Implementations Match](#when-two-implementations-match) gets none,
and it is the section describing the one mistake in the chapter that no tool
reports: the program runs, type-checks, and does the wrong thing.

Proposed exercise 11:

> 11. `ambiguous_supply.py` picks its `Console` by argument order.
>     Add a third implementation and predict, before running it, which of the
>     six orderings send Alice's greeting where.
>     Then follow the section's advice: give the two recording implementations
>     a method name the screen one does not have, declare each as its own
>     `Protocol`, and show that the ambiguity is now a type error rather than
>     a silent choice.

The second half is the part that earns its place: the section says "Give
abilities distinct method names when that ambiguity is possible" without
showing what that buys, and the exercise makes the reader produce the
diagnostic.

---

[] Reject

**Order: the assumes/introduces table, and what it does *not* show.**

Written out as the procedure asks, one line per section:

| Section | Assumes | Introduces |
|---|---|---|
| The Effect Type | 44's three questions | `Effect[A, E, R]`, the aliases, `Never` |
| The Simplest Effect | the aliases | `success()`, `run()`, `SuccessEffect` |
| Declaring a Dependency | `Depend` | `need()`, `Need`, `greeter.py` |
| The Effect Definition | 45's `Generator[Y, S, R]` | `Effect` as a `Generator` alias |
| Why `yield from` | that `Any` | why every request is `yield from` |
| Nothing Runs Yet | `need()` | the `Need` object, hand-driving |
| Supplying the Dependency | `greet()` | `supply()`, handlers, subtraction |
| An Effect Runs Once | `supply()`, `success()` | one-shot Effects, why combinators take functions |
| Forgetting to Supply | `run()` | `MissingAbilityError`, `run()`'s accepted type |
| Swapping the Implementation | `supply()` | `Recorder`, **`as_type()`** |
| Effects Propagate | `Depend` | virality, the missing-`yield from` trap |
| Retrofitting an Effect | propagation, 44's ex. 2 | `Need[A] \| Need[B]`, the `type`-alias warning |
| One Effect, Many Environments | two-argument `supply()` | environments as data |
| Builtin Abilities | the Ability idea | `stateless.console`/`files`/`time` |
| Supplying an Interface | **`as_type()`, 5 sections back** | `as_type()` vs `cast()`, `isinstance()`, `Protocol` abilities |
| When Two Implementations Match | `Protocol` abilities | argument-order resolution |
| Dependency Injection | everything above | the container contrast, handler layering |
| A Default Binding | layering | a fallback handler |
| Where `run()` Can Be Called | `run()` | `run_async()`, the nested-loop error |
| Waiting on a Coroutine | `run_async()` | `Async`, `wait()`, `Time` |
| The Error Channel (4 subsections) | `Effect[A, E, R]` | `@throws`, yielded failures, escape at the edge |
| Turning an Error Into a Value | `@throws` | `catch()`, error into result |
| Multiple Errors | `catch()` | partial catching |
| Emptying the Channels | both halves | the asymmetry between the two channels |

Reading the "assumes" column down the page, exactly one entry names something
later: `as_type()`, used in "Swapping the Implementation" and explained in
"Supplying an Interface," about 350 lines apart.

I looked hard at moving "Supplying an Interface" (and its dependent, "When Two
Implementations Match") up to sit directly after "Swapping the
Implementation," and I am recommending **against** it, for the record so the
next review does not re-open it:

- The debt is already mostly paid at the point of use. "It says 'treat this
  recorder as a `Console`,' and at runtime it returns the object it was
  given. `supply()` requires it because it reads the Ability from the static
  type of its argument" *is* the answer; the later section adds `cast()`,
  `Protocol`s, and the inheritance cost, none of which the reader needs yet.
- Moving it would put `console_protocol.py`'s `Console` in front of the
  reader before `greet_all.py`'s and `audit_log.py`'s, making the five-Console
  problem above materially worse.
- It would cost four sentence rewrites: "Builtin Abilities" ends with
  "[Supplying an Interface], next, explains where that cost comes from," and
  "One Effect, Many Environments" says "[When Two Implementations Match] picks
  up the case where two supplied objects fit one Ability" --- both become
  backward references.

The genuine ordering item in this chapter is the "Where `run()` Can Be Called"
cold open, above, which is cheap.
Everything else justifies its transition explicitly, which is unusual and
worth saying: most sections open with a sentence naming what the previous one
left undone.

---

## Cross-chapter

[] Reject

**`CLAUDE.md`, the Traps list: `validate_output.py` also breaks on a relative
`--tree`, and only `run_examples.py` is documented.**

The list says

> **`run_examples.py`: never pass a relative `--tree`.** It goes on
> `PYTHONPATH` and breaks once an example changes cwd.

`tools/validate_output.py` has the same defect for the same reason and is not
mentioned.
`run_location()` does `sys.path.insert(0, str(root))` with `root = tree /
'utils'` and then `os.chdir(rundir)`, so a relative `--tree` puts a relative
string on `sys.path` that stops resolving the moment the cwd moves into the
chapter directory.

Symptom, running exactly the deep-review recipe:

```
uv run python tools/validate_output.py --tree build/private/46 Chapters/46_Stateless.md
  line 239: ModuleNotFoundError: No module named 'greeter'
  ... 13 more
```

Every failing block is one that imports `utils/greeter.py`,
`utils/`-independent blocks pass, and an absolute `--tree` fixes all fourteen.
This is a trap worth documenting because the failure names the *chapter's*
imports, so it reads as a broken listing rather than a bad flag.

Change I would make in `CLAUDE.md`: generalize the bullet to
"`run_examples.py` and `validate_output.py`: never pass a relative `--tree`,"
and add that the second one manifests as `ModuleNotFoundError` on
`utils/` helpers.
I did not touch it, per the scope rules.

---

[] Reject

**`Chapters/47_Stateless_in_Practice.md`, "### `repeat()` and `memoize()`":
this heading is now linked from chapter 46.**

I added a paragraph to [An Effect Runs Once](#an-effect-runs-once) pointing at
`memoize()`, because the chapter previously told the reader that a Stateless
Effect can be run exactly once and that "that decision belongs to whoever
still holds the function," with no mention that the library ships the one
tool that makes a second `run()` produce the value again.
The link is `47_Stateless_in_Practice.md#repeat-and-memoize` and
`heading_links.py` passes on it now.

No change is needed in 47. This is a note so that renaming that heading is
known to have a consumer outside the chapter.
The two ends agree: 47 says "`memoize()` solves the spent-generator problem"
and "it wraps the Effect in an object that records the result and replays it
rather than driving the spent generator again," which is what 46 now says in
one sentence.

---

## Manifest: applied to `Chapters/46_Stateless.md` in this pass

[] Reject

*This block is a record of what already changed, not a proposal. Rejecting it
does nothing; to undo an item, revert it in the chapter.*

1. "Declaring a Dependency": "both this chapter and the next one import it" is
   now a named link to `[Stateless in Practice](47_Stateless_in_Practice.md)`.
   That was the chapter's last relative chapter reference; the CLAUDE.md
   grep (`previous chapter|previous section|last chapter|earlier chapter|the
   next chapter|the next one`) now returns nothing.
2. "The Effect Definition": the gloss on the `Generator`'s SendType now reads
   "the type the `yield` expression produces inside the generator," matching
   chapter 45's own wording, instead of "what comes back from a `yield`
   call" (a `yield` is not a call).
3. "Supplying the Dependency": "The `bound` assignment does three things"
   became "Those two lines do three things." The third item is
   `bound("Alice")`, which happens on the next line, not in the assignment.
4. "An Effect Runs Once": added a paragraph on `memoize()` with a link to
   47's `#repeat-and-memoize`, so the one-shot rule no longer reads as
   absolute.
5. "Effects Propagate, and the Checker Verifies It": added one sentence noting
   that `greet_all.py` repeats `Console` and `greet()` rather than importing
   them from `greeter.py`.
6. "Supplying an Interface": "Everything in between works the same under
   either form" became "Every function between that boundary and the Effect is
   written the same way under either form." The old pronoun had no antecedent
   after a sentence about local variables.
7. "Dependency Injection", `dependency_injection.py`: `get()` was LBYL
   (`if t not in DI_CONTAINER: raise ...`) against the house rule "Prefer
   EAFP over LBYL for a dict lookup," with nothing in the prose explaining the
   deviation. It is now `try`/`except KeyError` with
   `raise NotRegistered(...) from e`. Output is unchanged.
8. "Dependency Injection": "Java's checked exceptions" now links to
   `44_Effect_Management.md#catch-the-exception-you-expect`, where the same
   complaint is made about exception specifications.
9. "Waiting on a Coroutine": "takes that bound apart" became "takes that type
   bound apart," which names the concept and stops colliding with the `bound`
   variable in `supply_console.py`.
10. "Waiting on a Coroutine": added a note that the local `time` in the quoted
    `stateless.time.sleep()` is the supplied `Time` instance, not the standard
    library's `time` module, so `time.sleep(seconds)` is a coroutine.
11. "Declaring Is Not Handling": added a paragraph on `try`/`except` versus
    `catch()` (verified: the `except` really does fire, the signature keeps
    the failure, and an outer `catch()` makes the inner `except` dead code),
    and moved the "`@throws`-only channel" paragraph ahead of it so the
    section ends by handing off to "Turning an Error Into a Value."
    The same edit dropped "the next chapter" in favor of the bare named
    section link, matching every other forward reference in the chapter.
12. Ran `uv run python tools/reflow_prose.py --write 46` over the new prose
    only (the chapter was already reflow-clean; the tool reported four
    paragraphs, all mine).

Verified after every edit, against `build/private/46`: `extract_examples.py`,
`validate_output.py` (1 ok, 0 failed), `ruff check` (clean at 70), `ty check`
(3 diagnostics, all the intended `reveal_type` infos), `pytest` (10 passed),
`heading_links.py` (OK), `banned_phrases.py` (none), `reflow_prose.py --diff`
(0 paragraphs).

Prose-pass note for the record: the "promise" metaphor this sweep is hunting
does not occur in this chapter at all --- no `promise`, `promises`,
`promised`, or `promising`, in prose or code. Neither does "reach for."
The chapter already prefers the literal verbs the note asks for: an annotation
*states* or *declares* a dependency, `ty` *rejects* and *reports*, `supply()`
*answers* a request, and `@throws` *lifts* an exception into the type.
