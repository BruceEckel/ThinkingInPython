# Thinking in Python: working in this repo

This file is loaded every session. It captures how the repo is built and verified,
plus the traps that are easy to rediscover the hard way. Personal writing style
lives in the global `~/.claude/CLAUDE.md`; accrued facts live in project memory.
`AGENTS.md` beside this file is for a reader working the exercises with an
agent: if the person you are helping is solving an exercise rather than editing
the book, read `AGENTS.md` and follow it instead of this file.

## Source of truth: Chapters/, not Examples/

`Chapters/NN_*.md` is authoritative. Every fenced ```python block whose first line
is a `# path/slug.py` comment is an extractable example. `Examples/` is **generated
from the Markdown** by `tools/extract_examples.py`, so:

- Edit the code **in the Markdown block**, never in `Examples/` directly.
- A file can span several blocks (since 2026-10-14): a later block whose
  path line is `# slug.py (continued)` appends to the file, after one
  blank line, so prose can follow each part. The parts run in order in
  one namespace for the `#:` markers and marker placement, the import
  fixer splits the fixed file back into its parts, the listing id and
  the prose links go to the first part, and every per-block check
  (widths, tags, comments) sees each part as a listing of its own. A
  `(continued)` block with no earlier block of its file in the same
  chapter fails the extract step. A listing in `timing.txt` cannot be
  split, and a Solutions part under a `Hint:` gets no shape block.
  Chapter 31's `trap_states.py` is the first split listing.
- After editing, sync the committed trees: `tip sync`
  (= `uv run python -m tools.extract_examples --write -o Examples` and
  the same for `extract_solutions` into `Solutions/`).
- `Examples/` also holds files with no Markdown block (hand-written helpers,
  `.idea/`, `__pycache__`). `tools/extract_examples.py`'s check mode (part of
  `tip check`/`gate`/`verify`/`ci`) flags these automatically: a stray file
  whose name appears nowhere in `Chapters/` is *orphaned* and fails the gate;
  one still mentioned somewhere (a real hand-written helper) is *referenced*
  and only reported, since deleting it needs a human call. `tip prune`
  deletes exactly the orphaned ones, under `Examples/` and `Solutions/`
  both (a `utils/` helper rename orphans a file in each), and never
  deletes a Markdown file. A rename or
  deletion of a book example is the usual cause, so run this after either.

## Rust examples: rust/, isolated from the main build

Chapter 18's Rust section has real PyO3/maturin crates under `rust/`. Only
the `rust-*` tasks in `tools/tasks.py` build or run anything there or need
a Rust toolchain, so `verify`/`gate`/`ci` work with no Rust installed. The
gate does read `rust/`: `tip check` (and the gate's check step) runs
`extract_rust.py` in check mode since 2026-10-16, so a chapter 18 edit that
leaves `rust/fastcount/demo.py` or `src/lib.rs` stale fails the build, and
`tip rust-sync` regenerates them. Details: `rust/CLAUDE.md`.

## Effect programs: effects/, isolated the same way

Chapter 44's Koka, Flix, Scala (ZIO), and TypeScript (Effect) listings
are complete programs, extracted by `tools/extract_effects.py` into
`effects/<lang>/` from a first-line `// koka/greet.kk` path comment
(`Block.slash_slug`, shared with the Rust extractor; the fence language
picks the extractor). Only the `effects-*` tasks build or run them, each
with its own toolchain, and `tools/effects_run.py` skips a toolchain
that is not installed, so `verify`/`gate`/`ci` need none. The gate does
read `effects/`: `tip check` runs `extract_effects.py` in check mode, so
a chapter 44 listing edit that leaves `effects/` stale fails the build,
and `tip effects-sync` regenerates it. All four programs are held to one
transcript, `effects/expected.txt`, so the prompt and the greeting
change in five places together. Details and the facts the runner
depends on: `effects/CLAUDE.md`; setup and versions: `effects/README.md`.

## Cloud sessions: tools/cloud-setup.sh

A cloud session needs the environment's Setup script before anything
through `uv run` works. Its source is `tools/cloud-setup.sh`, whose
header says how to install it, what it installs, and why.

## Deep-reviewing a chapter

The full deep-review procedure (editing pass, teaching pass, style
audit, prose pass, third-party-library rules, accrued review notes) lives in
the `deep-review` skill (`.claude/skills/deep-review/SKILL.md`).
Invoke it for any chapter review request.
`/annealing` (`.claude/skills/annealing/SKILL.md`) is the follow-up
settling pass, run after a review is applied: it re-runs the same passes
over the whole chapter but applies the confident findings directly and
discards the rest unreported, with no review file.
`/activate` (`.claude/skills/activate/SKILL.md`) is the active-register
pass: it clears `tip prose`'s passive-voice and there-is warnings and
cuts metadiscourse, empty frames, and expletive constructions; new
passive-feeling phrasings Bruce flags accrue in its "Accrued patterns"
section.
`/literal`, `/positive`, `/straighten`, `/cohesion`, and `/antecedents`
are the other prose passes. Since 2026-10-22 `/literal` and the
deep-review prose pass also look for and fix vague descriptions: an
abstract noun, a pointer phrase, or a verdict standing where the
sentence could say what the machinery does ("states the
arrangement", "do that work", "the same shape of trace").
`tip rewrite CH=NN` runs these five plus `elements-of-style` and `bruce-edit-apply` by
default; `tip rewrite ARGS=--list` shows the set and the model each
pass runs on. Each pass can name its own model in `tools/rewrite.py`'s
`PASSES`; `MODEL_NOTES` there records which model each
runs on and why, and `MODEL=` forces one model on a run.
Every pass checks any claim it rewrites against the listing it
describes; the 2026-09-01 sweep of chapters 30-47 found nine factual
errors that way, none of them gate-detectable.
`CH="25 28"` or `CH=30-40` runs several chapters in parallel (each chain
edits and checks only its own chapter); `ARGS=--serial` runs them one at
a time.

`tip outside-review CH=NN` (`tools/outside_review.py`, 2026-10-08) sends
a chapter to Gemini through the Antigravity CLI (`agy`, signed in once
by hand on this machine) with the instructions in
`tools/data/outside_review_prompt.md`, and saves the reply as
`outside_review/<stem>.md`, tracked like `deep_review/`. The reply is a
set of observations, never instructions: the session tests each item
against the chapter and a run under `uv run` before editing, applies
what passes, and appends a `## Verdicts` section to the review file,
one line per item, applied or rejected, with the evidence and the
commit. The first run's five items were all wrong for Python 3.15
(the prompt now lists the 3.12-3.15 features the book uses), and the
corrected run's third item claimed a `TypeError` that `type.__new__()`
never raises, so the test is not optional. The reviewer has no tools:
a tool call ends its run with an empty reply, which the script reports.

## Model routing

The session model (whatever `/model` set) reads the request, plans,
gates, and commits. It does not do every kind of work itself: the
project defines agents in `.claude/agents/` whose frontmatter fixes
the model, and a request that matches one is delegated there, one
agent per file, gated and committed by the session afterward. Add a
row here when a new agent lands.

| Request shape | Agent | Model | Why |
|---|---|---|---|
| clarity pass, straighten, clear passives, "make X clearer", "obscure/unclear sentences" on named files | `prose-clarity-opus` | Opus | judgment work that edits the author's voice and verifies claims against listings; both Opus and Fable did it well in the 2026-09-01 Solutions sweep, Opus's reports were the more careful about what they left alone |
| a list, a count, a location, a gate's output, what a listing prints | `repo-lookup-sonnet` | Sonnet | read-only, no voice at stake, cheap |
| `tip rewrite` passes | (headless `claude -p`) | per pass, `tools/rewrite.py` `PASSES` | see `MODEL_NOTES` there |
| verify a chapter's factual claims against its listings and against the chapters it names | a fresh agent per chapter, report-only | Opus | verification fails by under-reading, not by over-editing, so `MODEL_NOTES`' result for the rewrite passes inverts here; in the 2026-09-02 calibration Opus found three real errors Fable read past, with zero false positives from either |
| deep review of a chapter, thread audits, anything that decides what a chapter claims | the session model, or a `fork` | session | needs the conversation's context; a fresh agent cannot know what Bruce has already ruled on |

Pass `model:` on an `Agent` call only to override a definition for one
run. A fresh agent costs roughly 70-150k tokens on a chapter-sized
file; a `fork` carries the whole conversation and costs several times
that, so forks are for work that needs the session's history.

## Editing passes: /edit-start and /edit-done

When Bruce says he is starting to edit a chapter, run `/edit-start NN`;
when he says he is done, run `/edit-done NN`. The skills hold the steps.
The local tag `edit-start-NN` is the only state (`git tag -l
'edit-start-*'` lists open passes), and a `SessionStart` hook prints the
open passes into every session, so a request that names no file ("fix
that sentence about closures") is looked up in the chapter in progress
first, and its Solutions file second, before asking which chapter he
means. "Apply" from him, with a chapter editor page open, means run a
round of the `chapter-editor` skill.

## Learning from editing passes

`/bruce-edit-capture` (`.claude/skills/bruce-edit-capture/SKILL.md`) reads the
before/after diff of an editing pass on a chapter, whoever made each edit
(Bruce's rule since 2026-09-28: a pass is judged by whether the chapter got
better), separates the generalizable edits from the local ones, and proposes editing practices into `bruce_edit_db.md`. It writes
only that file, never `Chapters/`. `/bruce-edit-apply`
(`.claude/skills/bruce-edit-apply/SKILL.md`) applies the promoted rules to a
chapter or the book, reporting per-rule firing counts. The split is deliberate:
capture is cheap and reversible, application rewrites prose that no gate
checks. One sighting logs a candidate; a second sighting in a different chapter
promotes it to a rule; only rules are applied. Rejected rules go to Retired and
are never re-proposed.

## The verify loop after editing a chapter

Fastest path for one chapter is `tip verify-ch CH=NN`
(`tools/verify_chapter.py`): the same fixers and gates as `verify`,
scoped to that chapter and its Solutions file, in a few seconds. It
reflows both files, as the gate does (the gate has reflowed
`Solutions/` since 2026-10-25, after a hand run brought the 45
READMEs to one sentence per line in e33ca13a),
and it writes no gate stamp; a change that other chapters depend on
(a renamed listing, a `utils/` helper, a linked heading) still needs
the whole-book run. That run is `tip verify`: fix line endings, every
mutating fixer (the comment-style fixers, import sorting, blank-line
cleanup), refresh the `#:` output markers in both trees, sync `Examples/`
and the `.py` files in `Solutions/`, build the figure gallery, then every gate but the
site build. Its ordered step list lives in `tools/verify.py`
(`VERIFY_TARGETS`), and `tip verify ARGS=--help` lists it without
running anything. The gate skips work that cannot find anything new
(`tools/skip_stamps.py`; `tools/CLAUDE.md` has the policy).
Two `verify-ch` runs at once wipe each other's `build/examples`, so
parallel runs (agents, several chapters) add `ISOLATED=1` as a tip
variable after the task name, `uv run tip verify-ch CH=NN ISOLATED=1`
(an `ISOLATED=1` environment-variable prefix is ignored and the run
uses the shared tree), which
extracts into `build/verify-ch-NN/` and reads only that tree (since
2026-10-05, after a twenty-agent sweep spent 5 to 40 retries per
chapter on the collisions); `build/verify-ch-*` can be deleted at any
time.
The marker refresh runs
*before* the sync, not after: `gate`/`solutions-gate` refresh markers
too, but only after their own prior sync step already copied the Markdown,
so a marker that needed fixing would otherwise stay one sync behind until
the next run caught it up.

Both gates and `verify-ch` also run `tools/marker_placement.py` (since
2026-10-02): a `#:` run must sit directly after the statement that
printed it, never gathered at the end of a listing. It reports and does
not self-heal; `tip marker-placement ARGS=--write` moves the runs, and
its docstring has the layout rules (import output goes below the import
block, for ruff's `I001`).

`prose_lint.py` (gated, in `verify-ch` too) fails a bare "raises"
(`BARE-RAISE`, since 2026-10-21): the verb takes an object, "raises a
`TypeError`", never "raises instead" or "raises in `__post_init__()`".
A fronted object ("the exception it raises") passes.
Prose-only edits still need `heading_links.py` (cross-references),
`banned_phrases.py`, and `check_self_reference.py` (claims the book makes
about its own chapters); all three are in `tip verify`.
So is
`check_quoted_diagnostics.py`: every quoted `ty` diagnostic's gutter
lines are compared with the extracted listing, and the dozen quotes
the book deliberately makes against an edited copy of a listing live
in `tools/data/quoted_diagnostics_baseline.txt`. A NEW entry after a
listing edit is a stale quote to requote, or a fresh deliberate edit
to accept with `tip quoted-diagnostics-accept`; `--all` lists every
hit. `exercise_refs.py` (in the gate since 2026-09-20) does the same
for prose that names an exercise by number: each "exercise N", "the
second exercise", or "the previous exercise" in `Chapters/` and
`Solutions/` is paired with the Solutions title under that number,
and the pairs live in `tools/data/exercise_refs_baseline.txt`.
Inserting or reordering an exercise changes the title under every
later number, so every reference to one turns NEW and fails the gate.
Reread each NEW sentence against the title printed beside it, fix the
number or `tip exercise-refs-accept`, and never accept without that
read: chapter 30 carried five stale numbers for a day after commit
a2cc5a98 inserted an exercise at 2, with every gate green. A new
reference is NEW too, until accepted. `tip verify-ch` sees only the
references its two files make, so after moving an exercise run
`tip exercise-refs` over the book. `tip verify`'s gate also
runs `validate_output.py --update` over all of `Chapters/` now, so a stale
`#:` marker anywhere self-heals (rewriting `Chapters/`) instead of failing
the build, the same way `fix-eol`/`sync` already self-heal other drift.
Check `git diff Chapters/` afterward: a chapter you did not touch can
still land in the diff if its output actually changed. An exception
raised where none is expected still fails the gate; only marker text is
auto-corrected. A lone bare `#: ` with nothing after it is always treated
as a not-yet-filled-in placeholder and filled in, even without `--update`.

Twelve report-only
prose checks run in `tip prose`, never in a gate, each with a baseline
of judged keeps in `tools/data/` so only new hits print (since
2026-10-03): `tip stranded` (`tools/stranded_prepositions.py`, a clause
ending on a preposition whose object moved) and `tip watch-words`
(`tools/watch_words.py`, the style guide's don't-use and avoid tiers).
`tip possessives` (`tools/stranded_possessives.py`, 2026-10-14) lists a
possessive whose head noun is elided ("not the base's"), the possessive
cousin of the stranded preposition; the sweeps that day fixed 83 and the
baseline holds the judged keeps.
`tip internal-names` (`tools/internal_names.py`, 2026-10-07) lists each
public class name, in code under `Examples/` and `Solutions/`, that no
code outside its class and no prose code span uses, a candidate for a
leading underscore; its baseline holds the judged keeps (stored
constructor data, table-driven names, double-dispatch legs,
introspection demos), and record fields are skipped by design.
`tip positional` (`tools/positional_refs.py`, 2026-10-07) lists prose
after a listing that points at a line by position ("the second
`print()`", "the last line", "line 3") or by a construct the listing
holds more than once ("the `for` loop" with two `for`s), the shapes
the tag convention replaces; a sentence that already cites a `[n]`
tag is skipped. Its baseline was seeded from the 2026-10-07 tag sweep,
which read every hit, so a new hit is a pointer to tag or a false
positive to accept (an ordinal naming an argument, a version, a
runtime call, output, or data).
`tip trailing` (`tools/trailing_tags.py`, 2026-10-18) lists two shapes
Bruce marked in chapter 31, rules R32 and R35 in `bruce_edit_db.md`: a
clause that ends on a comma, a participle, and a measure or place
("belongs in that state's row, written once"), and a transactional
connective ("in return", "the trade-off", "the cost of"). Its baseline
holds the judged keeps (a participle that describes the noun it
follows, a measured cost, a named trade-off), and chapter 31's hits
stay out of it while its editing pass is open.
`tip subject-gap` (`tools/subject_gap.py`, 2026-10-18) lists a
sentence whose subject head sits nine or more words from its verb
behind a relative clause, a participle, a "such as" phrase, or a
parenthetical ("an action that must run on every entry into that
state appears once", the chapter 31 sentence Bruce marked), the
`straighten` skill's "subject held open". It is the one check that
needs a parser: spaCy has no wheel for the pinned Python, so
`tools/spacy_parse.py` runs under `uv run --no-project
--python 3.12 --with spacy`, an environment uv caches after the
first run, and the check exits 0 with a message when that
environment cannot start. `tools/parsed_prose.py` starts that
parser, caches each file's parse under `build/parses/`, and hands
the token table to the rules, so a whole-book parse (about 24
seconds) happens once and a repeat run takes about a second. The sweep that day read 181 hits, fixed
37 (commit 0fc6e04d), and the baseline holds the keeps: coordinated
subjects, a short appositive, a relative clause that is the claim
and reads once, a parser error. Chapter 31's hits stay out of it
while its editing pass is open.
`tip sentence-shapes` (`tools/sentence_shapes.py`, 2026-10-18) uses the
same shared parse for five shapes from the style rules. The default
rules have a baseline: `[IMP]`, a command plus its consequence
("Remove `frozen=True` and the pattern fails"), `[COLON+AND]`, a
colon followed by a clause that joins a second clause with "and", and
`[PAIR]` (2026-10-26), a pair word ("between", "both", "either",
"neither") whose own phrase holds no conjunction and whose "and" or
"or" then arrives from the next clause followed by a noun phrase
("keeps state between values and the consumer has a loop": the reader
joins "the consumer" to "values" until the verb). A verb between the
phrase and the conjunction, or right after it, is quiet by design;
the book-wide read that day had 52 raw hits and 6 real ones. A
colon after a count or a demonstrative ("three parts:", "this
shape:") is skipped. The survey rules print only under `ARGS=--survey`
and never enter the baseline: `[AND]`, an "and" that joins two clauses
with different subjects, and `[COLON]`, a colon followed by an
independent clause. The author's own rewrites fire `[AND]` six times in
the calibration, so the shape is a judgment made per sentence. Use
`tip sentence-shapes CH=31 ARGS=--survey` at the start of a chapter
pass. `ARGS=--calibrate` runs all five rules over
`tools/data/edit_pairs.json` and the style rules' own examples.
`tip passive` (`tools/passive_voice.py`, 2026-10-19) reads the same
parse for passive clauses: a verb with a passive auxiliary and a passive
subject. `[PASSIVE]` names no actor, and `[PASSIVE+BY]` writes the actor
out in a by-phrase, the form most often worth turning around. Vale's
write-good `Passive` rule matched by word pattern and flagged an adjective
after "be" ("is unchanged"), which the parse skips, so `.vale.ini` turns
it off since 2026-10-19: of its 29 alerts the parse confirmed 19 and the
other 10 were adjectives, and the parse found 50 passives Vale missed.
The 2026-10-19 read fixed 13 and the baseline holds the keeps: a passive
whose actor is unknown ("Java is statically compiled"), a quoted
diagnostic, a naming convention ("is called *Multiton*"), a state
adjective, and a parser misread of a compound or a possessive.
`ARGS=--calibrate` compares the two rules over the book and lists the
hits that both flag, that only Vale flags, and that only the parse flags.
`tip past-tense` (`tools/past_tense.py`, 2026-10-19) enforces the style
rule that standing behavior takes the present tense. It reads the same
parse for a simple-past verb or a participle with a past auxiliary ("was
built", "had loaded"). The default rules, held to a baseline, are
`[PAST]`, the past verb of a main clause ("One design served three jobs
in this chapter"), and `[PAST-HEADING]`, a past verb in a heading ("What
Stayed Constant"), which the check reads from the document's own heading
lines. The first run found 1283 hits, nearly all in subordinate clauses
("the function the caller passed"), which refer back inside present
narration and are not the drift. `[PAST-SUB]` therefore prints only under
`ARGS=--survey`, for the activate pass, and is never baselined. Skips
print nothing: a sentence with a year, a version number, or a PEP number
(a dated event), a sentence with a modal (would, could, might, should), a
verb inside double quotes, a `Hint:` or `Done when:` paragraph, a
main-clause past whose subject is "I" or "we", and an "If" or "When"
sentence with "were". The baseline holds the keeps: a narrated run, a
measurement, and history without a year.
`tip expletives` (`tools/expletives.py`, 2026-10-19) enforces the style
rule of no "there is" and no empty "it is" frame, from the same parse.
`[THERE]` is the existential "there" (a token with dep `expl` whose verb
has no subject of its own), including the negated "there is no X".
`[IT-IS]` is the extraposed "it is easy to add" or "it is true that"
frame. There is no cleft rule, because the parse cannot tell "it is X
that" from "it is a NOUN that" with an antecedent. Vale's write-good `ThereIs` rule matches "There is/are" by word
pattern; `ARGS=--calibrate` compares it with the `[THERE]` hits, lists the
ones that both flag, that only Vale flags, and that only the parse flags,
and runs the built-in examples. The baseline holds the keeps: a quotation
the quote count missed, and an `[IT-IS]` "it" with a real antecedent.
`tip pointers` (`tools/pointer_words.py`, 2026-10-19) is a survey tool
that runs outside `tip prose`, reads the same parse, and keeps no
baseline. `[THIS]` is a sentence-opening demonstrative pronoun ("This is
the fast path"). `[IT]` is an opening "it" or "they" whose previous
sentence holds two or more nouns of the matching number (subjects,
objects, or complements), listed on the line as the candidates, or that
opens its paragraph. The calibration found it fires on the author's
rewrites about as often as on his originals ([THIS] 1 before-only, 0
both, 2 after-only; [IT] 1, 0, 1, of 72 pairs). The `antecedents` skill
reads its list per chapter (`tip pointers CH=NN`), and each hit is a
judgment that pass makes.
`tip negatives` (`tools/negation_density.py`, 2026-10-19) is a second
survey tool outside `tip prose`, with no baseline.
It counts, per paragraph, the style rule's family of negatives: the
parse's `neg` dependency, no/none/nothing/never/without/unless, verbs
like omit, lack, and fail, un-/non- and -less words, with the
restrictive `only` shown apart.
A paragraph at three or more (`--threshold N`) prints as `[NEG n +k only]
word, word x2: text`, and a per-file table of negatives per 1000 words
and the line `N paragraphs at >= 3 in F files` follow;
`--top N` keeps the N densest paragraphs.
The `positive` skill reads it per chapter (`tip negatives CH=NN`), and a
listed paragraph is a candidate for that skill's test, not a fault.
`tip italics` (`tools/italics.py`, 2026-10-23) lists italics that break
the introduce-once rule: `[EMPHASIS]` a span of function words ("*is*",
"defers *how*"), `[REPEAT]` a term italicized again in the same file,
and `[EARLIER]` a term italicized after the file's prose already used
it. Pattern names and capitalized titles are skipped. Run over the 15
chapters as they stood before that day's hand sweep (cd9c4045), it
flagged 32 of the 38 lines the sweep changed; a verb or adjective
stressed at its first use ("*suppresses*") is beyond it. The baseline
holds the judged keeps: a defining sentence for a term the earlier
prose used loosely, and a principle or pattern name (*Subtraction*,
*Reactor*) italic on every mention.
`tip stranded-accept`, `tip possessives-accept`, `tip watch-words-accept`,
`tip internal-names-accept`, `tip positional-accept`,
`tip trailing-accept`, `tip subject-gap-accept`,
`tip sentence-shapes-accept`, `tip passive-accept`,
`tip past-tense-accept`, `tip expletives-accept`, and `tip italics-accept` add the current
new hits to the baseline after a human read; `ARGS=--all`
lists every hit.
`CH=NN` scopes an accept the way it scopes the report (since
2026-10-23): it adds and drops entries for that chapter and its
Solutions file and leaves every other file's entries alone, so one
chapter's accept never takes in another chapter's unread hits.
`tip internal-names-accept` reads code, not prose, and takes no `CH=`.
The 2026-10-03 sweeps read every hit: 87 strandings fixed and 84
accepted, 610 watch words fixed and 220 accepted (a `want` with a
human subject, an arithmetic `even`, a `never` that is the claim, a
heading echoed in link text). Chapter 31's hits are left for its open
editing pass and are kept out of the stranded, watch-words, and positional
baselines, so they stay NEW until that pass closes.

## Exercise statements in Solutions/ are generated

The block quote under each `## N.` heading in `Solutions/` is the
chapter's exercise statement, copied by `tools/exercise_statements.py`
(`tip statements`, since 2026-10-02, after issue 16). The chapter is the
source: edit the exercise in `Chapters/`, and `tip verify`, `tip gate`, or
`tip verify-ch` rewrites the quote. A hand edit to the quote is
overwritten on the next run. The tool owns the block quote that starts at
the first non-blank line after a numbered heading, so a solution that
opens with a quotation of its own needs a sentence in front of it. Links
in the copy gain the `../../Chapters/` prefix, and `exercise_refs.py` skips
the copied lines. A solution's heading and its quoted exercise now sit
together, so read the pair when a solution changes: a solution that
answers a different exercise from the one quoted above it is the drift
`check_solutions.py` cannot see.

Each chapter with exercises carries one sentence under its
`## Exercises` heading that links `../Solutions/<its own stem>/`,
so a reader on GitHub can click through. `check_solutions.py` fails a
chapter whose link is missing or names another folder, which a chapter
rename leaves behind; `tip fix-solutions-links` inserts or corrects it.
The wording is the author's to change; the gate holds the target.
`build_site.link_solutions()` rewrites the link: on the site to the
chapter's `<stem>.solutions.html` page, and in the EPUB and PDF, which
carry no Solutions pages, to the GitHub URL.

**Solutions layout (2026-10-02).** A chapter's solutions are
`Solutions/<chapter>/README.md`, the authored Markdown, and the `.py`
files beside it are generated by `tip sync` and are never edited by
hand. Tools find the file through `tools/repo.py` (`solutions_file()`,
`chapter_stem()`), not by building a path, because a solutions file's
own stem is `README`. `--prune` deletes orphaned `.py` strays and never
deletes Markdown.

## Solutions reveal in steps: `tip steps`

A solution whose section opens (after the generated quote) with a
paragraph beginning `Hint:` is folded by `tools/solution_steps.py`
(`tip steps`, in `gate` and `verify-ch` since 2026-10-02) into nested
`<details>`: "Where to look" (the hint), "The shape" (each listing
with its function bodies elided, generated), then "Solution" (the
rest, as authored). A paragraph beginning `Done when:` directly after
the hint (since 2026-10-17) adds a "Done when" step between "The
shape" and "Solution": an authored criterion the reader checks before
opening the solution. Every "Solution" step ends with a generated
self-diagnosis paragraph (`DIAGNOSIS` in the tool): name what
separates your attempt from this one, a different design, a detail,
or an equivalent alternative. GitHub and the site render the ladder
collapsed, so a reader opens one step at a time; `tip hint CH=30 N=3`
prints the same steps one per run. The `<details>` lines, the four
`<summary>` labels, the diagnosis paragraph, and every block starting
`# The shape of` are tool-owned and rewritten on every run; edit the
hint, the `Done when:` criterion, the prose, and the listings inside
the ladder, never the tags. A solution without a `Hint:`
paragraph is left flat. Every Solutions file has had ladders since
c6271a94 (2026-10-02); the two flat answers left are chapter 38's
combined ones ("4 and 5", "6, 7, and 8"). The site renders each Solutions file as
`<stem>.solutions.html` beside its chapter (`tools/build_site.py`,
`write_solutions_page()`), with `solutions.js` remembering which
steps a reader opened; the EPUB and PDF still link GitHub. A shape
block carries no `#:` marker and no path comment, so the extractor
and the marker validator skip it, and the widths check still reads
it.

## Pyright: a periodic review, never a gate

`ty` is the only checker the gates run.
Pyright's disagreements with `ty` live in `tools/data/pyright_baseline.txt`,
and `tip pyright-review` prints the delta;
the `tool-upgrade` skill has the workflow and the history.
Three rules hold everywhere:

- **Nothing pyright-related joins `verify`, `gate`, `sweep`, or `ci`.**
- **No listing carries a pyright suppression.**
  An accepted disagreement is a baseline entry instead.
- **"The type checker" in prose means `ty`.**
  A sentence that holds for `ty` alone names `ty` and says what the other checkers do.
- **Name `ty` only where the sentence needs that checker** (Bruce, 2026-09-29,
  after PR #15 read `` `ty` sees `` as a typo for `try`): a contrast with
  Pyright or mypy, a version pin, a `ty` command or setting, a diagnostic
  name, or behavior known to be `ty`'s own. Everywhere else write "the type
  checker". In Part I (chapters 02-10) the first `ty` a chapter keeps reads
  "the type checker (`ty`)"; from chapter 11 on, a bare `ty` is fine.

## What the book says about itself

`check_self_reference.py` gates the shape that produced the most errors
in the 2026-09-02 correctness sweep: prose asserting something about
another chapter, or about the book, that reading the named place
disproves. Chapter 07 said "[Rethinking Objects] uses it" of
`slots=True`, and chapter 20 contains the string "slot" zero times. The
link resolved, the anchor was fine, every gate was green.

Two rules gate, because a substring search settles them. `absence`
catches "X appears nowhere else" where X is used elsewhere, searching
code spans and listings only, since the book's type names are also
English words ("a more complex design" must not disprove a claim about
`complex`). `direction` catches an ordering phrase that names a chapter
("an earlier chapter") within 80 characters of a link pointing the other
way.

A third rule, `grounding`, needs a model's verdict, so a new
misattribution passes the gate until `tip grounding-triage` runs.
Run it after editing a sentence that links another chapter.
`tools/CLAUDE.md` has how it works, and how `tip link-support`,
`tools/prose_calibration.py`, and `tip edit-patterns` work and what
their calibration found.

The rules are literal and under-report by design: a claim with no code
term in it is invisible to them. They are a floor, not a substitute for
reading.

## Pattern names: *Capitalized* and italic, every mention

Every naming of a design pattern is written capitalized and in italics,
on every mention, in prose and in link text: *State*, *Chain of
Responsibility*, `[*Template Method*](24_...)`. Names like State, Command,
Bridge, and Proxy are ordinary words otherwise, so this is the exception
to the global "italics only to introduce a term" rule. Headings stay
plain, and the lowercase word keeps its ordinary sense ("an observer
registers"). `tools/pattern_names.py` checks it (`tip pattern-names`)
and `tip fix-pattern-names` rewrites the unambiguous cases; the names
and the excluded phrases (`!State Machines`) are in
`tools/data/pattern_names.txt`. State/Command/Bridge at a line start
are listed only with `--sentence-start`, for a human to judge. As of
2026-10-06 it lists four lines in `Chapters/` and six in `Solutions/`,
all the ordinary word: the verb ("State the rule...") in nine and the
noun ("State that changes with each call") in chapter 17. The check has
been in `GATE_CHECKS` since 2026-09-16, so `verify`, `gate`, and
`verify-ch` fail on a plain name. Since 2026-10-06 the gate runs it
over `Solutions/` too: a hint that links a section by its title
italicizes the pattern name inside the link text,
`[The Classic *Visitor*](...)`, and a section title that uses the
word in its ordinary sense ("Intrinsic and Extrinsic State") gets a
`!` exclusion. A bold step label that opens with the verb
("**State the precondition in the strategy.**") counts as a sentence
start and joins that listing.

## Listing tags: `# [n]` in code, `` `[n]` `` in prose

Prose that walks a listing line by line points at a line with a tag,
not with "the first line" or "the `for` loop" (Bruce, 2026-10-07: a
positional phrase makes the reader count, and a construct name fails
when the listing has two of that construct). The tag is a trailing
comment `# [1]`, `# [2]`, ... on the code line, numbered from 1 in
order within one listing, and the prose refers to it as a code span,
`` `[1]` ``, never bare: the EPUB and PDF concatenate the chapters, so
one stray `[1]:` definition anywhere would turn every bare `[1]` into
a link. Name the construct instead when the listing has one of it and
the prose mentions it once; tags are for an ordered walk. The tag
counts toward the 60-column width, so a tagged line near the limit is
split (`prop = announcing(...)  # [3]` then `setattr(...)  # [4]`) or
carries the tag on its own line above it, which refers to the line
below. `tools/listing_tags.py` gates it (`tip listing-tags`, in
`GATE_CHECKS`): tags run 1..n in order, every tag is referenced in the
prose before the next listing or heading, every `` `[n]` `` resolves
to a tag in the nearest listing above, and a bare `[n]` in prose is a
finding. Chapter 30's `broadcasting.py` is the first tagged listing.
`# [1]` passes ruff as configured and under `--preview` (pycodestyle's
E262 rejects `#1`, `#(1)`, and `#<1>`, every form with no space after
the hash), which is why the bracket form was chosen over them.

## Diagrams: hand-authored SVGs, some generated

A figure is an SVG in `resources/images/`, referenced as `![caption](_images/<name>)`.
Never hand-edit a generated one:
each pattern chapter's story figure, and several body figures, from its module in `tools/story_figures/`,
and chapter 21's `coupling_gallery.svg` from `tools/coupling_panels.py`;
edit the spec and run its `tip fix-*` task.
Load the `figures` skill (`.claude/skills/figures/SKILL.md`) before drawing or editing any figure.
It holds the caption rules, the palette, the arrowheads, and what `tip figures` checks.

## `@record`: the book's frozen data class, from chapter 18 on

`utils/record.py` (chapter 18, `#record`) is
`dataclass(frozen=True, slots=True)` under
`dataclass_transform(frozen_default=True)`. From that section on, a
frozen data class in a listing is written `@record` with
`from record import record`, and the prose noun is "record". Chapters
12, 13, and 15 come before the definition and keep
`@dataclass(frozen=True)`. Since 2026-09-26 the decorator is
dual-form (bare or called, two `@overload`s, the `cls is None` test
from chapter 14's optional-parentheses section): `@record(slots=False)`
is `dataclass(frozen=True)` without slots, the one option it forwards.
Bruce's rulings from 2026-09-17, revised 2026-09-26:

- **A base the book owns gets an empty `__slots__ = ()` so its frozen
  subclasses are records.** Chapter 20's `shapes_oo.py` teaches it;
  chapter 34's `Node` and `Operators` (and every Solutions copy),
  Solutions 34's `Entry`, and chapter 29's `WhatIWant` carry it
  without comment.
- **A class whose base is a library's and declares no `__slots__` is
  `@record(slots=False)`:** the `Ability` and `Time` subclasses in
  chapters 46-47. So is a listing that reads the instance `__dict__`
  or pickles across versions (chapter 36's `sketch_v1.py`/
  `sketch_v2.py`, Solutions 36's `drawing_v1.py`/`exercise_7.py`),
  and those four are listed in `record_exceptions.txt` since their
  bases are slotted. The flag makes dropping slots a visible choice;
  never put a bare `@record` on a class and let a base take the
  slots back.
- **A class that needs an option `record()` lacks keeps `@dataclass`
  written out:** `order=True` (chapter 28), a weak reference
  (`weak_pool.py` and Solutions 35 exercise 5 are
  `@dataclass(frozen=True, slots=True, weakref_slot=True)`, one
  `__weakref__` slot and still no `__dict__`, since 2026-09-26), a
  `cached_property`.
- **Reword a sentence before keeping a listing long-form for its
  sake.** A sentence that names `frozen=True` about a converted class
  says "record" instead. The exceptions are listings whose subject is
  `frozen=True`: chapter 20's `immutable.py` and `frozen_leaky.py`,
  Solutions 20 exercise 2, chapter 18's `frozen_vs_slotted.py`. Chapter
  28's `still_a_tuple.py` and `tuple_ordering.py` (and Solutions 28
  exercise 6) stay long-form too: `FrozenColor` reads the same in both,
  and `tuple_ordering.py` sets it beside its `order=True` twin, so the
  one added option is the point of the comparison.
- **A Solutions copy of a chapter class follows its chapter listing.**
- Slots make an instance smaller, so a marker that measures memory
  moves when a class becomes a record. Solutions 35 `exercise_2.py`
  went from a ratio near ten to near six.

`tools/record_check.py` gates three shapes (`tip records`, in
`GATE_CHECKS` and in the Solutions checks since 2026-09-17): a
`@dataclass(frozen=True)` or `@record(slots=False)` whose bases are all
slotted fails unless `tools/data/record_exceptions.txt` lists it, a
bare `@record` under a base with no `__slots__` fails, and a
`record(...)` call with any argument but `slots=False` fails. A base it cannot see (imported from
another listing) draws no finding, so it under-reports by design. The
exceptions file is keyed by chapter *name* (`Rethinking_Objects`), not
number, so a renumbering leaves it alone and a chapter rename does not.
Run alone, `tip records` also fails on an entry that matches nothing.
Its `UNSLOTTED_LIBRARY` names Stateless's `Ability` and `Time`, and
chapter 47 says in prose that `Ability` declares no `__slots__`; recheck
both against `.venv/Lib/site-packages/stateless/` on a Stateless
upgrade.

Project memory `record-sweep-classification` has the per-class survey
and how it was measured.

## Traps (learned the hard way)

- **Listing line length is 60** (ruff `line-length` plus the `widths` check
  in `check_all.py`, which also covers fragments and `#:` markers that ruff
  never sees). The one sanctioned overflow is a trailing `# type: ignore`
  pragma, exempted by both ruff and `widths`. A `#:` marker wider than 60
  means the program's own printed output must shrink, not the marker.
  Wrapped imports use packed parentheses with per-file `I001` ignores in
  `pyproject.toml` (ruff would otherwise force one-name-per-line); a new
  over-60 import needs its file added there. A scratch dir's `ruff` uses
  the default 88, so **line length must be verified against
  `build/examples`**, not a temp file.
- **Run `ty`/`ruff`/`pytest` against `build/examples/`** (via `uv run`), never a
  loose scratch file, or config/imports resolve differently.
- **Bare `python`/`ty`/`pytest` on PATH can be a different, older tool than
  `uv run`'s.** They matched on 2026-09-13 (both `python` 3.15.0rc2, both
  `ty` 0.0.78); on 2026-10-11 `uv run python` moved to 3.15.0 final
  while bare `python` stayed the python.org 3.15.0rc2 installer, and
  they had diverged before: bare `python` was 3.14.6
  while `uv run python` was the pinned 3.15, and bare `ty` was 0.0.46
  against `uv run ty`'s 0.0.56. Running `validate_output.py` with the
  older bare `python` produced false failures on 3.15-only syntax
  (`sentinel`, `lazy import`, the PEP 798 comprehension-unpacking
  chapter) that vanished once invoked via `uv run`. Always go through
  `uv run` for anything that executes example code; never assume bare
  `python`/`ty`/`pytest` matches it. Bare `python` is also a different
  *build* of the same version. Since 2026-10-22 bare `python`,
  `python3`, and `py` all start the Python install manager's per-user
  CPython (`AppData/Local/Python/pythoncore-3.15-64`, 3.15.1 that
  day), a python.org build with the JIT compiled in
  (`sys._jit.is_available()` is `True`), while `uv run` uses uv's
  managed build, where it is `False`. `sys.version` tells the builds
  apart: "tags/v3.15..." is python.org, "main, ..." is managed.
  Before that date the python.org build lived at `C:/Python/python.exe`
  and there was no `python3` on PATH. The install manager replaced
  that build, and every environment created on it broke. A `uv tool`
  install (`tip`, `black`) then fails with "did not find executable at
  'C:\Python\python.exe'", and `uv tool install --reinstall` fails the
  same way, since it queries the old interpreter first; `uv tool
  uninstall` followed by `uv tool install --managed-python ...`
  rebuilds it. `[tool.uv] python-preference = "only-managed"` in
  `pyproject.toml` (2026-09-17) keeps a fresh clone or worktree's
  `uv sync` off the PATH interpreter; before that, uv's default
  preference picked the python.org build, and a scratch worktree
  reported two JIT markers as changed for that reason alone.
- **CPython's small-int cache is wider on the pinned 3.15 than the
  textbook `-5..256` range.** Confirmed cached up to at least 1024 on
  the beta and again on 3.15.0 final (2026-10-11). An example meant to
  show an "uncached" int needs a value safely
  above that (100000+), not just above 256, or the demo silently proves the
  opposite of what the prose claims. See project memory
  (`small-int-cache-extended-py315`) for the chapter-36 case this broke.
- **`#:` output markers must equal stdout exactly.** For nondeterministic output,
  round floats (`f"{x:.6f}"`) or print `type(e).__name__` instead of a message.
  A wall-clock threshold boolean is the exception: register it in
  `tools/data/timing.txt`, and `validate_output.py` treats its markers as
  claims, never auto-rewritten. On a mismatch it reruns the block, up to
  three runs in all, and passes as soon as one matches the committed
  marker; only a marker that misses every run fails, loudly, and the fix
  is then a human decision. Any *other* genuinely nondeterministic
  listing still self-heals silently under `--update` and can thrash
  between values, so don't assume a marker mismatch is repo drift: run
  the extracted script directly (`build/examples/<chapter>/<file>.py`)
  to check the value is stable, and if it's a timing boolean, add it to
  `timing.txt` instead of accepting the auto-fix.
- **A `#:` marker for output an `import` produced cannot hug that import.**
  Markers otherwise sit directly after the statement that produced them, but a
  marker placed after the last import sits *inside* the import block, and ruff's
  `I001` ("Import block is un-sorted or un-formatted") fails the gate.
  `validate_output.py` accepts either arrangement, so this surfaces at `tip
  lint`/`tip verify`, a step after the edit looked correct. Close the import
  block with its blank line first, then put the marker below it, directly above
  the code it precedes. Chapter 6's `package_only.py` was annealed into the
  hugging form and broke the build; its neighbors `using_packages.py` and
  `from_packages.py` already had the right shape.
- **A seeded simulation can still print differently on Linux.** Solutions
  38's `exercise_8.py` seeds its `random.Random`, and the gate in the WSL
  clone rewrote one of its `#:` readings anyway (`0.012` on Windows,
  `0.010` on Linux, 2026-09-24). The seed fixes the random draws; the
  C library's `cos` does not agree to the last bit between Windows and
  glibc, and a chaotic run (a kick that throws a grain across the plate
  each step) multiplies that last bit by about ten a step until a
  three-decimal reading moves. The chapter's own `chladni_plate` marker,
  at the default kick, matched on both. The fix was two decimals in that
  one listing, which both platforms print alike; do not reseed, and do
  not accept the Linux rewrite, which the next run's drift check then
  fails on. A `git diff` on a simulation marker after a Linux run is
  this until proven otherwise.
- **Async timing markers flip silently on Windows timers.** A `#:` trace
  that depends on ordering between asyncio deadlines needs wide margins.
  Chapter 19's `task_group.py` cancellation demo with 0.01/0.02/0.03s
  sleeps let task "a" complete before cancellation landed (b's failure
  and a's deadline fell inside one timer tick), and the self-healing
  gate rewrote the marker to contradict the prose. Use roughly 5-10x
  gaps between competing deadlines (0.01/0.05/0.25), widest where a
  cancellation must propagate, and treat any `git diff` on a timing
  marker as a red flag to investigate, not drift to accept.
- **Chapter 19's `gil_threads.py` boolean flips under machine load, and
  widening its threshold would be wrong.** `thr > seq * 0.9` asserts "threads
  bought no speedup," and `tip verify` runs during back-to-back gates
  (including inside `tip release`, twice in a row) rewrote it to `False`,
  contradicting the prose one line below. Do not widen the band to make it
  robust: at `0.7` a genuinely 30%-faster threaded run would still report "no
  faster," hiding the exact regression the listing exists to catch. The fix
  is in `thread_compare.py`'s `compare()`, which the neighboring I/O
  listing also uses: the two variants are timed alternately, five rounds,
  `min` of each, so a load burst lands on both.
  The listing is registered in `tools/data/timing.txt`,
  so a flip fails validation loudly instead of rewriting the marker.
  Do not shrink the loop to make the script faster. At 200,000 iterations each timed round is ~0.075 s,
  about five Windows scheduler quanta (~15 ms), so one lost quantum is
  a 20% error and the boolean flipped inside a quiet `tip verify`;
  at 1,000,000 a round is ~0.38 s and a quantum is 4%. The ratio
  itself is ~1.02 at either size, so the margin over 0.9 is thin and
  only the long measurement absorbs scheduler noise. The script's
  timeouts under the parallel runner were fixed on the runner side
  instead: `run_examples.py`'s default `--timeout` is 60 s (was 15).
- **Thousands of live `asyncio` tasks in one process can wedge Windows'
  `ProactorEventLoop` for every later `asyncio.run()` call in that process.**
  Chapter 19's `task_vs_thread_memory.py` used to create and cancel 20,000
  tasks. Run standalone (its own process, one `asyncio.run()` ever), that's
  instant. Run through `validate_output.py` (which execs every chapter's
  blocks, including every later `asyncio.run()` block, in one process), it
  triggered a storm of `RuntimeError: loop ... is not the running loop`,
  one per orphaned task, that took minutes to print and looked exactly like
  a hang — the `KeyboardInterrupt`s a human sends to escape it then get
  misattributed to whatever line happened to be executing next, in that or
  a later chapter. Bisected the threshold on this machine: 15,000 tasks ran
  clean, 20,000 didn't. Fixed by dropping `TASKS` to 5,000, comfortably under
  the cliff. If a future example needs a large task count again, verify it
  through `validate_output.py` on the real chapter file (not a standalone
  script run), since only the multi-`asyncio.run()`-per-process path
  reproduces this.
- **On Windows a listing can hang inside `asyncio.run()` before a line
  of its own code runs.** The event loop's self-pipe comes from
  `socket.socketpair()`, which CPython emulates with a loopback TCP
  connection, and the emulation's `accept()` blocks forever when the
  connect fails silently. A `faulthandler` dump on 2026-09-29 showed one
  validator worker inside that `accept()` and the rest idle; two of
  twelve whole-book runs hung on an idle machine, chapter 47 each time
  it was identified. Why the connect fails is not known. Since that
  date `validate_output.py` watches each file's process and reruns one
  that reports nothing in `--file-timeout` seconds (120; the log says
  "no result after 120s; rerunning (2/3)"), and `run_examples.py`
  reruns a timed-out example once. `pytest` fails a test after 120
  seconds (`pytest-timeout`, `timeout` in `pyproject.toml`, since
  2026-09-29) and prints every thread's stack; a timeout on a test
  that starts an event loop is this, so rerun it. A hang or a timeout on a listing that calls
  `asyncio.run()` is not evidence against the listing.
- **`build/` is derived and gitignored.** `extract_examples.py --write` now wipes
  the target under `build/` first, so a fresh sync is the fix for weird drift or a
  stale tree. A stale `build/examples/` was behind "phantom" timeouts/import errors.
- **Windows dir-lock on the wipe.** If the persistent shell's cwd sits inside
  `build/examples/<chapter>`, that open handle blocks the rmtree and
  `extract_examples.py --write` dies with `PermissionError [WinError 32]`. Keep the
  shell at the repo root and run chapter-dir commands in a subshell, e.g.
  `(cd build/examples && uv run ty check NN_Chapter)`.
  Orphaned python processes cause the same error: on 2026-09-03,
  worker/load-test processes left behind by subagents (ProcessPool
  workers, synthetic-load loops) held `build/examples/<chapter>` long
  after their agents finished, and `tip verify` died at the extract
  step. After a multi-agent run that executed listings, check
  `Get-Process python` before a verify and kill strays rooted in this
  repo's `.venv`. Also: piping `tip` through `tail` swallows its exit
  code; capture `$?` or redirect to a log instead.
- **Renumbering, renaming, or splitting a chapter** touches files and prose that no single gate covers.
  Follow the `rename-chapter` skill (`.claude/skills/rename-chapter/SKILL.md`).
- **Every chapter filename carries its part name, set off by `--`:**
  `NN_<Part>--<Chapter_Name>.md`, as in `08_Foundations--Static_Types.md`,
  `18_Techniques--Performance.md`, `34_Patterns--Composite_and_Interpreter.md`,
  `42_Functional--Error_Handling.md`, `47_Effects--Stateless_in_Practice.md`.
  The part name is the one in `build_site.PARTS`, so renaming a part renames its
  chapters' files. `01_Introduction.md` stays bare: `PARTS` starts Part I at 02,
  so chapter 01 belongs to no part. The H1 carries only the chapter name
  (`# Static Types`), so the filename and the URL say which part a chapter is in
  while the book's own title stays short. Filename stem and H1 therefore never
  match; do not "fix" one to the other.
  Keep `_` as the separator right after the number: `build_site.py` and
  `check_solutions.py` both pull the chapter number with `split("_", 1)[0]`.
  The link regexes restrict which characters a filename may use;
  the `rename-chapter` skill lists them and says why brackets fail silently.
- **Footnote labels are book-wide.** The EPUB and PDF concatenate every
  chapter, and pandoc keeps a `[^label]:` definition's first occurrence,
  so two chapters sharing a label show the first chapter's note in the
  second; the site, one page per chapter, hides it. `footnotes` in
  `GATE_CHECKS` (`tools/footnote_labels.py`) fails on it since
  2026-09-16, after release 0.5.9 went out with chapter 17 showing
  chapter 11's `parametrize` note.
- **Anchors:** pandoc auto-slugs a heading (backticks/punctuation dropped, but `.`
  is kept). Give headings an explicit `{#id}` when the auto-slug would be ugly
  (e.g. anything containing `type[...]` or `__init__`). `heading_links.py` gates it.
- **A new third-party dependency may not install on the pinned Python.**
  `requires-python` tracks a bleeding-edge version (3.15, a beta from the book's
  start until its final release on 2026-10-11), so a package can lack a wheel for it (source
  build then fails) or refuse outright (its own installer version-guards).
  Before committing a new dev dependency: add it to `pyproject.toml`, run
  `uv sync`, and if it fails, revert (`git checkout -- pyproject.toml uv.lock`)
  and re-sync rather than fighting the build. See project memory for the
  numpy/numba case and the workaround for illustrating a chapter example
  anyway.
- **A `ty` or Stateless upgrade is a book-wide event.**
  New inference breaks listings, and lost inference breaks them too.
  The `tool-upgrade` skill (`.claude/skills/tool-upgrade/SKILL.md`) holds the procedure,
  the version-pinned probes, and what each past upgrade broke.
  Follow it after any upgrade, which you never start yourself (see below).
- **A decorator that registers a class must register what a slotted
  `dataclass()` returns, and under `ty` it cannot build that class by
  calling `record(cls)` on its `type[E]` parameter.** `slots=True` makes `dataclass()` create and
  return a new class, since a class's slots are fixed at creation, so
  `EVENTS.add(cls)` before the call files a class that no instance
  belongs to. Chapter 27's `tagged_bus.py` builds first and registers
  `built`; the one-word swap to `slots=True` without that died at import
  with "Announce: not an @event". The same goes for any registering
  decorator stacked *under* `@record`: it would see the pre-slots
  class. None exists in the book, and `tip records` would not catch
  one. Separately, `ty` mistypes
  `record(cls)` on a `type[E]` parameter, so `tagged_bus.py` calls
  `dataclass(frozen=True, slots=True)(cls)` directly; the
  `tool-upgrade` skill has the probe to re-run on each upgrade.
- **A `type X = ...` alias's right side is lazily evaluated (PEP 695),** so it
  can name a class defined later in the same file with no string quotes, e.g.
  `type Bins = dict[type[Trash], list[Trash]]` above `class Trash:`. Confirmed
  both at runtime and under `ty check`.
- **Effect signatures stay written out in full; don't fold them into
  `type` aliases.** Chapters 46 and 47 spell every Effect signature out
  (47 carries the wrapped five-way union): the union is the information,
  and it stays visible at the point of use. On `ty` 0.0.91 a
  `type X = ...` alias as a generator's return annotation checks the
  same as the spelled-out form (an undeclared Ability draws
  `invalid-yield` through the alias), but an inference gained in one
  release can vanish in another, so re-run the probe on each `ty`
  upgrade (`stateless-partial-handling-ty-support` in project memory
  has it) before trusting an alias there. Chapter 45 has no Effect
  signature, so this entry does not apply there.
- **Never auto-run `tip tools-upgrade` or `tip python-upgrade`.** Both mutate
  tracked files (`uv.lock`, and `.python-version`/`pyproject.toml` with `TO=`) and
  can invoke real system package managers (`winget`/`brew`). Only run them when
  the user explicitly asks for that specific run, not to "verify" a change.
  `tip tools-check[-full]`, `tip tools-status`, and `tip sweep` are all
  safe to run freely (the first two are read-only; `sweep` writes only
  `build/`). The nag that `gate` prints when the tools are stale is a
  reminder for the author, not an instruction to you: never act on it by
  running an upgrade.
- **`tip gate` hides half its failures, and not the half you would guess.**
  `solutions-gate` is a *prerequisite* of `gate`, so the entire Solutions
  half runs before gate's own recipe starts. One red `gate` after a
  wide-reaching change therefore shows the Solutions failures and hides
  every `Chapters/` one behind them. Use `tip sweep` (runs every check
  over both trees, reports all failures, exits nonzero if any failed)
  whenever the first failure is unlikely to be the only one. A tool
  upgrade is the standard case, and `tools-upgrade` now ends with it.
- **A green `tip sweep` does not mean the committed trees are current,
  and does not mean the `#:` markers are right.** `sweep` runs checks,
  coupling-panels, solutions-numbering, ty, lint, run, and test, each
  over both build trees. It does *not* run `check` (the `Examples/` and
  `Solutions/` `.py` drift check) or `output-check`. Editing a listing in
  either Markdown tree therefore leaves its committed copy stale behind
  a green sweep, and a stale marker survives too. `tip verify` covers
  both, through `sync` and `output`. When iterating with `sweep`, run
  `tip check output-check` before believing the tree is clean.
- **A `#:` marker that measures memory or time is a claim about the
  process the gate runs it in, not about a standalone run.** Chapter
  35's `exercise_2.py` prints a `tracemalloc` peak ratio; standalone its
  first line reports 6.1 every time, and under `validate_output.py`,
  which execs the block alongside everything else, it reports the
  committed 6.2. (Before `Tile` became a `@record` on 2026-09-17 the
  pair was 9.8 and 9.9; the slotted `Tile` is smaller, so the ratio
  fell.)
  The gate's context is the authoritative one. Before "fixing" such a
  marker, reproduce it the way the gate does, or you will correct a
  value that was already right.
- **Appendix B's `check_files.py` marker is a self-check, and the gate
  will rewrite it without complaint.** The listing runs the Effect
  checker on six of its own files and on `utils/result.py`, and its
  `#:` lines show rows for the three edge functions, their module, and
  `result.Ok.bind ['Unknown']`. The prose says every core function is
  absent from that output, which is the appendix's claim that the core
  is pure. An edit to any checker listing (`effect_table.py`,
  `call_names.py`, `function_facts.py`, `local_types.py`,
  `infer_rows.py`, `row_check.py`) or to chapter 42's `utils/result.py`
  can add an
  unresolvable call: a method on a loop variable, on a record's field,
  or on an imported constant. `validate_output.py --update` then adds
  the new `Unknown` rows to the marker and the gate stays green while
  the prose turns false. Treat any `git diff` on that marker as a
  finding. The fix is to give the checker a written type (an annotated
  parameter, a small helper), as the appendix's "four changes"
  paragraph describes, and never to accept the changed marker.
  `greeting_check.py` and `third_party_stub.py` carry findings in their
  markers too, with prose tied to each line.
- **Prose in `Chapters/*.md` follows Semantic Line Breaks** (one sentence per
  line; a sentence still too wide breaks further at a top-level `,`/`;`/`:`).
  `gate` (so `verify`/`all`/`ci`) runs `reflow_prose.py --write`, so
  hand-edited prose self-heals (rewriting `Chapters/`) the same way line
  endings and `#:` markers do; expect rewrapped lines in `git diff
  Chapters/` after a verify. A paragraph that fails reflow's round-trip
  check is skipped, reported, and still fails the gate, so a rewrite can
  never silently change rendered output. `tip reflow CH=NN` still
  targets one chapter when iterating.
- **`ty` narrows a PEP 661 `sentinel()` parameter imprecisely if the
  annotation names the generic `sentinel` class instead of the specific
  value.** `dunder: Sequence[str] | sentinel` lets `ty` narrow the `is
  ALL_DUNDERS` branch, but the other branch keeps a bogus `sentinel &
  ~ALL_DUNDERS` type (some other sentinel value, not `Sequence[str]`), which
  then fails `name in dunder`. Naming the specific value instead,
  `Sequence[str] | ALL_DUNDERS`, fixes it: the union has only two members, so
  ruling one out via `is` leaves exactly `Sequence[str]`. See `display.py` in
  chapter 17 (Metaprogramming); project memory `typing-construct-hierarchy`
  has the fuller case study.
- **Every class, even an empty one, carries compiler-generated dunders that
  always differ from `object`'s own** (`__module__`, `__dict__`,
  `__firstlineno__`, `__annotate_func__`, `__static_attributes__`,
  `__weakref__`, `__doc__`). A filter meant to report "dunders this class
  redefined," built by comparing each dunder to `object`'s version, must
  restrict that comparison to a known allowlist (chapter 17's
  `INTERESTING_DUNDERS`) or it leaks all of this bookkeeping as false
  positives. `__static_attributes__` itself is new in CPython 3.13+: a tuple
  of names assigned via `self.X` anywhere in the class's own methods.

## Pointers

- `tools/` is a package: run a tool as `uv run python -m tools.<name>`
  from the repo root, not as `python tools/<name>.py` (a bare script
  cannot import its siblings, which are `tools.config`, `tools.repo`,
  and so on). The `tools_` prefix the shared modules used to carry is
  gone; the package namespace does that job. `tools/README.md` explains.
- `tools/*.py` all have thorough module docstrings; read them before guessing.
- A listing name in backticks in the prose (`registry.py`) becomes a link
  to that listing in the site and the EPUB at build time
  (`tools/listing_links.py`). Never write those links by hand in
  `Chapters/`; a plain code span is the source form.
- `tip` replaces make: `tools/tasks.py` holds every task (`tip help`),
  `tools/tip.py` runs them, and `uv run tip ...` works with no install.
- Detailed conventions and decisions are in project memory (`MEMORY.md` index).
- `thinking-in-python-skill.md` (repo root) and
  `.claude/skills/thinking-in-python/SKILL.md` are duplicate copies of the
  same Python coding-style skill, not a symlink (this repo has
  `core.symlinks = false`). Edit one, then copy the change into the other;
  `tip skill-copies` (in the gate since 2026-10-14, `tools/skill_copies.py`)
  fails when they differ.
