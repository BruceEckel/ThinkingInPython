> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 28_Patterns--Function_Objects (2026-09-29)

This run is part of the book-wide sweep of 2026-09-29, made in a worktree on branch `review/28`.
Nothing here needs your decision, so the file has no live blocks.

I checked each claim against its listing, the chapters it links (5, 14, 17, 18, 21, 30, 33, 37, 40), the GoF text, and probes under `ty` 0.0.84 and the pinned interpreter.
What holds:

- Both GoF quotations are in the book: "Commands are an object-oriented replacement for callbacks" (Command, Applicability), and the View-Controller pair as an example of *Strategy*, with the controller that ignores input events (chapter 1).
- `subscribe(Deposit, on_withdraw)` draws `invalid-argument-type` from `ty`.
- `Audit(50).threshold = 1` draws "Property `threshold` defined in `Audit` is read-only", the same message a written-out `@dataclass(frozen=True)` draws.
- An undecorated class with the right `__call__()` passes `ty` at `subscribe()`, and a string passes at `publish()`.
- `bisection()` returns `0.0` for a root at zero.
- A keyword for a positional-only parameter fails in `partial()`, and three `Placeholder` arguments bind a trailing one.
- Registering `cls` in `event()` produces `Announce: not an @event`, as `CLAUDE.md` records.
- Every sentence that another chapter writes about this one (17, 21, 25, 30, 31, 36, 37, 39, 40) matches what the named section says.

`tip verify-ch CH=28` passes 24 of 24.
The whole-book `tip verify` failed once on two chapter 47 listings that timed out (`run_cost.py`, `undeclared_failure.py`) while twenty other reviews loaded the machine.
Both pass when run again by themselves, and the 311 tests in `build/examples` pass.

## Applied directly

Chapter, corrections:

- Tagged bus, the `built` paragraph: "`@handler` rejects `Announce` because its `Deposit` is not an `@event`" named two classes the reader meets a listing later, since the split moved them to `bank_events.py`. The paragraph now states both consequences in terms of `tagged_bus.py` (`publish()` refuses every event, `@handler` refuses every handler class) and points to exercise 7.
- `partial_bisection.py`: `bisection_tol()` declared `float | None` and had no path that returns `None`. It now has the bracket check that `bisection_within()` has, so the two listings hold the same algorithm. The demo runs both `partial` objects through `solve()`, as `configured_strategy.py` runs its closures, and the prose says a `partial` object satisfies `RootFinder`. Before, the listing called them directly and showed nothing about interchangeability.
- Strategy: "That argument determines how comparison works" was wrong about `key`, which chooses what is compared. Now "it chooses the value by which each item is compared, and the algorithm that does the comparing stays the same."
- Closing paragraph: "one shared subject: instead of every observable holding its own list" used two words for one role. Both are "subject", the word chapter 30 uses.
- `bound_method.py`: `Account` had a hand-written `__init__()` that assigned one parameter. It is a `@dataclass` now, per the house rule.

Chapter, teaching:

- Bound method: added the near-miss. `account.deposit()` in the list calls the method while the list is built and stores `None`, and `ty` rejects the list.
- `test_chain.py`: the `# type: ignore` had no explanation. Added one: a `Callable` declares no `__name__`, `ty` is right because a `partial` object is a `RootFinder` without one, and a `Protocol` that declares `__name__` needs no comment.
- Event bus opening: the section presented the bus as the chain keyed by type. It differs in a second way, which is now stated: the bus calls every handler, and the chain stops at the first success.
- Tagged bus opening: added the motivation before the mechanism. Each `subscribe()` call in `event_bus.py` repeats the event type that the annotation names, and the second version reads the annotation.
- Tagged bus: added a paragraph on two details of `tagged_bus.py` that a reader would copy without understanding. `vars(cls)` is used because `hasattr(cls, "__call__")` is true of every class, and the `/` in `Handler` lets a handler name its parameter anything.
- Strategy opening: "so the chain in `chain.py` can fall back on them" referred to a chain the reader had not met. Now a separate sentence that says where `chain.py` is.
- Exercise 7 is new: register `cls` in `event()` and predict what importing `bank_events.py` does. The section had three listings, a test file, and no exercise.
- Exercise pointers added for exercises 3, 5, and 7, and accepted into `tools/data/exercise_refs_baseline.txt` after reading each against its title.
- The ladder's entries 2 and 3 now name their listings (`bound_method.py`, `partial_bisection.py`).

Chapter, style:

- Function references take parentheses: `subscribe()`, `publish()`, `partial()`, `bisection_tol()`, `bisection_within()`, `__call__()`, `__init__()`.
- Dropped "already" (twice), "simply", "exactly as", and the trailing "and nothing more"; removed the italics on "which".

Solutions:

- Exercise 2 did not do what the exercise asks. No handler reported why it failed, and `solve()` printed "could not converge" for every failure, which is false of `bisection()` on `[1.0, 1.3]`, where the interval has no bracket. Each finder now returns `float | Failed`, a record carrying the reason, and `solve()` separates the two with `match`. A second call shows a chain in which every finder fails.
- Exercise 4: the prose said a tolerance of `0.5` accepts the first Newton step. That step is 0.5, and `abs(step) < 0.5` passed only because the central-difference slope comes out as 2.0000000000575, which makes the step 0.49999999998. The tolerance is now `0.6`, and the output is unchanged. `MAX_ITER` gained `Final[int]`.
- Exercise 1: `Deposit` had a hand-written `__init__()` and a bare `dict` annotation. It is a `@record` with `dict[str, int]`, and the prose says why a frozen record can still update the balance.
- Exercise 6: added a paragraph for the other reading of the closing question. A value computed from the frozen `n` is read late by the two lambda forms and early by `partial()`. The answer about `n` stands, and now says `n`.
- Exercise 7: new solution, `exercise_7.py`.
- Exercises 3 and 5: dropped "exactly" (twice), "just", "itself" (twice), and two emphasis italics.

## Considered and declined

- `command_pattern.py`'s `Macro` and the two `EventBus` classes keep their hand-written `__init__()`. Each creates an empty container and takes no parameter, and the dataclass form needs `field(default_factory=...)`, a second topic in listings about something else.
- `chain.py` and `event_bus.py` each hold a library function and a demo, and a test imports each. Splitting them the way `tagged_bus.py` was split would add two listings to show what four lines of demo show now. The demos print during the test import and nothing depends on that output.
- `command_pattern.py`'s base class keeps `raise NotImplementedError`. The listing shows the classic form, and the solution to exercise 1 refers to those bodies.
- The `*what*`, `*how*`, `*which*` italics in the opening list stay. They name the three things deferred, and the rest of the chapter returns to them.
- Exercise 6's closing question still presupposes that one fix works and the solution still answers that none does for `n`. The 2026-08-11 review recorded the pair as deliberate.
- A `@handler` class whose `__call__()` takes only `self` fails with an `IndexError`. A check for it would add a fifth refusal to a listing that has four, for a mistake `ty` reports at the `subscribe()` call.
- `dataclass_transform` in the link text stays without its `@`. Chapter 17's heading has it, and the prose here names the function.
