# Deep-review carry-forward

Distilled 2026-08-09 from `deep_review/` (48 files, ~21,000 lines) before that
directory was deleted.
Every file was tracked, so the full text of any review is recoverable:
`git show ce118d4:deep_review/~19_Concurrency.md`, or
`git log --diff-filter=D -- deep_review/` to find the deleting commit later.

**What a fresh deep review should do with this file.** Read it before writing
findings, the way the skill's carry-forward step used to read the previous
`~`-prefixed review. Two things here are binding: a rejection must not be
re-proposed, and a standing exemption must not be re-flagged. Everything else
in the old reviews was either applied to the chapters already (so a fresh read
sees the result) or promoted into `CLAUDE.md` and project memory.

---

## Standing rejections

Bruce declined these. Do not propose them again, in any wording.

**01_Introduction: "wrote a message" stays vague.** The review flagged
"Eventually I even wrote a message confirming I was not going to complete it"
for not saying where (a blog post, a repository note, a mailing list).
Declined. The sentence stands as written.

*Correction, 2026-08-10:* this slot originally recorded a different
rejection, "do not name the `stateless` library in the Part V summary."
That inverted the actual outcome. In `~01_Introduction.md` (recoverable at
`8660e7c1^`) each checkbox sat *above* its block; the "name the library"
block's box was empty, the change was applied in commit 33a65808, and the
chapter has named `stateless` ever since, surviving the later annealing and
style passes. The two real 01_Introduction rejections in that file were the
"AI Trigger Warning" move (recorded below) and the "wrote a message"
vagueness (now recorded above).

**01_Introduction: do not move the "AI Trigger Warning" section.** The review
proposed moving it (about a quarter of the chapter) from between "How the Book
Is Organized" and "The Examples" down to after "Resources", so the reader gets
the instructions uninterrupted. Declined. Keeping the AI disclosure early is
the deliberate choice; the section stays where it is.

**39_Pattern_Catalog: do not add a conclusion or exercises.** The review
proposed either a closing three-sentence passage or two exercises, on the
grounds that the chapter currently stops on a table row and also closes Part
III. Declined. (The separately-proposed "Patterns Python Absorbed" table *was*
accepted and is in the chapter; that is not the rejected part.) Chapters 39 and
41 are the book's only two without exercises, and the absence is deliberate for
both.

---

## Standing exemptions

Each of these was examined by a past review, judged correct as written, and
recorded so the next pass would not raise it. They look like violations of a
rule the book otherwise follows, which is exactly why they keep getting
flagged.

**18_Performance: `slots.py`'s hand-written `__init__` is a teaching case.**
The house-style audit greps `def __init__(self` across `Chapters/` to catch
classes that should be dataclasses. In chapter 18 the only hit is `slots.py`,
and it is deliberate: the very next listing is the `@dataclass(slots=True)`
version, and the pair is the point.

**41_Functional_Toolkits: `recursion.py` teaches two things on purpose.** The
listing carries both the base-case/recursive-case lesson and
`sys.getrecursionlimit()`, with an `import sys` serving only the second. That
breaks "one new thing per listing". Splitting it would leave a two-line second
listing, which is worse, and the depth limit is discussed in the very next
paragraph. Left as is.

**34_Composite_and_Interpreter: the three-walker paragraph is not a
misplaced conclusion.** "Three walkers over one set of nodes is the pattern
pair in full …" reads like a chapter ending with a whole section after it. Read
twice and left alone: it closes the three-walker arc, "A Template Is a Tree" is
explicitly framed as an extension, and that section ends on the chapter's
strongest sentence, which a trailing summary would flatten. If a future pass
disagrees, the cheapest fix is a demotion ("… in full for a nested grammar"),
**not** a move or retitle: `02_Tour.md`, `33_Visitor.md`,
`39_Pattern_Catalog.md`, and `44_Effect_Management.md` all link to headings in
this chapter by anchor.

**22 → 33: the load-bearing-`Any` thread is consistent; do not "fix" either
end.** Chapter 33's "This `Any` is chosen, unlike the one in Data Transfer
Objects…" matches chapter 22's "no checker knows your attribute names". Both
were verified against `ty`: `Messenger` attribute access is
`unresolved-attribute` without the `Any`, and `SimpleNamespace` attribute
access reveals `Any`. Chapter 33's link deliberately carries no anchor, because
chapter 22's `Any` discussion sits in the unheaded intro.

**08_Static_Typing: the missing blank line after `# area.py` is
load-bearing.** House style would add one, but the chapter quotes `ty`'s
diagnostic verbatim including `--> area.py:6:12`, and the call sits on line 6
only because that blank line is absent.

**05_Functions: `sentinel()` really does build a new object per call.** PEP
661 sentinels are widely described as caching per name and module, which would
make the chapter wrong. Verified on the pinned interpreter:
`sentinel('MISSING') is sentinel('MISSING')` is `False`. The prose and the
`#: MISSING` marker are correct; do not "correct" them.

**17_Metaprogramming: the sentinel unions name values, not the class.**
`greenhouse.py` and `utils/display.py` annotate `EventMaker | NOT_CREATED` and
`Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS` rather than the generic
`sentinel` class. That is what makes `ty` narrow the other branch. Also
`_redefined()` restricts its comparison to `INTERESTING_DUNDERS` on purpose.
Both are recorded in `CLAUDE.md`.

---

## One open item, never resolved

**03_Containers: the `deque` threshold boolean.** A review proposed tightening
`print(deque_time * 20 < list_time)` to `* 50`, matching the neighboring
listing. It was reported rather than applied because it edits a timing boolean
and the supporting numbers came from a noisy shared Linux box, not Bruce's
machine (ratios of 414/364/401 at the listing's `n = 20_000`; 8/25/31 at
`n = 2_000`). Still unconfirmed on the real machine. Leave it at `* 20` unless
someone measures there.

---

## What was deliberately not carried

- **Per-chapter verification snapshots.** Chapters 01 and 18 had long "verified
  and correct" sections (external links resolving, `sys.getsizeof` figures,
  call counts, PyPI wheel availability, timing margins measured 8-of-8). Those
  are point-in-time and several are already stale by design (NumPy/Numba wheel
  support moves). A fresh review re-verifies what it depends on; that is the
  job.
- **Applied-directly lists.** Every entry describes an edit already sitting in
  `Chapters/`. A fresh review reads the current text.
- **Live blocks that were applied.** Their result is in the chapter.
- **Technical traps.** These were already promoted to `CLAUDE.md`'s "Traps
  (learned the hard way)" and to project memory (`MEMORY.md` indexes ~50
  entries, most originating in these reviews). Those two files are the live
  home for that knowledge, not this one.
