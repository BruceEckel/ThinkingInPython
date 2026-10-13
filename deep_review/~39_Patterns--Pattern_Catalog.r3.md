When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Third deep review of chapter 39, run 2026-10-13 after the day's deep reviews of
other chapters and the two outside reviews (commits f2062667 and b5946b90).
The chapter has no listings and no Solutions file, so the run checked prose and links:
every link target's section was read against the row that points at it
(all anchors resolve, and each section still covers its pattern),
the chapter 21 claim about the GoF taxonomy still holds,
every source and group table is still alphabetical,
and `ProactorEventLoop` was confirmed as the default loop under `uv run python` (3.15.0).
`tip verify-ch CH=39 ISOLATED=1` passed 17 of 17 before and after the edits,
and `tip prose CH=39` reports nothing new (Vale, stranded prepositions, watch words, positional pointers).
The standing rejection in `deep_review_db.md` (no conclusion, no exercises),
both earlier reviews' declined lists, and the outside reviews' rejected items are honored.

No finding needed a decision only you can make, so this file has no live blocks.

## Applied directly

- Intro, the "does not recommend it" paragraph held two concepts. The *dissolve* sentence now follows
  the language-limits clause it extends ("those workarounds often dissolve in Python"),
  and the *State*/*State Machine* pair is its own paragraph.
- Intro, *State*/*State Machine*: "so the object advances without the client choosing" became the positive contrast
  "the client chooses each new state" (*State*) against "The client supplies the inputs, and the machine chooses each next state"
  (*State Machine*), matching chapter 26's `change_to()` and chapter 31's opening.
- Intro, the three idiom groups: the list "language idioms, most of them tied to C++ or Java's limits, functional idioms, and ..."
  read as four items; the aside is now in parentheses.
- Intro, "Other Patterns and Idioms" is now a link to that section.
- Problem table: *Structured Concurrency* joins "Coordinating concurrent work"; the outside review added its row to the Concurrency table, but no problem row named it.
- Problem table: rows added for *Template Method* and *Iterator*, two GoF patterns with chapters of their own that a reader searching by problem could not reach.
- *Monitor Object*: "so only one method runs on an object at a time" became "so one method at a time runs on an object" (the `only ... at a time` rule).
- *Reactor* paragraph: the sentence joining the mechanism and the *Dispatcher* alias is split in two.
- *Proactor*: "follows the same naming" said nothing about the pattern.
  It is now its own paragraph contrasting the lookalike pair: a *Reactor* calls the handler when a source is ready and the handler does the I/O;
  a *Proactor* starts the I/O and calls the handler on completion, and Windows' default `ProactorEventLoop` uses I/O completion ports.
- *Bulkhead*: "so one failure does not stop the whole system" became "so one failure leaves the rest of the system running" (positive form).
- *RAII*: "in a constructor ... in the destructor" became "in a constructor ... in the matching destructor", so the two halves agree.
- Closing lines: "Subtracting Python's share leaves the intent, not the structure" and the next sentence's repeat of "subtracts Python's share"
  became a statement of what Python supplies, what the reader still decides, and where the links lead.
  This rewords the existing two sentences; it adds no conclusion section.

## Considered and declined

- Problem-table rows for every covered pattern (*Pipes and Filters*, *Borg*, *Blackboard*, *Reflection*, the functional idioms).
  The table is a selective index of common problems, and those names sit one scroll away in their source tables.
- *Inversion of Control* in the "Supplying a collaborator" problem row: its intent is about who calls whom, not about supplying a collaborator,
  and its own row already relates it to *Dependency Injection* and *Service Locator*.

## For the session

- `tip prose CH=39` printed one stale `internal_names` baseline entry from another chapter:
  `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`.
  It is not this chapter's; chapter 15's reviewer or the session should drop it from the baseline after checking.
