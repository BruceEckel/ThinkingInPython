> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 30_Patterns--Observer (2026-09-19)

This run found nothing that needs your decision, so the file has no live blocks.
Two Opus `verify-claims` agents checked the chapter (about 95 claims) and its Solutions file (47 claims) against the listings, the eight linked chapters, the GoF text, the figure, and live `ty`, Pyright, and runtime probes.
Everything they or I found had one sensible fix, and those fixes are listed below.
`make verify-ch CH=30` passes 21 of 21, and `make pyright-review` shows an empty delta.

## Applied directly

Chapter, corrections:

- Push/pull: "This further decouples observer and subject" contradicted the sentence before it and GoF (implementation item on push and pull). Now says pull spares the subject from deciding what observers need, and costs each observer a dependency on the subject's interface.
- "The Names This Chapter Uses": the complaint named `Observable`, which GoF never uses and which left the classic listing when it became `Subject`. The paragraph now attributes `Observable` to `java.util.Observable` and the reactive libraries. "Differ by three letters" is gone (the edit distance is four).
- `watched.py` prose: the `Thermometer` misspelling is an error because `Thermometer` defines no `__setattr__()`, not "because a `@property` gives the checker a name to match." A class with a property and a permissive `__setattr__()` draws nothing from `ty`; a class with neither draws the error.
- "What Stays Constant": "no flag" referred to the `changed` flag of a classic listing removed long ago, and now collided with the re-entry flag the chapter recommends. It reads "no `update()` method", matching the four things the Pythonic section says disappear.
- Orphaned listener: "is never retrieved" is asyncio's term for a logged report that does not appear here, because `gather()` retrieves and drops the exception. Now "is discarded without a report."
- "`gather()` re-raises the first exception into `set_celsius()`": the listing under it has no `set_celsius()`. Now "to its caller."
- "`always: 1` never prints": nothing prints there. Now gives the probed result, `['once: 1', 'always: 2']`.
- "[Unsubscribing During a Notification] runs the failure": the section narrates it and its listing runs the working version. Now "traces."
- Dataclass paragraph: stray `)` after the chapter 12 link.
- Classic section: `Plot` and `Table` "attach", but neither exists. Now "a `Plot` or a `Table` would attach."

Chapter, teaching:

- `test_unsubscribe_stops_delivery()` stashed `record = received.append` under the comment "equal, not identical", so it tested identity. It now subscribes and unsubscribes `received.append` directly, and the prose about bound-method equality names the test and uses `received.append` in place of the classic `obj.update`.
- Lapsed listeners: added the near-miss. `weakref.ref(plot.redraw)` is dead on creation, which is the reason `WeakMethod` exists. Chapter 10 never mentions it.
- Async alias: "does the same job as the synchronous `Listener[T]`'s" named no job. Now says the parameter ties the listener's argument to the broadcaster's payload.
- Async self-removal: the old text said `once` "still receives that notification", which is trivially true of a listener that is running. The point is that `always` is not skipped; the text says so, and says what the next `announce()` does.
- "Three ways" paragraph: First, Second, Third, so the reader can find the three.
- Cut the event-bus sentence that closed the async section. Chapter 28's bus is synchronous, "the same fan-out" read as `gather()` there, and "What Stays Constant" makes the point in the right place.

Chapter, prose: "defines only", "`update()` is where each observer reacts" (`Display` modifies nothing), "`listener(data)`, where the classic version calls", "because `announce()` loops over a copy", the `echo` sentence ("the value the setter already holds" had the wrong holder), "`announce()` returns only after every listener finishes" (not "succeeds"; failure comes later), "it is enough to know that", "`True` only for", "so you can test it without a GUI."

Solutions:

- Listings under headings 2, 3, and 4 were named `exercise_3.py`, `exercise_4.py`, and `exercise_2.py`, left over from the reordering in cdd94192. Renamed to match their headings, with the two test imports. No gate reads these names.
- Exercise 6's Pyright paragraph gave the wrong cause and a fix that does not work. Pyright types `Thermometer.celsius` as `Notifying[float] | float` because the constructor's `self.celsius = celsius` declares an instance attribute; with those assignments removed it accepts the call. "A method on `Thermometer`" draws the same error, so only the `type(obj).__dict__` lookup remains.
- Exercise 4 put quotation marks around words the exercise does not contain.

## Considered and declined

- A listing that runs the no-copy failure (a `Broadcaster` subclass whose `announce()` loops over `self._listeners`). It would duplicate `once` and `always` to print one list, and the index-by-index prose plus the stated result now carries it.
- `watched.py` introduces `__setattr__()`, the `__dict__` write, and the bare annotation in one listing. Each is forced by the one before it and each gets its own paragraph, so splitting would show a listing that does not work.
- "(`tools/data/norun.txt` lists it)" is repo tooling in book prose, but chapter 31 says the same, so it is a convention.
- `test_no_subscribers_is_a_noop` goes unmentioned in the sentence listing what the tests confirm. The sentence claims no count.
