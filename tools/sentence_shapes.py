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
cannot tell which from the parse.
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

Four rules run by default, `RULES`: `[IMP]`, `[COLON+AND]`, `[PAIR]`,
and `[AND+REL]`, judged against a baseline. Four are survey rules, `SURVEY_RULES`: `[AND]`,
plain `[COLON]`, `[ADD]`, and `[TWO]`. The calibration shows why. `[AND]` fired on 7 before
only, 1 both, and 6 after only of the 72 rewritten pairs, so the
author's own rewrites carry the shape: it is a judgment made per
sentence in an editing pass, not a fault, and the whole book yields
hundreds of hits. `[COLON]` is the same, since most colons restate in
other words. `[IMP]` fired on 2 before only, 0 both, and 1 after only,
and the after-only one was an exercise sentence the parser misread.
Survey rules print only under `--survey`, each line marked `survey`
instead of NEW or accepted, after the default rules' lines. They never
enter the baseline and never count toward `N new`. The intended use is
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
sentence's first character. Every hit is read once by a human, and the
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

`--calibrate` checks all seven rules against `tools/data/edit_pairs.json`
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
    uv run python -m tools.sentence_shapes --survey  # + AND, COLON, ADD
    uv run python -m tools.sentence_shapes --calibrate
    uv run python -m tools.sentence_shapes Chapters/31_*.md
    uv run tip sentence-shapes CH=31
    uv run tip sentence-shapes-accept
"""

from collections.abc import Iterator
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
BARE_PRONOUNS: Final = frozenset(
    "it they he she this that which who these those".split())
SUBJECT_DEPS: Final = ("nsubj", "nsubjpass")
CLOSERS: Final = frozenset("\"'”’)]*_")
RULES: Final = {
    "IMP": "imperative plus consequence",
    "COLON+AND": "colon, then a clause with an and-joined clause",
    "PAIR": "a pair word whose and or or arrives from the next clause",
    "AND+REL": "an and-joined second subject after a relative clause",
}
"""The default rules: judged against the baseline."""
SURVEY_RULES: Final = {
    "AND": "an and joining clauses with different subjects",
    "COLON": "colon, then an independent clause",
    "ADD": "an additive adverb after a change of subject",
    "TWO": "two modified terms held across one comparison",
}
"""Printed only under `--survey`; never baselined."""
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
ADDITIVE_WORDS: Final = frozenset({"also", "too", "likewise"})
"""Adverbs that add a member to a set the previous sentence set up."""
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


def shapes(paragraph: Paragraph) -> Iterator[tuple[str, Sentence]]:
    """(rule, sentence) for each hit in one paragraph."""
    if skipped(paragraph):
        return
    previous: Sentence | None = None
    for sentence in paragraph.sentences:
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
    for sentence in colon_units(paragraph):
        label = colon_clause(sentence)
        if label:
            yield label, sentence


def find(docs: list[Document], parser: Parser = parse) -> Iterator[Finding]:
    """A finding per rule per sentence, the message led by `[RULE]`."""
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        for paragraph in paras:
            lines = paragraph.lines
            for rule, sentence in shapes(paragraph):
                line = lines[min(sentence.start, len(lines) - 1)]
                yield Finding(doc.path, line, f"[{rule}] "
                              + sentence_text(paragraph, sentence))


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
        survey_help="also print the survey rules (AND, COLON), "
                    "never baselined or counted",
        calibrate_help="run the rules over tools/data/edit_pairs.json "
                       "and the built-in examples")
    args = parse_args(ap, argv)
    if args.calibrate:
        return run_calibrate("sentence_shapes", calibrate, parser)
    return run("sentence_shapes", args, lambda docs: find(docs, parser),
               baseline=BASELINE, header=HEADER,
               is_survey=lambda message: rule_of(message) in SURVEY_RULES)


if __name__ == "__main__":
    raise SystemExit(main())
