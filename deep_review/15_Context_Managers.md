When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Opening, lines 3-12: the two opening paragraphs say the same thing twice.**

Paragraph one: "runs setup before a block and cleanup after it, even if the
block raises an exception." Paragraph two: "marks out a span of execution,
running setup at its start and cleanup at its end." A reader gets the same
sentence twice before reaching any code, and the only new information in the
second paragraph is the `__del__()` contrast.

Proposed change: collapse to one paragraph, keeping the `__del__()` pointer:

```
The `with` statement,
introduced in [Control Flow](04_Control_Flow.md#context-managers),
marks out a span of execution:
it runs setup before a block and cleanup after it,
even if the block raises an exception.
That is far more reliable than the `__del__()` approach in [Cleanup](10_Cleanup.md).
This chapter shows how to write your own context managers, and how `with` works.
```

Reason: the chapter's first job is to make the reader want the tool. Saying
the definition once and immediately naming the alternative it beats does that
in four lines instead of eight.

---

[] Reject

**Line 85-88: "raises an exception" undersells how confusing the reuse error is.**

The text says "reusing the same object in a second `with` raises an
exception." On the pinned 3.15 build the exception is:

```
AttributeError: '_GeneratorContextManager' object has no attribute 'args'
```

(verified: `__enter__()` does `del self.args, self.kwds, self.func`, so the
second `__enter__()` fails looking for `self.args`, not with the
`RuntimeError: generator didn't yield` that older write-ups describe). That
message names nothing a reader would connect to reuse, so a reader who hits it
in their own code will not recognize the cause the chapter just warned them
about.

Proposed change: name the message, in the same paragraph:

```
so reusing the same object in a second `with` fails with a message that names
nothing useful:
`AttributeError: '_GeneratorContextManager' object has no attribute 'args'`.
```

Reason: the value of a warning is that the reader recognizes the symptom
later. A generic "raises an exception" cannot do that; the actual string can.

Alternative if you would rather not pin a CPython-internal message into the
book: say "fails with an `AttributeError` from inside `contextlib`, which
names nothing useful" and leave the exact text out.

---

[] Reject

**`utils/exceptions.py` (listing at line 279): one listing, five new things.**

The listing and its explanation introduce, in about twenty lines: the
`sentinel` builtin, a PEP 695 `type` alias, `type[BaseException]` as "the
class, not an instance", narrowing a union by ruling out a sentinel with
`is not`, and `issubclass()` with a tuple second argument. Four of the five
get their own explanatory paragraph afterward, which is the tell: the listing
needs 25 lines of prose to unpack because it is carrying five lessons at once,
and none of the five is the chapter's topic. The chapter's topic here is "a
truthy `__exit__()` return suppresses," which the listing demonstrates in two
lines.

Proposed change: split it. Show the minimal single-type version first, in the
chapter (not in `utils/`):

```python
# ignore_one.py

class ignore_one:
    def __init__(self, kind: type[BaseException]) -> None:
        self.kind = kind

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc: BaseException | None, tb: object) -> bool:
        if exc_type is not None and issubclass(exc_type, self.kind):
            print(f"{exc!r}")
            return True
        return False
```

then present `utils/exceptions.py` as "the version the rest of the book uses,"
whose only additions are the `ALL` sentinel default and the tuple form. The
sentinel/narrowing paragraphs then attach to the second listing, where they
are the one new thing.

Cost: one extra listing and about ten extra lines, in the chapter's longest
section. Reject if you would rather the section stay compact; the current
version is correct, just dense.

---

[] Reject

**`utils/exceptions.py` and `banner_cm.py`: hand-written `__init__` with no stated reason.**

`Trace` in `trace_cm.py` gets an explicit justification at line 98-99
("`__init__()` stays in its longhand form here rather than becoming a
`@dataclass`, so nothing between the class statement and the two protocol
methods needs decoding"). `ignore` and `banner` are the same shape — an
`__init__()` that only assigns one parameter to one field — and carry no such
note. `thinking-in-python-skill.md` says a class whose `__init__()` only
assigns parameters is a `@dataclass`, and that the manual form is written only
when the code is teaching it, "and then say why."

Recommended change (cheapest, and consistent with the chapter's stated
reason): extend the existing justification so it covers all three. Reword line
98-99 to something like "Every hand-written context manager class in this
chapter keeps `__init__()` in longhand rather than becoming a `@dataclass`, so
nothing between the class statement and the two protocol methods needs
decoding."

Alternative: convert `ignore` and `banner` to `@dataclass`. Not recommended
for `ignore`: `utils/exceptions.py` is imported by chapters 17, 18, 36, 40 and
44, so any change to it has to be re-verified against all of them, and the
generated `__eq__`/`__repr__` buy nothing for a class used only as
`with ignore(...)`.

---

[] Reject

**`object_pool.py`, line 662: `as conn` binds a name nothing reads.**

```python
with suppress(RuntimeError), pool.lease() as conn:
    raise RuntimeError("crash during query")
```

`conn` is never used in that block, and it shadows the `conn` from the
successful lease four lines above. Ruff does not catch it because the code is
at module level rather than inside a function.

Proposed change: drop the binding.

```python
with suppress(RuntimeError), pool.lease():
    raise RuntimeError("crash during query")
```

Reason: the point of the second `with` is that the lease is returned on the
exception path, which has nothing to do with the leased object. A bound name
nothing reads invites the reader to look for a use that is not there.

---

[] Reject

**`object_pool.py` / the thread-safety paragraph (line 654 and the prose after it): `qsize()` is approximate.**

`available()` returns `Queue.qsize()`, and the paragraph immediately after the
listing says "This means you can hand the same pool to several threads." The
stdlib documents `qsize()` as approximate: `qsize() > 0` does not guarantee a
later `get()` will not block, and `qsize() == 0` does not guarantee a `put()`
will not block. The chapter puts an unreliable-under-concurrency accessor and
the "share it across threads" claim two sentences apart, with nothing between
them.

Proposed change: add one sentence to the thread-safety paragraph, after "This
means you can hand the same pool to several threads":

```
`available()` is a snapshot for the demo, not a synchronization primitive:
`Queue.qsize()` is only approximate once more than one thread is borrowing,
because another thread can lease or return between the count and its use.
```

Reason: a reader who copies `Pool` into threaded code is likely to write
`if pool.available(): ...`, which is exactly the race the note rules out.

---

[] Reject

**Chapter-wide: async context managers are never mentioned.**

This is the book's context-manager chapter and it never says that
`__aenter__()`/`__aexit__()`, `async with`, `contextlib.asynccontextmanager`
and `AsyncExitStack` exist. [Concurrency](19_Concurrency.md) then uses
`async with` eleven times — `asyncio.TaskGroup`, `async with lock`,
`async with semaphore`, the deadlock demo — without ever explaining what makes
an object usable there, because the explanation logically belongs here and
chapter 19 reasonably assumes it happened. The result is that no chapter
teaches the async half of the protocol.

Recommended change: a short section at the end of "The `contextlib` Toolkit",
before "An Object Pool", roughly:

```
## The Async Protocol

`with` calls `__enter__()` and `__exit__()`.
`async with` calls `__aenter__()` and `__aexit__()`,
which are coroutines, so the setup and the cleanup can both await.
`contextlib.asynccontextmanager` turns an async generator into one,
the same way `@contextmanager` turns a generator into the synchronous form,
and `AsyncExitStack` is the `ExitStack` equivalent.
[Concurrency](19_Concurrency.md) uses `async with` throughout;
everything this chapter says about ordering, the exception arguments,
and the truthy-return suppression applies unchanged.
```

with one small listing (an `@asynccontextmanager` that prints enter/exit
around an `await asyncio.sleep(0.01)`), so the reader sees the shape.

Cost: the listing needs `asyncio.run()`, which the book does not otherwise
introduce until chapter 19, so the section either forward-references 19 for
`asyncio.run()` or stays prose-only. Prose-only would still close the gap.

Alternative if you want chapter 15 to stay synchronous: add a single
forward-pointing sentence here ("the async form, `async with` with
`__aenter__()`/`__aexit__()`, works the same way; see [Concurrency]") and put
the actual explanation at the top of chapter 19's `async with` material. That
is a chapter-19 edit, so it is logged under Cross-chapter below.

---

[] Reject

**Chapter-wide: no closing section; the chapter ends inside the Object Pool.**

The last prose before the exercises is about `lease()`. Neighboring chapters
close with a section that gathers the guidance — 16's "Choosing a Form", 17's
"Which Hook for Which Job", 12's "Where the Checks Went". Chapter 15's
guidance exists but is scattered across three places: "The generator form is
usually the clearest choice" (line 148), "Choose these before writing
`__enter__()` and `__exit__()` by hand" (line 553), and the
`ContextDecorator` limits paragraph (line 459-474).

Proposed change: a short "Choosing a Form" section before the exercises, four
or five lines, in a decision order: use a `contextlib` manager if one fits;
otherwise `@contextmanager`; otherwise a class, when the manager needs state,
methods, or reuse across several `with` statements; add `ContextDecorator`
only when the same bracket should also apply to a whole function.

Reason: the chapter now teaches four ways to get a context manager and never
puts them side by side. This is also where the "the reader can do something
new" test is decided: right now the last thing they read is a pattern example
rather than a rule they can apply.

---

[] Reject

**Chapter-wide: the payoff listing is the last one.**

The most convincing thing in the chapter is `Pool.lease()` — a two-line
borrower contract that makes a resource leak impossible. It is on the last
page. The chapter opens with `trace()`, which prints "enter A" and "exit A"
and buys the reader nothing they could not get from two `print()` calls.

Proposed change: put a three-line stripped version of the pool in the opening,
before "A Basic Context Manager", as motivation:

```
with pool.lease() as conn:
    conn.query("SELECT name FROM users")
```

with one sentence saying the connection goes back to the pool on every path
out, including the exception path, and that [An Object Pool](#an-object-pool)
builds it. Leave the full treatment where it is.

Cost: it forward-references a section eight pages later, and it shows a `with`
before the chapter has said what one is (though [Control
Flow](04_Control_Flow.md#context-managers) already did). Low confidence that
this is worth the churn — reject freely if the opening reads fine to you.

---

[] Reject

**Not in this chapter: `Solutions/15_Context_Managers.md` is incomplete and partly mismatched.**

Reported rather than fixed, since the brief scopes edits to
`Chapters/15_Context_Managers.md`. Three problems:

1. The chapter has seven exercises; the solutions file has four. Exercises 5
   (stacked `@banner`), 6 (the `KeyError`-only manager), and 7 (`ExitStack`
   from `sys.argv`) have no solution.
2. Solution 3's heading reads "A fourth manager on one `with` line". Exercise 3
   asks for a *third* manager, and the solution's code correctly shows three.
   The heading is wrong.
3. Solution 2 does not answer exercise 2. The exercise says "In
   `demo_exceptions.py`, change `ignore(ZeroDivisionError)` to
   `ignore((ZeroDivisionError, TypeError))`" — one call-site edit against the
   chapter's `ignore`, which takes a single `types` argument. The solution
   instead writes a new `Ignore(*types)` class with a different signature and
   different semantics (no `ALL` default, no printing), then explains why
   `*types` needed no change. A reader comparing the two will conclude the
   chapter's `ignore` accepts `ignore(A, B)`, which it does not.

Also note exercise 6's manager was renamed from `retrying` to `ignore_missing`
in this review (the old name described retrying, which the exercise never
asks for), so a solution written for exercise 6 should use the new name.

## Cross-chapter

**19_Concurrency.md** — only if you take the "alternative" branch of the async
finding above. Chapter 19 introduces `async with` at line 271 ("An `async
with` block owns every task started inside it") and uses it at lines 280, 654,
1345, 1637, 1872, 1910, 1964 and 1966 without ever stating that it is the
context-manager protocol with `__aenter__()`/`__aexit__()`. The change I would
make there: two sentences immediately before the `task_group.py` listing at
line 272, saying that `async with` is the `with` of [Context
Managers](15_Context_Managers.md#the-protocol) with awaitable
`__aenter__()`/`__aexit__()`, that entry and exit order are the same, and that
`contextlib.asynccontextmanager` builds one from an async generator. No
chapter-19 code changes. Do not apply this if you instead add the async
section to chapter 15.
