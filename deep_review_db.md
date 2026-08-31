# Deep-review carry-forward

Two generations of `deep_review/` have existed. Both are gone from the working
tree; both are recoverable from git.

- **First generation**, 48 files and roughly 21,000 lines, distilled 2026-08-09
  and deleted in `8660e7c1`. Recover any file with
  `git show 8660e7c1^:deep_review/~19_Techniques--Concurrency.md`.
- **Second generation**, 47 chapter files written 2026-08-11 by a full sweep on
  the `deep-review-sweep` branch (one `review/NN_*` branch per chapter, merged
  in), then followed by a readability pass (`7f165a08`), `/anneal` everywhere
  (`8db5c64a`), and `/activate` (`200ab2de`, `8e15ddb9`, `bb81711a`). Distilled
  into this file 2026-08-13 and deleted. Recover any file with
  `git show bb81711a:deep_review/~03_Foundations--Containers.md`.

One caveat on recovering a second-generation file: the 2026-08-13 cleanup
corrected two pieces of bookkeeping in the working tree and then deleted the
directories in the same change, so those corrections are in this file but not
in `bb81711a`. A recovered `deep_review/~NN_*.md` shows an unchecked
`[] Reject` on the four blocks listed under "Decisions made and applied"
below, all four of which Bruce accepted; and a recovered `readability/NN_*.md`
lacks the `~` completion prefix even though its findings were applied. Trust
this file over the recovered ones on both points.

**What a fresh deep review should do with this file.** Read it before writing
findings. Two things here are binding: a standing rejection must not be
re-proposed, and a standing exemption must not be re-flagged. Everything else
was either applied to the chapters already (so a fresh read sees the result) or
promoted into `CLAUDE.md` and project memory.

---

## Standing rejections

Bruce declined these. Do not propose them again, in any wording.

**01_Introduction: "wrote a message" stays vague.** The review flagged
"Eventually I even wrote a message confirming I was not going to complete it"
for not saying where (a blog post, a repository note, a mailing list).
Declined. The sentence stands as written.

**01_Introduction: do not move the "AI Trigger Warning" section.** The review
proposed moving it (about a quarter of the chapter) from between "How the Book
Is Organized" and "The Examples" down to after "Resources", so the reader gets
the instructions uninterrupted. Declined. Keeping the AI disclosure early is
the deliberate choice; the section stays where it is.

**39_Patterns--Pattern_Catalog: do not add a conclusion or exercises.** The review
proposed either a closing three-sentence passage or two exercises, on the
grounds that the chapter currently stops on a table row and also closes Part
III. Declined. (The separately-proposed "Patterns Python Absorbed" table *was*
accepted and is in the chapter; that is not the rejected part.) Chapters 39 and
41 are the book's only two without exercises, and the absence is deliberate for
both.

**Do not narrate tool-version history.** Two 2026-08-11 blocks proposed keeping
a record of what `ty` used to get wrong (46_Effects--Stateless's PEP 695 alias gap,
47_Effects--Stateless_in_Practice's citation of it). Both rejected, with the reason:
*"Just modernize everything. I don't want a history of 'what didn't used to
work'."* This generalizes past those two chapters. When a tool upgrade makes a
caveat obsolete, delete the caveat rather than dating it, and never add prose of
the form "before version X this failed". The traps worth keeping live in
`CLAUDE.md`, which is for the author, not in the book's prose.

---

## Decisions made and applied

Four blocks from the 2026-08-11 round were accepted and are in the chapters.
Recorded here so a later review does not re-raise the same gap as a new finding.

- **02_Foundations--Tour** gained exercise 6, a prediction exercise for negative floor
  division (`-9 // 4` and `-9 % 4`), with its solution in `Solutions/02_Foundations--Tour.md`.
  The chapter's sharpest fact for a C or Java reader had no exercise.
- **06_Foundations--Modules_and_Packages** gained `exporting.py` and `star_import.py`
  demonstrating `__all__` and the underscore convention, plus exercise 6.
  "What a Module Exports" had been the chapter's only section with neither a
  listing nor an exercise.
- **18_Techniques--Performance**: the NumPy section became a real tested listing.
  `numpy>=2.5.2` is a dependency in `pyproject.toml`, and `vectorize_numpy.py`
  is fenced, with a threshold boolean and `report()` numbers in the house style.
  Numba stays an indented illustration (numba 0.66.0 tops out at cp314), as does
  the Rust demo, which needs both.
- **30_Patterns--Observer**: exercise 2 was reworded to describe the game
  `Solutions/30_Patterns--Observer.md` actually implements. The exercise had described a
  spread-outward rule while the solution implemented classic Flood-It.

---

## Standing exemptions

Each was examined by a past review, judged correct as written, and recorded so
the next pass does not raise it. They look like violations of a rule the book
otherwise follows, which is why they keep getting flagged.

**Hand-written `__init__()` is deliberate in a dozen classes.** This is the most
repeated false positive in the book. The house-style sweep greps
`def __init__(self` across `Chapters/` and re-finds the same set every time.
Each has a recorded reason: dataclasses are not taught until chapter 12, so
chapter 10's `Node` and `Resource` cannot use them; `leaky.py` and `plugged.py`
(ch. 20) exist to show underscore-private fields behind properties;
`OverStream` (ch. 23) transforms its argument (`iter(source)`) and seeds derived
state; `History` (ch. 36) and `StateMachine` (ch. 31) rename what they store,
which a generated `__init__()` cannot express; `Sketch` (ch. 36) is the mutable
originator deliberately contrasted with the frozen `Drawing`; the `singleton`
decorator class (ch. 24) matches chapter 14's `repeat`; `PizzaBuilder` (ch. 27)
is framed as a direct translation of a Java workaround; and the minimal wrapper
stand-ins in chapters 26, 29, 30, and 38 would gain a second topic from
dataclass machinery in listings whose one new thing is the pattern. Chapter
18's `slots.py` is the same call: the very next listing is the
`@dataclass(slots=True)` version, and the pair is the point.

**"Which X Should You Use?" headings keep their question form.** Chapters 22,
24, 27, 31, and 35 all use it for decision sections. The heading-style rule bars
"You Can/Must" modal clauses, not questions, and renaming one instance would
break the set.

**Part I chapters end on Exercises with no conclusion section.** Chapters 02
through 07 share the shape. It is the tour-part convention, not a missing
summary.

**`#:` markers gathered at a listing's end after an `if __name__` block.**
Hugging the code would put an indented marker inside the block, and no indented
`#:` exists anywhere in `Chapters/`. End-of-listing is the established shape for
`__main__` demos (`use_module.py`, `point_distance.py`, `leaky.py`).

**Repeated italics on pattern names.** Part III italicizes `*Observer*`,
`*Proxy*`, `*Command*` and the rest on every use, not only the first. Chapter 26
has thirteen `*Proxy*`. This is house convention, not the
italics-for-emphasis violation it resembles.

**41_Functional--Toolkits: `recursion.py` teaches two things on purpose.** The
listing carries both the base-case/recursive-case lesson and
`sys.getrecursionlimit()`, with an `import sys` serving only the second. That
breaks "one new thing per listing". Splitting it would leave a two-line second
listing, which is worse, and the depth limit is discussed in the very next
paragraph.

**34_Patterns--Composite_and_Interpreter: the three-walker paragraph is not a misplaced
conclusion.** "Three walkers over one set of nodes is the pattern pair in
full ..." reads like a chapter ending with a whole section after it. Read twice
and left alone: it closes the three-walker arc, "A Template Is a Tree" is
explicitly framed as an extension, and that section ends on the chapter's
strongest sentence, which a trailing summary would flatten. If a future pass
disagrees, the cheapest fix is a demotion ("… in full for a nested grammar"),
**not** a move or retitle: `02_Foundations--Tour.md`, `33_Patterns--Visitor.md`,
`39_Patterns--Pattern_Catalog.md`, and `44_Effects--Effect_Management.md` all link to headings in
this chapter by anchor. The same applies to the "A Template Is a Tree" heading
itself, which chapter 2 links by explicit anchor.

**22 → 33: the load-bearing-`Any` thread is consistent; do not "fix" either
end.** Chapter 33's "This `Any` is chosen, unlike the one in Data Transfer
Objects…" matches chapter 22's "no checker knows your attribute names". Both
were verified against `ty`: `Messenger` attribute access is
`unresolved-attribute` without the `Any`, and `SimpleNamespace` attribute
access reveals `Any`. Chapter 33's link deliberately carries no anchor, because
chapter 22's `Any` discussion sits in the unheaded intro.

**08_Foundations--Static_Types: the missing blank line after `# area.py` is
load-bearing.** House style would add one, but the chapter quotes `ty`'s
diagnostic verbatim including `--> area.py:6:12`, and the call sits on line 6
only because that blank line is absent.

**05_Foundations--Functions: `sentinel()` really does build a new object per call.** PEP
661 sentinels are widely described as caching per name and module, which would
make the chapter wrong. Verified on the pinned interpreter:
`sentinel('MISSING') is sentinel('MISSING')` is `False`. The prose and the
`#: MISSING` marker are correct; do not "correct" them.

**17_Techniques--Metaprogramming: the sentinel unions name values, not the class.**
`greenhouse.py` and `utils/display.py` annotate `EventMaker | NOT_CREATED` and
`Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS` rather than the generic
`sentinel` class. That is what makes `ty` narrow the other branch. Also
`_redefined()` restricts its comparison to `INTERESTING_DUNDERS` on purpose.
Both are recorded in `CLAUDE.md`.

---

## Resolved, and no longer open

**03_Foundations--Containers: the `deque` threshold stays at `* 20`.** A first-generation
review proposed tightening `print(deque_time * 20 < list_time)` to `* 50` to
match the neighboring listing, and it was carried for months as an open item
because the supporting numbers came from a noisy shared Linux box rather than
Bruce's machine. Measured on the real machine 2026-08-11, five standalone runs:
list/deque ratios 82, 83, 83, 86, 93. `* 50` would leave under 2x headroom and
the self-healing gate would flip the marker under load; `* 20` keeps roughly 4x.
(`membership_cost.py`'s `* 100` was measured at the same time: ratios 5000+,
ample.) Settled. Do not reopen without new measurements on that machine.

**09_Foundations--Class_Attributes: the `ty` augmented-assignment gap closed.** `ty` 0.0.70
flags `self.total += 1` on a `ClassVar` (`invalid-attribute-access`), so the
chapter's old "passes with zero diagnostics" claim stopped holding.
`counter_near_miss.py` now carries a `# type: ignore`, exercise 7 asks what
`ty` reports instead of why it accepted the code, and both
`Solutions/09_Foundations--Class_Attributes.md` and `Solutions/12_Techniques--Data_Classes_as_Types.md`
(exercise 6, `self.built += 1` on a frozen class) were rewritten to match.

---

## What was deliberately not carried

- **Applied-directly lists**, the bulk of both generations. Every entry
  describes an edit already sitting in `Chapters/`. A fresh review reads the
  current text.
- **Chapter-local declined judgments**, roughly 200 of them in the second
  generation. Each is a one-off weighing (a heading's wording, a listing's
  self-containment, whether a section needs one more exercise) justified where
  it was made. Only the judgments that generalize across chapters are above.
- **Per-chapter verification snapshots.** Chapters 01 and 18 had long "verified
  and correct" sections (external links resolving, `sys.getsizeof` figures, call
  counts, PyPI wheel availability, timing margins measured 8-of-8). Those are
  point-in-time and several are stale by design. A fresh review re-verifies what
  it depends on; that is the job.
- **Technical traps.** Already promoted to `CLAUDE.md`'s "Traps (learned the
  hard way)" and to project memory (`MEMORY.md`). Those two files are the live
  home for that knowledge, not this one.
