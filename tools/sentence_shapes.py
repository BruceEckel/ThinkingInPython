#!/usr/bin/env python
"""Report sentences with an imperative-plus-consequence, a split-worthy "and", a colon-led clause, a pair word's stray conjunction, or an additive adverb with an open focus.

Five sentence shapes from the author's style rules, found with the
dependency parse that `tools/parsed_prose.py` caches under
`build/parses/` (spaCy, run in a throwaway Python 3.12 environment; see
that module). Each hit carries its rule label at the start of the
printed sentence.

`[IMP]`, imperative plus consequence: the sentence root is a bare
imperative verb (tag `VB`, no subject, not an infinitive after "to")
and a verb coordinated with it through "and" has a subject of its own.
"Remove CODE and the pattern fails" commands the reader and then
reports what happens; the repair is the condition, "If you remove
CODE, the pattern fails". The second clause's subject may be anything,
"you" included, but it must be a plain `nsubj` or `nsubjpass`. Two
imperatives ("Try the operation and handle the exception") and an
exercise ("Run CODE and read the error it reports") are not hits,
since the second verb has no subject. Two exclusions keep exercise
sentences out: a coordinated verb with a wh-word child (tag `WP`,
`WDT`, or `WRB`) or a `mark` child ("that", "whether") is a wh-clause
or that-clause, not a consequence ("Explain both failures, and why an
intermediate kick avoids them"); and the `csubj` fallback below fires
only when the "and" joins the imperative to the finite root.

`[AND]`, an "and" that joins two clauses with different subjects: the
root is a finite verb with a subject, a verb coordinated with it
through "and" is finite and has its own subject, that second subject
is not a bare pronoun (it, they, he, she, this, that, which, who,
these, those), and its text differs from the first. The test is
substitution: if "but", "so", "while", or "whereas" fits where the
"and" sits, the "and" is not additive, and the sentence splits. Only
the root clause is examined, and a sentence is reported once.

`[COLON]`, a colon followed by an independent clause: after a ":" in
the sentence, a subject whose head is a finite verb that also follows
the colon. A colon is a pointer to what the lead-in announced (a list,
an example, a restatement), so a clause after it is often a reason or a
claim of its own, and the colon stands in for "because" or a period.
`[COLON+AND]` is the stronger label for the same shape when that
clause's verb is coordinated through "and" with a second verb that has
its own subject: a colon delivers one thing, and the first claim takes
a period. A sentence earns one of the two labels. A spaCy sentence
that ends on a colon is merged with the sentence after it in the same
paragraph before the rule applies, since the parser splits there. The
style rules keep a colon after a count or a demonstrative that names
what follows ("three parts:", "this shape:"), so a colon is skipped
when a non-punctuation word before it is a number (pos `NUM`) or one of
`COUNT_WORDS` ("both", "two", "several", "pair"), or when the last such
word is one of `POINTER_WORDS` ("this", "these", "following", "here").
A bare noun lead-in ("The prediction:") stays a hit.

`[PAIR]`, a pair word whose conjunction arrives from the next clause
(2026-10-26, from a sentence the author marked in chapter 45): a word
that promises a pair, "between", "both", "either", or "neither"
(`PAIR_WORDS`, each with the conjunction that completes it), whose
governed phrase holds no such conjunction, followed by that
conjunction with no punctuation (`PAIR_BREAKS`) and no verb between,
and then a noun phrase (`PAIR_NOUN_START`). "The producer keeps state
between values and the consumer has a loop of its own": the reader
joins "the consumer" to "values" as the pair's second half and backs
up at "has". The repair closes the pair word's phrase before the next
clause starts ("from one value to the next while the consumer has"),
or puts a comma before the conjunction. The phrase is the object's
subtree for "between" and the head's subtree for the other three, so
"both" before a verb ("CODE both creates X and appends Y") holds its
own "and" and is quiet. Two shapes are quiet by design, from the
book-wide read that day (52 hits, 6 real): a verb between the phrase
and the conjunction settles the pair word first ("both forms keep the
result and the name"), and a verb after the conjunction resolves the
misreading at once ("leaves both loops in one step and skips CODE"),
so only a noun phrase after the conjunction counts. A complete pair
the parser attaches elsewhere ("between the check and the use can
reset", "either a CODE the author typed or an CODE") still reports,
and the baseline holds those.

`[AND+REL]` (2026-10-26, from a sentence the author marked in chapter
45) is the `[AND]` shape where the first clause already carries a
relative clause (a `relcl` token) or an opening parenthesis before the
second subject: "CODE supplies one as CODE, which produces CODE, CODE,
CODE, and so on without end, and CODE has an CODE of the same shape".
The second claim rides as an afterthought on a sentence that was
already full, so the first takes a period. It is the "weight" tell of
the style rule's "and" bullet, and the only part of the `[AND]` shape
precise enough to baseline: of the 927 `[AND]` hits that day, 11 had
this shape, 5 were split, and the 6 keeps are Done-when criteria,
which list several conditions in one sentence by design. A sentence
earns `[AND+REL]` or `[AND]`, never both.

`[ADD]` (2026-10-28, from a sentence the author marked in chapter 45)
is an additive adverb whose focus the sentence leaves open. "also",
"too", "as well", and "likewise" (`ADDITIVE_WORDS`) say that
something joins a set the previous sentence established, and the
reader has to decide which constituent is the new member. When the
sentence's subject differs from the previous sentence's, the subject
is the first candidate ("the generator, too, keeps its place"), and
a writer who meant the predicate ("its place, as well as its
variables") is misread: "A closure keeps its captured variables
between calls. The generator keeps its place as well" said that the
closure keeps its place. Both readings are open whenever the subject
is new, so the rule fires on a root-clause additive adverb in a
sentence whose root subject's lemma differs from the previous
sentence's root subject (same paragraph), the subject not a bare
pronoun (`BARE_PRONOUNS`, plus "we", "you", "I", "one"), since a
pronoun carries the previous subject on. The degree "too" ("too
easy": "too" followed by anything but punctuation), the pair "not
only ... but also", and "as well as" (a conjunction, not the tag)
are not additive here and are skipped, and so is an adverb in a
subordinate clause. The repair names the thing added ("keeps its
locals and its place", "copies on the way in as well as on the way
out") or lets another word carry it ("removes that last change").
The book-wide read that day had 178 hits and 17 real ones, so the
rule is a survey rule: most additive adverbs with a new subject do
mean the subject ("Pyright accepts the read too"), and the reader
cannot tell which from the parse. Since 2026-11-09 its read hits are
kept in the judged baseline described under `[SAME+NEW]` below. The
reread that day covered the 153 standing hits: 4 rewritten (three
named the thing added, "accept `bpackage` as well as `bPackage`";
one dropped an "also" with nothing to add to) and 149 kept. A kept
hit's reading depends on the sentence before, so an `[ADD]` hit prints
both, `[ADD] sentence | after: previous sentence`, and its baseline
entry holds both: an edit to either sentence retires the entry.

`[TWO]` (2026-10-28, from a sentence the author marked in chapter 45
as "hard to follow") is a comparison whose two terms each carry a
modifier of their own, so the reader holds two unfinished pictures
and the relation between them in one clause: "`drive()` answers a
request yielded two generators deep the same way it answers one from
`interview()`'s own body." The comparator is "the same way", "the
same X as", "as X as", "like", "unlike", "rather than", "instead
of", "compared with", or "differs from" (`comparator()`). The first
term runs from the root verb to the comparator, the second from the
comparator to the end, and a term is heavy (`heavy_side()`) when it
holds four or more content words and among them a verb ("a request
yielded two generators deep", "it answers one from `interview()`'s
own body"), the mark of a stretch the reader builds rather than
reads. The rule fires when both terms are heavy.
The repair introduces each picture in its own sentence and then
states the relation ("The requests now come from `ask()`, one
generator below `interview()`, and `yield from` passes each one up
to the driver, so `drive()` sees the same `Question`s it saw in
`interview_generator.py`"), or drops a modifier the context already
supplies. "Use a `set` rather than a `list`" is quiet, because both
terms are light. It is a survey rule because weight is a judgment:
two heavy terms the reader already knows can ride in one clause.
Since 2026-11-09 its read hits are kept in the judged baseline
described under `[SAME+NEW]` below. The reread that day covered the
84 standing hits and rewrote none: 62 are comparisons that read once
(two bare verb phrases around "rather than", terms already on the
page, exercise statements) and 22 are not the shape (an idiom such
as "as soon as", or "like" meaning "such as").

`[CAN]` (2026-10-30, from a sentence the author marked in chapter 20)
is a modal "can" standing where the sentence reports what happens:
"A test can catch the broken contract", said of the test the next
sentence describes, is "A test catches the broken contract". The
style rule keeps "can" for a standing capability, and the reader
takes "can" as possibility, so a "can" on an event that does occur
hedges a fact. The rule (`can_event()`) fires on an `aux` token
with lemma "can" whose head is a lexical verb (so "can be" is
quiet) in the root clause or a verb coordinated with the root,
with no negation ("cannot" is a claim about ability) and no
"also", "still", "even", or "always" on the verb, whose subject is
a thing rather than a person (`PERSON_SUBJECTS`: "you", "we", "I",
"one", "reader", "programmer"), in a sentence with none of
`OPTION_WORDS` ("if", "when", "whenever", "unless", "whether",
"while", "until", "once", "either", "or", "any", "anything"), which
mark a condition or a choice and so a real capability. The repair
is the plain present ("catches", "reaches", "reports"). It is a
survey rule because the parse cannot tell a capability stated as
a fact ("a `set` can hold any hashable object", "`survey()` can
delegate to either") from an event hedged with "can"; the reader
of the list asks whether the sentence describes what the thing on
the page does, and writes the present if so.

`[CAUS]` (2026-11-09, from a heading the author marked in chapter 45)
is a causative verb whose object is the real actor and whose
infinitive is the real event: "`close()` Requires the Generator to
Finish", Bruce: "see how passive that is? Maybe something like:
'`close()`: the generator must finish.'" The sentence is grammatically
active, but the generator, which must act, is the object of
"requires", and finishing hangs off it as an infinitive, so the
actor is demoted. The same shape: "`close()` requires the generator
to finish", "the decorator lets the caller skip the check", "the
registry allows a subclass to register itself", "`slots=True` makes
`dataclass()` build a new class". The repair puts the actor in
subject position with its own verb or modal ("the generator must
finish", "the caller can skip the check", "`dataclass()` builds a
new class under `slots=True`"). The rule (`causative()`) fires on a
`CAUSATIVES` verb (a `VERB`, not passive) with a noun object, the
`dobj` of the verb or the `nsubj` of the complement, followed by a
verb complement (`xcomp` or `ccomp`). The parser sometimes reads
"requires the generator to finish" as a preposition "to" with the
verb as its `pobj`, so that reading counts too. The message leads
with the three words: `[CAUS] requires CODE finish: ...`. Quiet by
design: a passive causative ("is required to define it", which is
`tip passive`'s), an adjective complement ("makes the check safe"),
a pronoun object ("lets us", "let's"), and a noun object with no verb
complement ("needs a lock"). It is a survey rule because "need" and "want" often take a
purpose infinitive that is not the actor's event ("a lock to hold"),
"let" and "make" fire on imperatives ("Let the type checker infer
the rest") and titles ("Making Classes Work"), and the reader of the
list asks whether the object is the one that acts; "get", "have",
"expect", and "help" were dropped from the list the day it was
written, since their hits were purpose infinitives and perfects. The
first book-wide run had 308 hits.

`[SAME]` (2026-11-01, from a sentence the author marked in chapter 45)
is a "same" with nothing to compare against: "At CODE, the same CODE
raises CODE", said of a generator with one `yield`. "Same" has one
job, saying that two things the reader could take as different are
one thing or alike. When the noun has one referent on the page and
nothing is compared, "same" only means the one just mentioned, which
"the", "that", or "its" already says, and the sentence is a pointer
dressed as a comparison. The repair is the pointer ("its CODE", "That
directory reaches pytest", "uses this self-registration"). The rule
(`same_pointer()`) fires on a "same" whose previous token is a
determiner or possessive (`SAME_DETERMINERS`), in a sentence with none
of `COMPARISON_WORDS` ("as", "than", "both", "each", "and", a count)
and none of the "no matter" and "for any" sequences, and not in an
idiom (`same_idiom()`: "same way", "same time", "same place",
"same reason", "of the same", "the same with", "stays the same",
"reads the same", a subject pronoun opening a relative clause right
after it, or "same" before sentence punctuation as a predicate). It is a survey rule because the
parse cannot tell an implied second term ("for the same reason
`bump()` does", "The same approach isolates a database") from none.
The book-wide read that day covered 194 candidates and rewrote 6, so
the keeps dominate. On 2026-11-09 the R63 sweep read every "same" in
the book, and the 143 hits standing that day were reread in context
before they were recorded: 4 were rewritten and 139 kept. The 4 were
a noun the passage had not used ("the same bracket" beside "one
setup, one teardown"; "the same declaration" and "the same
substitution", each with a cognate in another sense inside
`[SAME+NEW]`'s window) and a "same" said of two different things
("The same cycle appears at the group level", a second cycle). Since
then `[SAME]` shares the judged baseline described under `[SAME+NEW]`
below.

`[SAME+NEW]` (2026-11-09, from the author's "same as what" on a
chapter 45 sentence and the read of the close calls that followed) is
a "same" on a noun the passage has not used: "CODE uses the same
separation to check each value", where nothing above says
"separation" or "separate". "Same" sends the reader back to match the
noun against an earlier mention, and the search finds none, because
the writer coined a noun for something the passage had described in
other words ("the same hazard" for a missing attribute, "the same
shallowness", "the same machinery"). The repair says what the thing
is ("checks each value while it is still separate from the literal
text") or uses the noun the passage did use ("this design" before,
so "the same design", not "the same model"); rule R63's sixth test in
`bruce_edit_db.md`. The rule (`same_new_noun()`) takes each "same"
after a `SAME_DETERMINERS` word, finds the noun it modifies in the
parse, and fires when no word in the `SAME_NEW_WINDOW` source lines
above the "same" (prose, listings, and headings alike), and no word
earlier in its own paragraph, is a `cognate()` of that noun: equal
light stems, stems sharing five letters and all but two of the
shorter one ("separate" answers "separation"), or an identifier that
holds the noun (`singledispatch` answers "dispatch"). Quiet by
design, each because the sentence supplies the second term: a command
(an exercise or a step label); a noun that is a code span or has one
before it; a `SAME_NEW_QUIET` noun (way, time, place, reason, and the
property nouns of "of the same name"); a counted noun ("the same two
files"); a `SAME_NEW_PLACES` preposition before the determiner ("in
the same file", "a list with the same elements"); a second term
attached to the noun, "as", "that", or "which" after it or a new
noun phrase that opens a relative clause ("the same `cls` it
received"); a subject that is plural, coordinated, or counted
("Every responder writes the same comparison"); and a "same" spread
over repeats or cases ("the same answer every time", "the same call
on each element", a second "same" in the sentence). The hit names the
noun: `[SAME+NEW] separation: ...`. It is a survey rule because the
window is a line count, not the reader's memory, and a summary noun
for the sentence before ("faced the same problem", "uses the same
technique") is often the plain way to say it. The first book-wide run
had 117 hits and the read rewrote 20: a noun the passage had under
another name ("the same generic caretaker" for `History`, "the same
question" for a request), a "same" that was untrue ("the same limit"
ahead of "both limits"), and a term stated only afterward. The other
96 were keeps. Reprinted on every run, they would make a chapter pass
reread all of them to find one written since, so the rules in
`JUDGED_SURVEY_RULES` (`[ADD]`, `[SAME]`, `[SAME+NEW]`, and `[TWO]`)
share a baseline of their own,
`tools/data/sentence_shapes_survey_baseline.txt` (`SURVEY_BASELINE`).
`--survey` prints the hits of those rules not in it and ends on `K
survey, J judged`; `--survey --all` prints the judged ones too, marked
`judged`; and `--survey-accept` adds the unjudged hits after a human
read and drops stale entries, for the given files alone like
`--accept`. An entry is keyed by its sentence (an `[ADD]` entry by its
sentence and the one before it), so for the other rules an edit to the
passage above a kept sentence leaves the entry in place: reread a kept
sentence when the text above it changes.

`[PRT]` (2026-11-04, from a sentence the author marked in chapter 45)
is a phrasal verb split around a noun-phrase object: "the driver
carries the request out". The reader takes "carries the request" as a
finished verb phrase, transport, and revises it when "out" arrives
and turns the verb into "performs"; the particle holds the verb's
meaning and lands last. The author's style puts the particle beside
its verb whenever the object is a noun phrase, "carries out the
request", "looks up the name", "turns off the sensor", "shuts down the
generator". The rule (`split_particle()`) fires on a token with dep
`prt` whose head verb precedes it, with a `dobj` of that verb between
the two. Quiet by design: an object that is one of `LIGHT_OBJECTS`, a
pronoun or the CODE placeholder, which English puts before the
particle ("carries it out", "looks `name` up"); an object holding a
number, which makes the particle a measure ("stops one level up",
"three levels down"); a `QUIET_PARTICLES` particle, "through" or
"over", whose verb has no joined form in the book's senses ("lets zero
through", "starts the work over"); and a particle followed by one of
`PATH_PREPOSITIONS`, which makes it the start of a path ("leaves the
amount up to you", "sends a request up to the event loop"). It is a
default rule because the repair is one word's move and the keeps are
few: a joined form with another meaning ("pass the error up", since
"pass up" declines; "pass the tuple on"), a directional pair ("passes
the CODE up and the CODE down"), and a parser misread ("up front",
"Putting the Pieces Together"). The book-wide read that day had 78
candidates. A heading with the shape ("Telling the Wrappers Apart")
takes one verb instead ("Distinguishing the Wrappers"), but headings
are outside the paragraph reader, so the rule never sees one.

Five rules run by default, `RULES`: `[IMP]`, `[COLON+AND]`, `[PAIR]`,
`[AND+REL]`, and `[PRT]`, judged against a baseline. Eight are survey rules, `SURVEY_RULES`: `[AND]`,
plain `[COLON]`, `[ADD]`, `[TWO]`, `[CAN]`, `[SAME]`, `[SAME+NEW]`, and `[CAUS]`. The calibration shows why. `[AND]` fired on 7 before
only, 1 both, and 6 after only of the 72 rewritten pairs, so the
author's own rewrites carry the shape: it is a judgment made per
sentence in an editing pass, not a fault, and the whole book yields
hundreds of hits. `[COLON]` is the same, since most colons restate in
other words. `[IMP]` fired on 2 before only, 0 both, and 1 after only,
and the after-only one was an exercise sentence the parser misread.
Survey rules print only under `--survey`, each line marked `survey`
instead of NEW or accepted, after the default rules' lines. They never
enter the default rules' baseline and never count toward `N new`.
The rules in `JUDGED_SURVEY_RULES` share a judged list of their own,
described in the `[SAME+NEW]` section above. The intended use is
`tip sentence-shapes CH=31 ARGS=--survey` at the start of a chapter
pass.

The shared reading rules: a paragraph whose text starts with `Hint:` or
`Done when:` (the Solutions labels) is skipped; the paragraph reader is
the one `tools/stranded_prepositions.py` uses, so listings, headings,
block quotes, tables, and `#:` lines are skipped and inline code spans
arrive as the placeholder `CODE`. When the parser cannot start, the
check says so and exits 0.

Report-only: it prints the hits and exits 0, because the parser is a
statistical model and no gate runs it. `--fail` exits 1 when a NEW hit
is found. It runs inside `tip prose` and alone as `tip sentence-shapes`.
The baseline file, the report, the command line, and the edit-pairs half
of `--calibrate` are `tools/parse_check.py`'s, shared with the other
parse-based checks.

A hit prints as `path:line: [RULE] sentence`, the line holding the
sentence's first character. A `[SAME+NEW]` hit puts the noun and a
colon before the sentence, a `[CAUS]` hit the verb, object, and
complement, and an `[ADD]` hit the previous sentence after ` | after: `.
Every hit is read once by a human, and the
ones judged keeps live in `tools/data/sentence_shapes_baseline.txt`, so
a run prints only what is new. An entry is `path<TAB>[RULE] sentence`
with whitespace normalized and no line number, so a reflow or an edit
elsewhere in the file leaves the entry alone, while an edit to the
sentence retires it and the rewritten sentence reports as NEW. An
entry is a judged keep, not an exemption. The default run prints each
NEW hit and a summary (`N new, M accepted`), and lists a `stale` entry
that matches no hit any more. `--all` prints every hit, marked NEW or
accepted. `--accept` appends every NEW hit to the baseline and drops
the stale entries. A run given paths compares against those files' entries alone, and `--accept`
with paths adds and drops entries for those files and keeps
every other file's entries.

`--calibrate` checks every rule against `tools/data/edit_pairs.json`
(the sentences the author rewrote, 72 records of `before`, `after`, and
`fault`): each before and after text is parsed as a one-paragraph
document, and each rule reports the pairs where it fires on the before
text only (the hoped-for result), on the after text only, and on both,
with the ids and texts. The built-in `CALIBRATION_EXAMPLES` (the style
rules' own examples and their repairs) print in the same run, marked
ok or MISS. Calibration writes no cache.

Known false negatives, from the 2026-10-18 calibration on the small
English model. Of the rule examples, "Remove CODE and the pattern
fails" parses as an imperative root. "Forget the new argument at a call
and CODE reports a CODE" does not: the parser makes "Forget" the
clausal subject (`csubj`) of "reports", so `clausal_imperative()`
reads that one misparse. "CODE returns a new function, and the old one
stays registered" is missed by `[AND]`, because the parser tags "stays"
as a plural noun. Sentence-initial imperatives that the parser tags as
nouns ("Print", "Run") are missed by `[IMP]`; there is no fallback
for them. Known false-positive shapes, all left in the report for a
human: an exercise instruction with a long second clause ("Write a
test in which the first listener fails and the second still records
its notification"), an additive "and" whose clauses name different
subjects but belong together, and a colon that restates in other words
or introduces a list whose items hold relative clauses.

    uv run python -m tools.sentence_shapes           # new hits
    uv run python -m tools.sentence_shapes --all     # every hit
    uv run python -m tools.sentence_shapes --accept  # judged keeps
    uv run python -m tools.sentence_shapes --survey  # + AND, COLON, ADD, TWO, CAN, SAME, SAME+NEW, CAUS
    uv run python -m tools.sentence_shapes --survey-accept  # judged ADD, SAME, SAME+NEW, TWO keeps
    uv run python -m tools.sentence_shapes --calibrate
    uv run python -m tools.sentence_shapes Chapters/31_*.md
    uv run tip sentence-shapes CH=31
    uv run tip sentence-shapes-accept
    uv run tip sentence-shapes CH=31 ARGS=--survey-accept
"""

import re
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Final
from tools import parse_check
from tools.config import DATA_DIR
from tools.markdown import Document
from tools.parse_check import (
    build_arg_parser,
    calibrate_edit_pairs,
    key,  # noqa: F401
    parse_args,
    run,
    run_calibrate,
    sentence_text,
    skipped,
)
from tools.parsed_prose import (
    FINITE_TAGS,
    Paragraph,
    Parser,
    Sentence,
    Token,
    children,
    conj_verbs,
    coordinator,
    finite,
    parse,
    parsed,
    subject_of,
    subtree,
)
from tools.report import Finding
from tools.stranded_prepositions import clean, display  # noqa: F401
from tools.word_stutter import same_stem, stem

BASELINE: Final = DATA_DIR / "sentence_shapes_baseline.txt"
HEADER: Final = (
    "# Sentence-shape hits a human read and judged keeps: a colon\n"
    "# that restates in other words, an \"and\" that is additive, an\n"
    "# imperative the parser misread. An entry is not an exemption\n"
    "# from the rule.\n"
    "# path<TAB>[RULE] sentence, with whitespace normalized and no\n"
    "# line number, so a reflow leaves an entry alone and an edit to\n"
    "# the sentence retires it. Rewritten by\n"
    "# `tip sentence-shapes-accept`; read the delta with\n"
    "# `tip sentence-shapes` before accepting.\n"
    "# See tools/sentence_shapes.py.\n"
)
SURVEY_BASELINE: Final = DATA_DIR / "sentence_shapes_survey_baseline.txt"
"""The judged survey keeps, apart from the default rules' baseline."""
SURVEY_HEADER: Final = (
    "# Survey hits a human read and judged keeps, for the survey rules\n"
    "# in JUDGED_SURVEY_RULES ([ADD], [SAME], [SAME+NEW], [TWO]): the\n"
    "# sentence has one reading, and a reader gets it on the first\n"
    "# pass. An entry is not an exemption from the rule.\n"
    "# path<TAB>[RULE] sentence, with whitespace normalized and no\n"
    "# line number, so a reflow leaves an entry alone and an edit to\n"
    "# the sentence retires it. [SAME+NEW] puts the noun and a colon\n"
    "# before the sentence. [ADD] puts \" | after: \" and the sentence\n"
    "# before it after its own sentence, because the reading depends\n"
    "# on both, so an edit to either one retires the entry. For the\n"
    "# other rules an edit to the passage above leaves the entry in\n"
    "# place, so reread a kept sentence when the text above it changes.\n"
    "# Rewritten by `tip sentence-shapes ARGS=--survey-accept`; read\n"
    "# the delta with `tip sentence-shapes ARGS=--survey` before\n"
    "# accepting.\n"
    "# See tools/sentence_shapes.py.\n"
)
"""The comment header of the survey baseline file."""
BARE_PRONOUNS: Final = frozenset(
    "it they he she this that which who these those".split())
SUBJECT_DEPS: Final = ("nsubj", "nsubjpass")
CLOSERS: Final = frozenset("\"'”’)]*_")
RULES: Final = {
    "IMP": "imperative plus consequence",
    "COLON+AND": "colon, then a clause with an and-joined clause",
    "PAIR": "a pair word whose and or or arrives from the next clause",
    "AND+REL": "an and-joined second subject after a relative clause",
    "PRT": "a phrasal verb's particle after a noun-phrase object",
}
"""The default rules: judged against the baseline."""
SURVEY_RULES: Final = {
    "AND": "an and joining clauses with different subjects",
    "COLON": "colon, then an independent clause",
    "ADD": "an additive adverb after a change of subject",
    "TWO": "two modified terms held across one comparison",
    "CAN": "a modal can where the sentence reports what happens",
    "SAME": "a same with nothing to compare against",
    "SAME+NEW": "a same on a noun the passage above has not used",
    "CAUS": "a causative verb that demotes the actor to its object",
}
"""Printed only under `--survey`; never in the default baseline."""
JUDGED_SURVEY_RULES: Final = frozenset(
    {"ADD", "SAME", "SAME+NEW", "TWO"})
"""The survey rules whose read hits are kept in `SURVEY_BASELINE`."""
ALL_RULES: Final = tuple(RULES) + tuple(SURVEY_RULES)
COUNT_WORDS: Final = frozenset(
    "both several twice two three four five six seven eight nine ten "
    "pair couple".split())
"""Words that make a colon lead-in a count ("three parts:")."""
POINTER_WORDS: Final = frozenset(
    "this these that those following so here".split())
"""Last words that make a colon lead-in a demonstrative ("this shape:")."""
WH_TAGS: Final = frozenset({"WP", "WDT", "WRB"})
PAIR_WORDS: Final = {
    "between": "and", "both": "and", "either": "or", "neither": "nor"}
"""A word that promises a pair, and the conjunction that completes it."""
PAIR_BREAKS: Final = frozenset(",;:.()?!")
"""Punctuation that closes a pair word's phrase before its conjunction."""
PAIR_NOUN_START: Final = frozenset(
    {"DET", "NOUN", "PROPN", "PRON", "ADJ", "NUM"})
"""Parts of speech that open a noun phrase after the stray conjunction."""
ADD_AFTER: Final = " | after: "
"""Joins an `[ADD]` hit's sentence to the sentence before it."""
ADDITIVE_WORDS: Final = frozenset({"also", "too", "likewise"})
"""Adverbs that add a member to a set the previous sentence set up."""
PERSON_SUBJECTS: Final = frozenset(
    "you we i one reader programmer author people someone".split())
"""A subject whose \"can\" is a choice or a permission, not a hedge."""
OPTION_WORDS: Final = frozenset(
    "if when whenever unless whether while until once either or any "
    "anything anyone sometimes".split())
"""Words that mark a condition or a choice, so the \"can\" is real."""
ABILITY_ADVERBS: Final = frozenset({"also", "still", "even", "always"})
"""Adverbs on the verb that make the \"can\" a capability claim."""
CARRIED_SUBJECTS: Final = BARE_PRONOUNS | frozenset({"we", "you", "i", "one"})
"""A subject that carries the previous sentence's subject on."""
COMPARATOR_PAIRS: Final = frozenset({
    ("rather", "than"), ("instead", "of"), ("compared", "with"),
    ("compared", "to"), ("differs", "from"), ("differ", "from"),
    ("same", "way")})
"""Two-word comparators, by (previous word, word)."""
HEAVY_CONTENT: Final = 4
"""Content words a side of a comparison needs before it is heavy."""
LIGHT_POS: Final = frozenset({"DET", "PUNCT", "PART", "CCONJ", "SPACE"})
"""Tokens that add no weight to a side."""
NESTING_POS: Final = frozenset({"VERB"})
"""A side with a verb of its own (a participle, a relative clause, a
clause) is a picture the reader builds rather than a name."""
CAUSATIVES: Final = frozenset({
    "require", "let", "allow", "make", "force", "enable", "cause", "permit", "need", "want"})
"""Verbs that put the actor in object position before its infinitive."""
CAUS_OBJECTS: Final = frozenset({"NOUN", "PROPN"})
"""Parts of speech for the object; a pronoun (\"lets us\") is quiet."""
COMPLEMENT_DEPS: Final = frozenset({"xcomp", "ccomp"})
SAME_DETERMINERS: Final = frozenset(
    "the this that its their his her your our".split())
"""Words before \"same\" that make it a pointer candidate."""
COMPARISON_WORDS: Final = frozenset(
    "as than that which whether both each every all across twice "
    "again regardless either two three four several everywhere "
    "throughout identical one and".split())
"""Words that mark a comparison or a count, so \"same\" is real."""
SAME_PHRASES: Final = (("no", "matter"), ("for", "any"))
"""Two-word sequences that make a \"same\" sentence quiet."""
SAME_AFTER: Final = frozenset({"way", "time", "place", "reason"})
"""Words after \"same\" that make an idiom."""
SAME_PREDICATE: Final = frozenset(
    "stays stay stayed remains remain is are was were look looks "
    "read reads".split())
"""Verbs before \"the same\" that make it a predicate; \"of the same\"
(\"a package of the same name\") relates two things and is quiet too."""
SAME_SUBJECTS: Final = frozenset("it they he she we you i".split())
"""A subject pronoun right after \"same X\" opens a relative clause
(\"the same cls it received\"), which is the second term."""
SAME_PUNCT: Final = frozenset(".,:;)")
"""Punctuation after \"same\" that makes it a predicate."""
SAME_NEW_WINDOW: Final = 30
"""Source lines above a \"same\" that count as its passage."""
SAME_NEW_QUIET: Final = frozenset(
    "way time place reason thing kind sort name type shape size "
    "length order".split())
"""Nouns after \"same\" that name no thing a passage could introduce:
the idioms (\"the same way\") and the property nouns of \"of the same
name\"."""
SAME_NEW_TERMS: Final = frozenset({"as", "that", "which"})
"""A word right after the noun that attaches the second term."""
RECIPROCAL_WORDS: Final = frozenset(
    "both each every all two three four several they these "
    "those and or".split())
"""Subject words that make the compared things the subject's own
members (\"Every responder writes the same comparison\")."""
SAME_NEW_SPREAD: Final = frozenset(
    "every each both either any all twice again forever always "
    "everywhere throughout".split())
"""Words in the noun's own clause that spread \"same\" over repeats
or members, which are then its second term (\"the same answer every
time\", \"the same call on each element\")."""
SAME_NEW_CASES: Final = frozenset({"whether", "regardless"})
"""Words that name the cases a \"same\" holds across."""
SAME_NEW_PLACES: Final = frozenset("in inside within at on with".split())
"""Prepositions that make \"the same X\" a shared place or property
(\"in the same file\", \"at the same depth\", \"a new list with the
same elements\"), whose second term is the other thing in the
sentence."""
SUBJECT_STARTS: Final = frozenset({"DET", "PRON", "PROPN"})
"""Parts of speech that open a new noun phrase right after a noun,
the subject of a relative clause with its pronoun dropped; the CODE
placeholder is a `PROPN`."""
JOINING_WORDS: Final = frozenset({"and", "or", "both"})
"""Words before \"same\" in its clause that join the things compared
(\"skipping and stopping give the same result\")."""
PASSAGE_WORD: Final = re.compile(r"[A-Za-z][a-z]+|[A-Z]+")
"""A word of prose, or one part of an identifier (`to_query`,
`PriorityQueue`)."""
LIGHT_OBJECTS: Final = frozenset(
    "it them this that one you me us each both all some something "
    "anything nothing everything code".split())
"""An object English puts before the particle: a pronoun ("carries it
out", "gives something up"), or the CODE placeholder a code span
becomes ("looks `name` up"), one word the reader does not hold the
verb open across."""
QUIET_PARTICLES: Final = frozenset({"through", "over"})
"""Particles whose verb has no joined form in the book's senses: "lets
zero through", "passes the string through", "starts the work over",
"leaves one student over"."""
PATH_PREPOSITIONS: Final = frozenset(
    "to of into onto from toward towards".split())
"""A preposition right after the particle makes it the start of a path
("leaves the amount up to you", "sends a request up to the event loop",
"follow the traceback down to the call"), where the object stays
before it."""

CALIBRATION_EXAMPLES: Final[tuple[tuple[str, str, bool], ...]] = (
    # (rule, text, should it fire)
    ("TWO", "`drive()`, imported unchanged, answers a request yielded two generators deep the same way it answers one from `interview()`'s own body.", True),
    ("TWO", "`drive()` is imported unchanged. The requests now come from `ask()`, one generator below `interview()`, and `yield from` passes each one up to the driver, so `drive()` sees the same `Question`s it saw in `interview_generator.py`.", False),
    ("TWO", "Use a `set` rather than a `list` for membership tests.", False),
    ("TWO", "A delegating generator passes requests up the same way a function call passes a return value down.", False),
    ("IMP", "Remove `frozen=True` and the pattern fails.", True),
    ("IMP", "If you remove `frozen=True`, the pattern fails.", False),
    ("IMP", "Forget the new argument at a call and `ty` reports "
            "a `missing-argument`.", True),
    ("IMP", "If you forget the new argument at a call, `ty` reports "
            "a `missing-argument`.", False),
    ("IMP", "Run `ty` and read the error it reports.", False),
    ("IMP", "Try the operation and handle the exception.", False),
    ("AND", "`wraps()` returns a new function, and the old one "
            "stays registered.", True),
    ("AND", "`wraps()` returns a new function. The old one stays "
            "registered.", False),
    ("COLON+AND",
     "Python supplies `self` only when the lookup finds the function "
     "on the class: a function stored there is a descriptor, and "
     "reading it through an instance binds that instance.", True),
    ("COLON+AND",
     "Python supplies `self` only when the lookup finds the function "
     "on the class. A function stored there is a descriptor, and "
     "reading it through an instance binds that instance.", False),
    ("PAIR", "The problem appears whenever the producer keeps state "
             "between values and the consumer has a loop of its own.",
     True),
    ("PAIR", "The problem appears whenever the producer keeps state "
             "from one value to the next while the consumer has a loop "
             "of its own.", False),
    ("AND+REL",
     "The third-party `more-itertools` package supplies one as "
     "`iterate(func, start)`, which produces `start`, `func(start)`, "
     "`func(func(start))`, and so on without end, and `toolz` has an "
     "`iterate()` of the same shape.", True),
    ("AND+REL",
     "The third-party `more-itertools` package supplies one as "
     "`iterate(func, start)`, which produces `start`, `func(start)`, "
     "`func(func(start))`, and so on without end. `toolz` has an "
     "`iterate()` of the same shape.", False),
    ("PAIR", "Both forms keep the result and the name.", False),
    ("ADD", "A closure keeps its captured variables between calls, but "
            "each call runs its body from the top. The generator keeps "
            "its place as well, so a loop in progress survives.", True),
    ("ADD", "A closure keeps its captured variables between calls, but "
            "each call runs its body from the top. The generator keeps "
            "its locals and its place in the body, so a loop in progress "
            "survives.", False),
    ("ADD", "It checks the declaration's type and ignores which code "
            "runs first. Pyright accepts the read too.", True),
    ("ADD", "Programmers have been bad at keeping objects inside that "
            "set. Constructing an object in an illegal state is too "
            "easy.", False),
    ("PAIR", "A `break` at the match leaves both loops in one step and "
             "skips `else` along with them.", False),
    ("CAN", "A test can catch the broken contract.", True),
    ("CAN", "A test catches the broken contract.", False),
    ("CAN", "If you remove the guard, a subclass can take the slots "
            "back.", False),
    ("CAN", "You can skim for topics new to you.", False),
    ("CAN", "A `set` can hold any hashable object.", False),
    ("CAN", "The type checker cannot see the string.", False),
    ("CAUS", "`close()` requires the generator to finish.", True),
    ("CAUS", "The decorator lets the caller skip the check.", True),
    ("CAUS", "`slots=True` makes `dataclass()` build a new class.", True),
    ("CAUS", "The generator must finish.", False),
    ("CAUS", "It makes the check safe.", False),
    ("CAUS", "The pool needs a lock.", False),
    ("CAUS", "The class is required to define it.", False),
    ("SAME", "At `[2]`, the same `yield` raises `GeneratorExit`.", True),
    ("SAME", "At `[2]`, its `yield` raises `GeneratorExit`.", False),
    ("SAME", "The same directory reaches pytest through `pythonpath` in `pyproject.toml`.", True),
    ("SAME", "Alternative constructors need `Self` for the same reason `bump()` does.", False),
    ("SAME", "`register()` returns the same `cls` it received, so the name `Espresso` refers to the original class.", False),
    ("SAME", "The code runs the same with or without them.", False),
    ("SAME+NEW", "A finished f-string is a single `str` in which the values have merged into the literal text. `safe()` uses the same separation to check each value.", True),
    ("SAME+NEW", "`safe()` checks each value while it is still separate from the literal text.", False),
    ("SAME+NEW", "The `# type: ignore` in `report` silences `ty`'s diagnostic for the same hazard.", True),
    ("SAME+NEW", "The `hash()` failure is a second symptom of the same shallowness.", True),
    ("SAME+NEW", "`async`/`await` is the same machinery with a syntax that marks a function as one the event loop resumes.", True),
    ("SAME+NEW", "A `Template` keeps each value separate from the literal text. `safe()` uses the same separation.", False),
    ("SAME+NEW", "An `if`/`isinstance()` chain gives the same exhaustiveness check as a `match`.", False),
    ("SAME+NEW", "Every responder that filters by size writes the same comparison.", False),
    ("SAME+NEW", "A pure call returns the same answer every time.", False),
    ("SAME+NEW", "`expect()`, in the same file, prints through `report()` too.", False),
    ("PRT", "A generator yields a request and waits while the driver carries the request out.", True),
    ("PRT", "A generator yields a request and waits while the driver carries out the request.", False),
    ("PRT", "The driver carries it out.", False),
    ("PRT", "`pickle` looks the class up as `shapes.Circle` and does not find it.", True),
    ("PRT", "Gradual typing leaves the amount up to you.", False),
    ("PRT", "The `Result` that `ask()` returns stops one level up.", False),
    ("PRT", "`check()` rejects negatives but lets zero through.", False),
)
"""The style rules' own examples: (rule, text, should it fire)."""


def root_of(sentence: Sentence) -> Token | None:
    """The token that is its own head, None for an empty sentence."""
    for tok in sentence.tokens:
        if tok.head == tok.i:
            return tok
    return None


def phrase(tok: Token, sentence: Sentence) -> str:
    """The lowercase text of a token and everything below it."""
    keep = subtree(tok, sentence)
    return " ".join(t.text for t in sentence.tokens if t.i in keep).lower()


def absorbed_subject(head: Token, sentence: Sentence) -> bool:
    """Is the subject of `head` hanging off an earlier noun as a conj?

    "Forget X at a call and CODE reports Y": the parser coordinates
    "call" and "CODE", so "reports" has no subject and the "and" is a
    child of "call".
    """
    return own_subject(head, sentence) is None and any(
        t.dep == "conj" and t.pos in ("NOUN", "PROPN", "PRON")
        and t.i < head.i and sentence.tokens[t.head].pos in (
            "NOUN", "PROPN", "PRON")
        for t in sentence.tokens)


def clausal_imperative(sentence: Sentence) -> bool:
    """The parser's misreading of "Forget X and CODE reports Y".

    The sentence-initial bare verb becomes the clausal subject (`csubj`)
    of the verb after the "and", which is then the root. The shape is a
    hit when that head is finite, the bare verb has no coordinated verb
    of its own (else the "and" joins two imperatives), and an "and"
    lies between them that joins the imperative to the root: it hangs
    off the bare verb or the root, or off a noun whose coordinated
    partner is the root's absorbed subject. An "and" inside a relative
    clause ("in which the first responder fails and the second ...")
    hangs off a verb and is no hit.
    """
    tokens = sentence.tokens
    first = tokens[0] if tokens else None
    if first is None or first.tag != "VB" or first.dep != "csubj":
        return False
    head = tokens[first.head]
    if not finite(head, sentence) or any(
            c.dep == "conj" for c in children(first, sentence)):
        return False
    ands = [t for t in tokens if t.dep == "cc" and t.text.lower() == "and"
            and first.i < t.i < head.i]
    return any(t.head in (first.i, head.i) for t in ands) or (
        bool(ands) and absorbed_subject(head, sentence))


def own_subject(verb: Token, sentence: Sentence) -> Token | None:
    """The verb's `nsubj` or `nsubjpass` child, None otherwise."""
    for child in children(verb, sentence):
        if child.dep in SUBJECT_DEPS:
            return child
    return None


def consequence_clause(verb: Token, sentence: Sentence) -> bool:
    """A plain clause with its own subject, not a wh- or that-clause."""
    if own_subject(verb, sentence) is None:
        return False
    return not any(c.tag in WH_TAGS or c.dep == "mark"
                   for c in children(verb, sentence))


def imperative_consequence(sentence: Sentence) -> bool:
    """A bare imperative root with an "and" verb that has a subject."""
    root = root_of(sentence)
    if root is None or root.pos not in ("VERB", "AUX") or root.tag != "VB":
        return clausal_imperative(sentence)
    if subject_of(root, sentence) is not None:
        return False
    if root.i > 0 and sentence.tokens[root.i - 1].text.lower() == "to":
        return False
    return any(
        consequence_clause(c, sentence)
        and coordinator(c, sentence) == "and"
        for c in conj_verbs(root, sentence)
    )


def and_joined_clause(sentence: Sentence) -> Token | None:
    """The finite "and" verb whose subject differs from the root's, or None.

    The root is a finite verb with a plain subject; the verb coordinated
    with it through "and" is finite, has a subject of its own that is
    not a bare pronoun, and that subject's text differs from the first.
    """
    root = root_of(sentence)
    if root is None or not finite(root, sentence):
        return None
    first = subject_of(root, sentence)
    if first is None or first.dep not in SUBJECT_DEPS:
        return None
    for conj in conj_verbs(root, sentence):
        second = subject_of(conj, sentence)
        if (second is None or not finite(conj, sentence)
                or coordinator(conj, sentence) != "and"):
            continue
        said = phrase(second, sentence)
        if said not in BARE_PRONOUNS and said != phrase(first, sentence):
            return conj
    return None


def and_joins_subjects(sentence: Sentence) -> bool:
    """A finite root and a finite "and" verb with different subjects."""
    return and_joined_clause(sentence) is not None


def and_rides_on_relative(sentence: Sentence) -> bool:
    """The `[AND]` shape where the first clause already carries a
    relative clause or a parenthetical.

    "CODE supplies one as CODE, which produces CODE, CODE, CODE, and
    so on without end, and CODE has an CODE of the same shape": the
    first clause holds a `relcl` (or an opening parenthesis) before the
    "and" that introduces the second subject, so the second claim
    rides on a sentence that was already full. The first claim takes a
    period. The test is the clause's weight, not its subject, so a
    short first clause with a relative clause still counts.
    """
    conj = and_joined_clause(sentence)
    if conj is None:
        return False
    second = subject_of(conj, sentence)
    assert second is not None
    toks = sentence.tokens
    end = min(second.i, conj.i)
    for t in toks[:end]:
        if t.punct and t.text == "(":
            return True
        if t.dep != "relcl":
            continue
        start = min(subtree(t, sentence))
        if (start > 0 and toks[start].tag in WH_TAGS
                and toks[start - 1].punct and toks[start - 1].text == ","):
            return True
    return False


def pair_noun(tok: Token, sentence: Sentence) -> Token | None:
    """The noun a pair word governs, or None.

    "between" governs its object. "both", "either", and "neither"
    govern the noun they determine ("both loops"); before a verb
    ("CODE both creates X and appends Y") the verb holds the pair's
    own conjunction, so there is nothing to check.
    """
    if tok.text.lower() == "between":
        return next((c for c in children(tok, sentence) if c.dep == "pobj"),
                    None)
    if tok.head == tok.i:
        return None
    head = sentence.tokens[tok.head]
    return head if head.pos in PAIR_NOUN_START else None


def is_finite(tok: Token) -> bool:
    """A clause verb: finite or modal by tag, not a noun's participle."""
    return tok.pos in ("VERB", "AUX") and (
        tok.tag in FINITE_TAGS or tok.tag == "MD"
    ) and tok.dep not in ("acl", "amod")


def clause_boundary(tok: Token) -> bool:
    """Punctuation, a conjunction, or a wh-word that starts a clause."""
    if tok.punct:
        return tok.text in PAIR_BREAKS
    return tok.pos in ("CCONJ", "SCONJ") or tok.tag in WH_TAGS


def noun_phrase_start(tok: Token) -> bool:
    """A token that opens or continues a noun phrase after "and"."""
    return (tok.pos in PAIR_NOUN_START or tok.tag == "POS") and (
        tok.tag not in WH_TAGS)


def pair_gap(sentence: Sentence) -> bool:
    """A pair word whose "and" arrives from the next clause.

    "keeps state between values and the consumer has a loop":
    "between" promises "between X and Y", and the clause
    coordination's "and" followed by a noun phrase reads as the pair's
    second half until the verb arrives. The parser misreads the
    sentence the same way, hanging "the consumer" on "values", and
    hangs a complete pair's second half elsewhere just as often, so
    the test reads the token line instead of the attachment: a finite
    verb earlier in the pair word's own clause (back to the nearest
    punctuation, conjunction, or wh-word), so the clause is complete
    up to the pair phrase; the conjunction after the pair noun with
    no verb, subordinator, or punctuation between; a noun phrase after
    the conjunction; and a finite verb right after that noun phrase,
    which makes it a subject. A verb between the noun and the
    conjunction settles the pair word first ("both forms keep the
    result and the name"), and a verb right after the conjunction
    resolves the misreading at once ("leaves both loops in one step
    and skips"), so neither is a hit. "A call between the check and
    the use can reset" has no verb before "between", so "the use"
    completes the pair; "so neither the class nor the instance holds"
    starts its clause at "so".
    """
    toks = sentence.tokens
    for tok in toks:
        want = PAIR_WORDS.get(tok.text.lower())
        if want is None:
            continue
        noun = pair_noun(tok, sentence)
        if noun is None or noun.i < tok.i:
            continue
        before = toks[:tok.i]
        clause_start = next(
            (i + 1 for i in range(len(before) - 1, -1, -1)
             if clause_boundary(before[i])), 0)
        if not any(is_finite(t) for t in before[clause_start:]):
            continue
        conj = None
        for later in toks[noun.i + 1:]:
            if later.punct and later.text in PAIR_BREAKS:
                break
            if later.pos in ("VERB", "AUX", "SCONJ"):
                break
            if later.text.lower() == want:
                conj = later
                break
        if conj is None:
            continue
        rest = toks[conj.i + 1:]
        if not rest or not noun_phrase_start(rest[0]):
            continue
        phrase_end = 0
        while phrase_end < len(rest) and noun_phrase_start(rest[phrase_end]):
            phrase_end += 1
        if phrase_end < len(rest) and is_finite(rest[phrase_end]):
            return True
    return False



def ends_on_colon(sentence: Sentence) -> bool:
    """Does the sentence's last word-like token equal ':'?"""
    tail = [t for t in sentence.tokens
            if t.pos != "SPACE" and t.text not in CLOSERS]
    return bool(tail) and tail[-1].text == ":"


def merge(first: Sentence, second: Sentence) -> Sentence:
    """Two sentences as one, the second's indexes moved past the first."""
    shift = len(first.tokens)
    moved = tuple(t._replace(i=t.i + shift, head=t.head + shift)
                  for t in second.tokens)
    return Sentence(first.tokens + moved, first.start, second.end)


def colon_units(paragraph: Paragraph) -> list[Sentence]:
    """The paragraph's sentences, each colon-ended one joined to the next."""
    units: list[Sentence] = []
    pending: Sentence | None = None
    for sentence in paragraph.sentences:
        if pending is not None:
            sentence = merge(pending, sentence)
            pending = None
        if ends_on_colon(sentence):
            pending = sentence
        else:
            units.append(sentence)
    if pending is not None:
        units.append(pending)
    return units


def counted_lead_in(sentence: Sentence, colon: Token) -> bool:
    """Does a count or demonstrative before this colon name what follows?"""
    words = [t for t in sentence.tokens[:colon.i] if not t.punct]
    if not words:
        return False
    return (any(t.pos == "NUM" or t.text.lower() in COUNT_WORDS
                for t in words)
            or words[-1].text.lower() in POINTER_WORDS)


def colon_clause(sentence: Sentence) -> str | None:
    """COLON, COLON+AND, or None for a clause after a colon."""
    found: str | None = None
    tokens = sentence.tokens
    for colon in tokens:
        if colon.text != ":" or counted_lead_in(sentence, colon):
            continue
        for subject in tokens:
            if subject.i <= colon.i or subject.dep not in (
                    "nsubj", "nsubjpass", "expl"):
                continue
            verb = tokens[subject.head]
            if verb.i <= colon.i or not finite(verb, sentence):
                continue
            found = found or "COLON"
            if any(subject_of(c, sentence) is not None
                   and coordinator(c, sentence) == "and"
                   for c in conj_verbs(verb, sentence)):
                return "COLON+AND"
    return found


def additive_word(sentence: Sentence) -> Token | None:
    """The sentence's additive adverb, or None.

    "also", "too", "likewise", or the "well" of "as well". Skipped:
    the "also" of "but also", the degree "too" (followed by a word,
    not punctuation), and "as well as", which is a conjunction.
    """
    toks = sentence.tokens
    for k, tok in enumerate(toks):
        low = tok.text.lower()
        before = toks[k - 1].text.lower() if k else ""
        after = toks[k + 1] if k + 1 < len(toks) else None
        if low in ADDITIVE_WORDS and tok.pos in ("ADV", "PART"):
            if low == "also" and before == "but":
                return None
            if low == "too" and after is not None and not after.punct:
                continue
            return tok
        if low == "well" and before == "as":
            if after is not None and after.text.lower() == "as":
                continue
            return tok
    return None


def governing_verb(tok: Token, sentence: Sentence) -> Token:
    """The verb an adverb modifies, through any adverb or aux chain."""
    cur = tok
    while cur.head != cur.i:
        head = sentence.tokens[cur.head]
        if head.pos in ("VERB", "AUX"):
            return head
        cur = head
    return cur


def additive_after_new_subject(sentence: Sentence,
                               previous: Sentence) -> bool:
    """Does an additive adverb follow a change of root subject?

    The adverb must sit in the root clause, both sentences must have
    a root subject, this sentence's subject must not be a pronoun
    that carries the previous subject on, and the two subjects'
    lemmas must differ.
    """
    adverb = additive_word(sentence)
    root = root_of(sentence)
    if adverb is None or root is None:
        return False
    if governing_verb(adverb, sentence).i != root.i:
        return False
    subject = subject_of(root, sentence)
    previous_root = root_of(previous)
    if subject is None or previous_root is None:
        return False
    previous_subject = subject_of(previous_root, previous)
    if previous_subject is None:
        return False
    if subject.text.lower() in CARRIED_SUBJECTS:
        return False
    return subject.lemma.lower() != previous_subject.lemma.lower()


def comparator(sentence: Sentence) -> Token | None:
    """The token that relates two terms, or None.

    "like" and "unlike" as prepositions, the second word of a
    `COMPARATOR_PAIRS` pair ("rather than", "the same way"), the
    second "as" of "as X as", and an "as" within eight words of a
    "same".
    """
    toks = sentence.tokens
    lows = [t.text.lower() for t in toks]
    for k, low in enumerate(lows):
        before = lows[k - 1] if k else ""
        if low in ("like", "unlike") and toks[k].pos in ("ADP", "SCONJ"):
            return toks[k]
        if (before, low) in COMPARATOR_PAIRS:
            return toks[k]
        if low == "as" and k >= 2 and lows[k - 2] == "as":
            return toks[k]
        if low == "as" and "same" in lows[max(0, k - 8):k]:
            return toks[k]
    return None


def heavy_side(tokens: list[Token]) -> bool:
    """Is this stretch of a sentence a picture of its own?

    `HEAVY_CONTENT` content words (not `LIGHT_POS`), and among them
    a verb (`NESTING_POS`): a participle, a relative clause, or a
    clause, which makes the reader build the stretch rather than
    read a name.
    """
    content = [t for t in tokens if t.pos not in LIGHT_POS]
    if len(content) < HEAVY_CONTENT:
        return False
    return any(t.pos in NESTING_POS for t in content)


def two_terms(sentence: Sentence) -> bool:
    """Does a comparison in the predicate hold a heavy term on each side?

    The first term runs from the root verb to the comparator, the
    second from the comparator to the end of the sentence.
    """
    comp = comparator(sentence)
    root = root_of(sentence)
    if comp is None or root is None or root.i >= comp.i:
        return False
    toks = sentence.tokens
    first = comp.i
    lows = [t.text.lower() for t in toks]
    if lows[first - 1] in ("rather", "instead", "compared", "differs",
                           "differ", "same", "as"):
        first -= 1
        if lows[first - 1] == "the" and lows[first] == "same":
            first -= 1
    before = list(toks[root.i + 1:first])
    after = list(toks[comp.i + 1:])
    return heavy_side(before) and heavy_side(after)


def can_event(sentence: Sentence) -> bool:
    """Is a modal "can" hedging an event the sentence reports?

    An `aux` with lemma "can" on a lexical verb in the root clause
    (or coordinated with the root), with no negation and none of
    `ABILITY_ADVERBS` on the verb, a subject that is not one of
    `PERSON_SUBJECTS`, and none of `OPTION_WORDS` in the sentence.
    """
    root = root_of(sentence)
    if root is None:
        return False
    lows = {t.text.lower() for t in sentence.tokens}
    if lows & OPTION_WORDS:
        return False
    for tok in sentence.tokens:
        if tok.lemma.lower() != "can" or tok.dep != "aux":
            continue
        verb = sentence.tokens[tok.head]
        if verb.pos != "VERB":
            continue
        main = verb.i == root.i or (
            verb.dep == "conj" and verb.head == root.i)
        if not main:
            continue
        kids = children(verb, sentence)
        if any(k.dep == "neg" for k in kids):
            continue
        if any(k.text.lower() in ABILITY_ADVERBS for k in kids):
            continue
        subject = subject_of(verb, sentence)
        if subject is None and verb.dep == "conj":
            subject = subject_of(root, sentence)
        if subject is None or subject.text.lower() in PERSON_SUBJECTS:
            continue
        return True
    return False


def causative(sentence: Sentence) -> tuple[Token, Token, Token] | None:
    """(verb, object, infinitive) for a causative that demotes its actor.

    A `CAUSATIVES` lemma on a non-passive `VERB` with a noun object
    (`CAUS_OBJECTS`) and a verb complement. The object is the verb's
    `dobj` before an `xcomp` or `ccomp` verb, or the `nsubj` of that
    complement. The parser also reads \"requires the generator to
    finish\" as a `prep` \"to\" with the verb as its `pobj`, so that
    counts as the complement.
    """
    toks = sentence.tokens
    for verb in toks:
        if verb.lemma.lower() not in CAUSATIVES or verb.pos != "VERB":
            continue
        kids = children(verb, sentence)
        if any(k.dep == "auxpass" for k in kids):
            continue
        for obj in kids:
            if (obj.dep != "dobj" or obj.pos not in CAUS_OBJECTS
                    or obj.i < verb.i):
                continue
            for k in kids:
                if (k.dep in COMPLEMENT_DEPS and k.pos == "VERB"
                        and k.i > obj.i):
                    return verb, obj, k
                if k.dep == "prep" and k.text.lower() == "to" and (
                        k.i > obj.i):
                    for inf in children(k, sentence):
                        if inf.dep == "pobj" and inf.tag == "VB":
                            return verb, obj, inf
        for comp in kids:
            if comp.dep not in COMPLEMENT_DEPS or comp.pos != "VERB":
                continue
            for obj in children(comp, sentence):
                if (obj.dep == "nsubj" and obj.pos in CAUS_OBJECTS
                        and verb.i < obj.i < comp.i):
                    return verb, obj, comp
    return None


def same_idiom(toks: list[Token], k: int) -> bool:
    """Is the \"same\" at index k an idiom or a predicate?"""
    after = toks[k + 1] if k + 1 < len(toks) else None
    if after is None or after.text in SAME_PUNCT:
        return True
    if after.text.lower() in SAME_AFTER:
        return True
    if any(t.text.lower() in SAME_SUBJECTS and t.dep.startswith("nsubj")
           for t in toks[k + 1:k + 4]):
        return True
    before = toks[k - 2].text.lower() if k >= 2 else ""
    if before in SAME_PREDICATE or before == "of":
        return True
    return toks[k - 1].text.lower() == "the" and (
        after.text.lower() == "with")


def same_pointer(sentence: Sentence) -> bool:
    """Does a \"same\" stand where a pointer would do?

    A token with lemma \"same\" after a `SAME_DETERMINERS` word, in a
    sentence with none of `COMPARISON_WORDS` or `SAME_PHRASES`, and
    not an idiom (`same_idiom()`).
    """
    toks = list(sentence.tokens)
    lows = [t.text.lower() for t in toks]
    if set(lows) & COMPARISON_WORDS:
        return False
    if any(pair in SAME_PHRASES for pair in zip(lows, lows[1:])):
        return False
    for k, tok in enumerate(toks):
        if tok.lemma.lower() != "same" or k == 0:
            continue
        if lows[k - 1] not in SAME_DETERMINERS:
            continue
        if same_idiom(toks, k):
            continue
        return True
    return False


def cognate(noun: str, word: str) -> bool:
    """Do two words share a stem, as \"separation\" and \"separate\" do?

    Equal light stems (`word_stutter.stem()`), or stems that share
    their first five letters and all but two letters of the shorter
    stem, so \"except\" answers \"exception\" and \"over\" does not
    answer \"overhead\". A noun of five letters or more inside a
    longer word also counts, for an identifier that holds it
    (\"dispatch\" in `singledispatch`).
    """
    a, b = stem(noun), stem(word)
    if same_stem(a, b) or (len(a) >= 5 and a in b):
        return True
    shared = 0
    for x, y in zip(a, b):
        if x != y:
            break
        shared += 1
    return shared >= 5 and shared >= min(len(a), len(b)) - 2


def passage_words(text: str) -> set[str]:
    """The lowercase words of the prose and code in `text`."""
    return {w.lower() for w in PASSAGE_WORD.findall(text)}


def clause_verb(tok: Token, sentence: Sentence) -> Token:
    """The nearest verb at or above `tok`, or the root."""
    toks = sentence.tokens
    while tok.head != tok.i and tok.pos not in ("VERB", "AUX"):
        tok = toks[tok.head]
    return tok


def clause_mate(tok: Token, verb: Token, sentence: Sentence) -> bool:
    """Does `tok` hang under `verb` with no other verb between?"""
    toks = sentence.tokens
    while tok.head != tok.i:
        tok = toks[tok.head]
        if tok.i == verb.i:
            return True
        if tok.pos in ("VERB", "AUX"):
            return False
    return tok.i == verb.i


def reciprocal_subject(verb: Token, sentence: Sentence) -> bool:
    """Does the clause under `verb` speak of several things at once?

    Its subject is plural, coordinated, or counted
    (`RECIPROCAL_WORDS`), so a \"same\" in that clause compares the
    subject's own members with each other.
    """
    toks = sentence.tokens
    subject = subject_of(verb, sentence)
    while subject is None and verb.dep == "conj" and verb.head != verb.i:
        verb = toks[verb.head]  # "succeed and fail on the same inputs"
        subject = subject_of(verb, sentence)
    if subject is None:
        return False
    if subject.tag in ("NNS", "NNPS"):
        return True
    words = {toks[i].text.lower() for i in subtree(subject, sentence)}
    return bool(words & RECIPROCAL_WORDS)


def second_term_attached(noun: Token, sentence: Sentence) -> bool:
    """Does the sentence give the noun's second term right after it?

    \"The same X as Y\", \"the same X that ...\", and a relative
    clause with its pronoun dropped, which starts a new noun phrase
    right after the noun: a determiner, a pronoun, or a name (\"the
    same `cls` it received\", \"the same guarantee the `Result` type
    gives\", \"the same layout `array` uses\"). The test is the next
    word's part of speech, since the parser often reads the clause's
    verb as a noun (\"gives\", \"searches\") and marks no subject. A
    preposition after the noun is not one, so \"the same machinery
    with a syntax that marks ...\" stays a hit.
    """
    toks = sentence.tokens
    after = toks[noun.i + 1] if noun.i + 1 < len(toks) else None
    if after is None:
        return False
    if after.text.lower() in SAME_NEW_TERMS or after.pos in SUBJECT_STARTS:
        return True
    return any(c.dep == "relcl" for c in children(noun, sentence))


def spread_over_cases(same: Token, verb: Token,
                      sentence: Sentence) -> bool:
    """Does the sentence spread this \"same\" over repeats or cases?

    A second \"same\" (\"the same arguments produce the same
    result\"), a `SAME_NEW_CASES` word or \"no matter\", a
    `SAME_NEW_SPREAD` word in the noun's own clause, or a
    `JOINING_WORDS` word in that clause before the \"same\".
    """
    toks = sentence.tokens
    lows = [t.text.lower() for t in toks]
    if sum(1 for t in toks if t.lemma.lower() == "same") > 1:
        return True
    if set(lows) & SAME_NEW_CASES or ("no", "matter") in zip(lows, lows[1:]):
        return True
    for t in toks:
        low = t.text.lower()
        if low in SAME_NEW_SPREAD and t.i != same.i:
            if clause_mate(t, verb, sentence):
                return True
        if low in JOINING_WORDS and t.i < same.i:
            if clause_mate(t, verb, sentence):
                return True
    return False


def imperative(sentence: Sentence) -> bool:
    """Is the sentence a command: a bare verb root with no subject?"""
    root = root_of(sentence)
    return (root is not None and root.tag == "VB"
            and subject_of(root, sentence) is None)


def same_new_noun(sentence: Sentence, paragraph: Paragraph,
                  source: Sequence[str] = ()) -> Token | None:
    """The noun after a \"same\" that the passage has not used, or None.

    A \"same\" after a `SAME_DETERMINERS` word modifies a noun, and no
    word in the `SAME_NEW_WINDOW` lines of `source` above the \"same\",
    nor earlier in its own paragraph, is a `cognate()` of that noun:
    \"uses the same separation\" where nothing above says \"separation\"
    or \"separate\". `source` is the document's lines, listings and
    headings included; without it the paragraph alone is the passage.
    Quiet: a command (an exercise or a step label), a noun that is a
    code span or has one before it (\"the same `Path` object\"), a
    `SAME_NEW_QUIET` noun, a counted noun (\"the same two files\"), a
    `SAME_NEW_PLACES` preposition before the determiner, a noun with
    its second term attached (`second_term_attached()`), a
    `reciprocal_subject()`, and a \"same\" the sentence spreads over
    repeats or cases (`spread_over_cases()`).
    """
    if imperative(sentence):
        return None
    toks = sentence.tokens
    for k, tok in enumerate(toks):
        if tok.lemma.lower() != "same" or k == 0:
            continue
        if toks[k - 1].text.lower() not in SAME_DETERMINERS:
            continue
        if k >= 2 and toks[k - 2].text.lower() in SAME_NEW_PLACES:
            continue
        noun = toks[tok.head]
        if noun.i <= k or noun.pos != "NOUN":
            continue
        if noun.text.startswith("CODE"):
            continue
        if noun.lemma.lower() in SAME_NEW_QUIET:
            continue
        between = toks[k + 1:noun.i]
        if any(t.pos == "NUM" or t.text.startswith("CODE")
               for t in between):
            continue  # "the same two files", "the same `Path` object"
        if second_term_attached(noun, sentence):
            continue
        verb = clause_verb(noun, sentence)
        if reciprocal_subject(verb, sentence):
            continue
        if spread_over_cases(tok, verb, sentence):
            continue
        at = min(tok.idx, len(paragraph.lines) - 1)
        line = paragraph.lines[at]
        above = "\n".join(
            source[max(0, line - 1 - SAME_NEW_WINDOW):line - 1])
        before = paragraph.text[:tok.idx].replace("CODE", " ")
        words = passage_words(above) | passage_words(before)
        if any(cognate(noun.lemma, word) for word in words):
            continue
        return noun
    return None


def split_particle(sentence: Sentence) -> bool:
    """Does a phrasal verb's particle follow a noun-phrase object?

    A token with dep `prt` whose head is a verb before it, with a
    `dobj` of that verb between the two whose subtree is more than one
    of `LIGHT_OBJECTS`: "carries the request out", "looks the name
    up". The reader takes "carries the request" as a finished verb
    phrase and then revises it when "out" arrives; the repair puts the
    particle beside its verb, "carries out the request". A pronoun
    object stays between them because English puts it there. Quiet:
    a `QUIET_PARTICLES` particle, and a particle that opens a path
    (`PATH_PREPOSITIONS` right after it: "leaves the amount up to you").
    """
    toks = sentence.tokens
    for tok in toks:
        if tok.dep != "prt" or tok.lemma.lower() in QUIET_PARTICLES:
            continue
        after = toks[tok.i + 1] if tok.i + 1 < len(toks) else None
        if after is not None and after.text.lower() in PATH_PREPOSITIONS:
            continue
        verb = toks[tok.head]
        if verb.pos not in ("VERB", "AUX") or verb.i >= tok.i:
            continue
        for child in children(verb, sentence):
            if child.dep not in ("dobj", "obj"):
                continue
            if not verb.i < child.i < tok.i:
                continue
            words = [toks[i] for i in sorted(subtree(child, sentence))
                     if not toks[i].punct]
            if (len(words) == 1
                    and words[0].text.lower() in LIGHT_OBJECTS):
                continue
            if any(w.pos == "NUM" for w in words):
                continue  # a measure: "stops one level up"
            return True
    return False


def shapes(paragraph: Paragraph, source: Sequence[str] = (),
           ) -> Iterator[tuple[str, Sentence]]:
    """(rule, sentence) for each hit in one paragraph.

    `source` is the document's lines, which `[SAME+NEW]` reads above
    the sentence; without it that rule sees the paragraph alone.
    """
    if skipped(paragraph):
        return
    previous: Sentence | None = None
    for sentence in paragraph.sentences:
        if split_particle(sentence):
            yield "PRT", sentence
        if previous is not None and additive_after_new_subject(
                sentence, previous):
            yield "ADD", sentence
        previous = sentence
        if imperative_consequence(sentence):
            yield "IMP", sentence
        if and_rides_on_relative(sentence):
            yield "AND+REL", sentence
        elif and_joins_subjects(sentence):
            yield "AND", sentence
        if pair_gap(sentence):
            yield "PAIR", sentence
        if two_terms(sentence):
            yield "TWO", sentence
        if can_event(sentence):
            yield "CAN", sentence
        if same_pointer(sentence):
            yield "SAME", sentence
        if same_new_noun(sentence, paragraph, source) is not None:
            yield "SAME+NEW", sentence
        if causative(sentence) is not None:
            yield "CAUS", sentence
    for sentence in colon_units(paragraph):
        label = colon_clause(sentence)
        if label:
            yield label, sentence


def find(docs: list[Document], parser: Parser = parse) -> Iterator[Finding]:
    """A finding per rule per sentence, the message led by `[RULE]`."""
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        for paragraph in paras:
            lines = paragraph.lines
            for rule, sentence in shapes(paragraph, doc.lines):
                line = lines[min(sentence.start, len(lines) - 1)]
                detail = ""
                found = causative(sentence) if rule == "CAUS" else None
                if found is not None:
                    detail = " ".join(t.text for t in found) + ": "
                noun = (same_new_noun(sentence, paragraph, doc.lines)
                        if rule == "SAME+NEW" else None)
                if noun is not None:
                    detail = noun.text + ": "
                tail = ""
                if rule == "ADD":
                    index = next(i for i, s in enumerate(paragraph.sentences)
                                 if s is sentence)
                    tail = ADD_AFTER + sentence_text(
                        paragraph, paragraph.sentences[index - 1])
                yield Finding(doc.path, line, f"[{rule}] " + detail
                              + sentence_text(paragraph, sentence) + tail)


def rule_of(message: str) -> str:
    """The label in a message's leading `[RULE]`."""
    return message[1:message.index("]")]


def load_baseline(path: Path | None = None) -> set[str]:
    """The accepted keys, without comments or blank lines."""
    return parse_check.load_baseline(path or BASELINE)


def write_baseline(entries: set[str], path: Path | None = None) -> None:
    """The header plus the sorted entries, with LF line endings."""
    parse_check.write_baseline(entries, path or BASELINE, HEADER)


def labels_of(paras: list[Paragraph], skip: int = 0) -> set[str]:
    """The rule labels any paragraph of a text earns."""
    return {rule for p in paras for rule, _ in shapes(p)}


def calibrate(parser: Parser = parse) -> None:
    """Run the rules over the recorded edit pairs and the examples."""
    docs = [Document.from_text(clean(text),
                               Path(f"calibrate/example{number}.md"))
            for number, (_, text, _) in enumerate(CALIBRATION_EXAMPLES)]
    sides = calibrate_edit_pairs(
        parser, dict.fromkeys(ALL_RULES, ""), labels_of,
        previous=False, meanings=False, extra_docs=docs)
    print("== built-in examples ==")
    for number, (rule, text, should) in enumerate(CALIBRATION_EXAMPLES):
        fired = rule in sides[f"example{number}.md"]
        verdict = "ok  " if fired == should else "MISS"
        want = "fires" if should else "quiet"
        print(f"{verdict} [{rule}] {want}: {text}")


def main(argv: list[str] | None = None, parser: Parser = parse) -> int:
    ap = build_arg_parser(
        __doc__, fail_help="exit 1 when any NEW sentence is found",
        survey_help="also print the survey rules, never counted as "
                    "new; a judged [ADD], [SAME], [SAME+NEW], or [TWO] "
                    "hit prints only with --all",
        survey_accept_help="add the unjudged [ADD], [SAME], [SAME+NEW], "
                           "and [TWO] hits to their own baseline and "
                           "drop stale entries",
        calibrate_help="run the rules over tools/data/edit_pairs.json "
                       "and the built-in examples")
    args = parse_args(ap, argv)
    if args.calibrate:
        return run_calibrate("sentence_shapes", calibrate, parser)
    return run("sentence_shapes", args, lambda docs: find(docs, parser),
               baseline=BASELINE, header=HEADER,
               is_survey=lambda message: rule_of(message) in SURVEY_RULES,
               survey_baseline=SURVEY_BASELINE, survey_header=SURVEY_HEADER,
               is_judged=lambda message: (
                   rule_of(message) in JUDGED_SURVEY_RULES))


if __name__ == "__main__":
    raise SystemExit(main())
