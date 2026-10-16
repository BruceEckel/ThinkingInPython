> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/39_Patterns--Pattern_Catalog.md`, 2026-10-16.
The chapter is mostly tables, and its prose has been through a deep review,
a straighten pass, a claims sweep, and the terminology rulings this month,
so the run found little.
Two edits were applied directly; this file holds no live block and stands
as the applied-directly record.
No earlier `~` review exists for this chapter; `readability_db.md` was read
and nothing below re-raises an entry there.

## Applied directly

- Line 28, §70 / treadmill: "The tables follow each source's own grouping, so each name sits where its source puts it." -> "The tables follow each source's own grouping." The second clause restated the first.
- Line 259 (*Messenger* row), list-label fragment after a semicolon: "Bundle values into one object with named attributes; the in-process form of *Data Transfer Object*." -> "Bundle values into one object with named attributes. *Messenger* is the in-process form of *Data Transfer Object*." This matches the two-sentence form of the *Surrogate* and *Inversion of Control* rows. A comma appositive was the close alternative, but it would attach to "attributes".

## Considered and declined

- Lines 22-26, the *State* / *State Machine* contrast, §31 staccato by shape ("The client supplies the inputs. The machine chooses each next state."). Kept: the short sentences set the two patterns side by side, and joining the last pair with "and" would hide the change of subject the global rules ask to split.
- Line 272, "Python includes the piece their inventors set out to supply." "the piece" is a stand-in noun, but the table right below names each piece, and the rows mix language features (`for`, a module, a function) with library calls (`copy.replace()`, `functools.singledispatch`), so one more exact noun ("feature", "mechanism") would fit some rows and not others. Bruce's line from the original draft.
- Line 247, *Inversion of Control* row, "The usual alternative to *Dependency Injection* is *Service Locator*. *Service Locator* keeps control in your code..." The repeated name is deliberate after the straighten pass; a "which" there would point at two candidates.
- Line 202, *Point-to-Point Channel*, "exactly one receiver." The precise-match use the global rule allows; it is the pattern's defining contrast with *Publish-Subscribe Channel*.
- Line 109 (*Command* row), "enabling queues, logging, and undo", §3 -ing tail and §10 triple. Kept: the triple is the GoF intent's own list of uses, and each item is a real use.
- Lines 289-290, closing triple "which algorithm to pass, which action to save for later, or which values to share." §10 by shape; each item maps to a row of the table above (*Strategy*, *Command*, *Flyweight*).
- Line 18, "dissolve in Python". A figure, but it echoes chapter 21's heading "When a Pattern Dissolves", which the link targets, so it is the book's term.
