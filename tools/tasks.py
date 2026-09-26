"""The book's tasks: what `tip` runs, and what its picker lists.

This file replaces the Makefile. Each task is a function taking the
command line's variables (`Vars`), registered by `@task` under the
section most recently opened by `section()`. The decorator's first
argument is the one-line doc the listing shows; the docstring is the
long-form help the picker shows on `?`, and the body is the recipe,
shown under it. Put a task's one-line doc in the decorator so the
listing and the recipe never drift apart, and anything longer in the
docstring.

`secondary=True` folds a task out of the listing (still documented,
still smoke-tested by `tip verify-targets`) because a sibling's doc
text names it (`fix-eol` under `eol`). `also(name, ...)` repeats tasks
defined in other sections into the section it sits in, at that point
in the listing, so the everyday section can show `check-ch` and
`spell` without moving their definitions. The sections run from the
everyday loop down to setup and cleanup: what you run most is at the
top of the menu, what you run rarely at the bottom.

A variable a task's doc mentions as `NAME=example` is prompted for by
the picker before the task runs; `defaults=` says what Enter means.
The steps are `py()` (a `tools.` module), `tool()` (a console script
from the project environment), and `run()` (any command); tools/tip.py
has the machinery.
"""
import shutil

from tools.config import ROOT
from tools.tip import Vars, also, invoke, py, run, section, task, tool

# The Markdown checks the gate enforces, run together by check_all.py in one
# process with one parse per file, rather than as separate scripts. Names
# come from `tip checks ARGS=--list`. This is check_all's whole registry:
# prose-lint joined once its last findings were cleared, and widths joined
# when the book moved to 60-character listings, so a new violation of
# either now fails the gate rather than sitting in a backlog. widths also
# runs over Solutions/ (a separate step in `gate`), since Solutions
# listings render on the same small screens. records runs there too:
# most of the book's frozen data classes are in Solutions/.
GATE_CHECKS = ("listings widths banned comment-periods comment-caps "
               "comment-spacing anchors footnotes self-reference prose-lint "
               "pattern-names records").split()

# Markdown outside Chapters/ that still carries intra-document links worth
# gating. Only `anchors` runs over it: `banned` would fire on the tooling
# README's own worked example of a banned phrase (and on the `from
# __future__ import annotations` lines still in a few Solutions listings),
# and the listing checks have no ```python blocks to inspect in the README.
# Two of these links were dead for a while precisely because nothing looked
# outside Chapters/, and three anchors in Solutions/ were dead for the same
# reason. check_solutions.py covers the other half of a Solutions link, the
# `../Chapters/` prefix that `anchors` cannot see is missing.
GATE_DOCS = ["tools/README.md", "Solutions"]

SOLUTIONS_TREE = str(ROOT / "build" / "solutions")


def prose_files(v: Vars) -> list[str]:
    """Files for spell/prose: all of DOCS (default Chapters and
    Solutions), or one chapter via CH= (a number or stem prefix), e.g.
    `tip prose CH=33` or `tip prose CH=33_Patterns--Visitor`. CH= covers
    the chapter and its Solutions file together, and a CH matching
    nothing is passed through as a pattern so the tool still errors
    loudly instead of silently linting everything."""
    ch = v.get("CH")
    if not ch:
        return v.words("DOCS") or ["Chapters", "Solutions"]
    found = [str(p.relative_to(ROOT).as_posix())
             for d in ("Chapters", "Solutions")
             for p in sorted((ROOT / d).glob(f"{ch}*.md"))]
    return found or [f"Chapters/{ch}*.md"]


def remove(path: str) -> None:
    """Delete a directory under the repo root, if it is there. On
    Windows a shell whose cwd sits inside it holds it open and the
    delete fails silently; run from the root."""
    print(f"remove {path}")
    shutil.rmtree(ROOT / path, ignore_errors=True)


section("Everyday")


@task("The verify loop for one chapter and its Solutions file (CH=28), "
      "a few seconds")
def verify_ch(v: Vars) -> None:
    """`tip verify` scoped to one chapter and its Solutions file, in a few
    seconds instead of tens: fix-eol, reflow, both extracts, this chapter's #:
    markers (chapter and Solutions), both syncs and drift checks, the Markdown
    gates on these two files, then ty/ruff/run/pytest over the chapter's
    directory in each build tree. GATE_CHECKS is passed through so the Markdown
    checks are the gate's by construction. It writes no gate stamp: a change
    that can reach other chapters (a renamed listing, a utils/ helper, a
    heading others link to) still needs `tip verify`.
    """
    py("tools.verify_chapter", *v.words("CH"), "--checks", *GATE_CHECKS)


also("check-ch", "run-one")


@task("The everyday loop: every fixer, refresh #: markers, sync "
      "Examples/ and SolutionsCode/, figures, then every gate but the "
      "site build (ARGS=--help lists the steps)")
def verify(v: Vars) -> None:
    """The edit-and-check loop to repeat after touching a chapter: every
    mutating fixer (the comment-style fixers, import sorting, blank-line
    cleanup), a refresh of the #: output markers, a sync of the committed
    Examples/ and SolutionsCode/ trees, the figure gallery, then the full
    gate. Each fixer repairs something the gate would otherwise fail on,
    and the gate already self-heals line endings, reflow, and markers, so
    a fixer-free loop would only trade a fix for a failure. The marker
    refresh runs before the sync on purpose: the gate refreshes markers
    too, but only after its own sync step already copied the Markdown, so
    a stale marker would otherwise stay one sync behind until the next
    run caught it up. The ordered step list, and the doc text ARGS=--help
    prints for each one, both live in tools/verify.py (VERIFY_TARGETS);
    add a target there to include it, nothing else needs to change.
    """
    py("tools.verify", *v.words("ARGS"))


@task("Run every check over both trees, reporting all failures instead "
      "of the first")
def sweep(v: Vars) -> None:
    """`gate` stops at its first failure, and since `solutions-gate` is one of
    its deps, that half runs first and can hide every Chapters/
    failure behind it. So one `gate` rarely shows the whole blast radius of
    a tool upgrade. This runs every static check over both trees to
    completion and summarizes which failed. `tools-upgrade` ends with it;
    run it directly after any change wide enough that the first failure is
    unlikely to be the only one. The #: markers are excluded on purpose
    (see the script docstring).
    """
    py("tools.sweep_checks")


@task("The gate without sync or site (check, reflow, slugs, output, ty,"
      " ruff, run, pytest, solutions-gate)",
      deps=("solutions-gate",))
def gate(v: Vars) -> None:
    """The local gate without the site build: line endings, listing density,
    drift check, output markers, ty, ruff, run, pytest, plus the same checks
    for Solutions/ (solutions-gate). `verify` runs `sync` first; `ci` adds the
    site. validate_output.py runs with --update: a stale #: marker self-heals
    (rewriting Chapters/) the same way fix-eol/sync already do, rather than
    failing the build. A raised exception where none is expected still fails
    the gate; only marker text is self-corrected. The drift check also fails on
    an orphaned stray under Examples/ (a file no block generates and no chapter
    mentions); run `tip prune` to delete those. solutions-gate applies the same
    stray check to SolutionsCode/ against Solutions/*.md; `prune` covers that
    tree too. reflow_prose.py runs here with --write, so prose that drifts out
    of Semantic Line Breaks self-heals (rewriting Chapters/) the same way
    fix-eol and validate_output's marker --update do, instead of failing the
    build and forcing a `tip reflow` plus a second full run. The safety valve
    stays: a paragraph that fails reflow's round-trip check is never rewritten,
    and that failure still exits nonzero and stops the gate.
    """
    tool("pytest", *v.words("PYTEST_N"), "tools/tests")
    py("tools.check_line_endings")
    py("tools.check_all", *GATE_CHECKS)
    py("tools.check_all", "anchors", "--paths", *GATE_DOCS)
    py("tools.check_all", "widths", "records", "--paths", "Solutions")
    py("tools.coupling_panels", "--check")
    py("tools.state_machine_figure", "--check")
    py("tools.check_quoted_diagnostics")
    py("tools.exercise_refs")
    py("tools.reflow_prose", "--write")
    py("tools.check_unique_slugs")
    py("tools.extract_examples")
    py("tools.check_skip_lists")
    py("tools.extract_examples", "--write")
    py("tools.validate_output", "--update", "Chapters")
    tool("ty", "check", "build/examples")
    tool("ruff", "check", "build/examples")
    py("tools.run_examples")
    tool("pytest", *v.words("PYTEST_N"), "build/examples")
    py("tools.gate_stamp", "--write", "gate")
    py("tools.tool_stamp", "--nag")


@task("The Solutions gate: numbering, check, output, ty, ruff, run, "
      "pytest",
      secondary=True)
def solutions_gate(v: Vars) -> None:
    """Mirrors `gate`, but for Solutions/: numbering, drift check, output
    markers, ty, ruff, run, pytest. This skipped the run step until 2026-08-31,
    on the reasoning that every extractable block carries a #: marker and so is
    already executed by the marker refresh. That was wrong: 24 answers carry no
    marker and are not tests, so nothing ran them, and the first run over the
    tree found one that could not execute at all. It costs about six seconds.
    The numbering check runs first because it is the cheapest and reports a
    missing answer, which no later step here would notice. extract_solutions.py
    also fails on an orphaned stray under SolutionsCode/; `tip prune` deletes
    exactly those. Folded out of the listing: `gate` names it, and `gate` is
    what you run.
    """
    py("tools.check_solutions")
    py("tools.extract_solutions")
    py("tools.extract_solutions", "--write")
    py("tools.validate_output", "--update", "--tree", SOLUTIONS_TREE,
       "Solutions")
    tool("ty", "check", "build/solutions")
    tool("ruff", "check", "build/solutions")
    py("tools.run_examples", "--tree", SOLUTIONS_TREE)
    tool("pytest", *v.words("PYTEST_N"), "build/solutions")


@task("Report when the gate last passed and what changed since")
def gate_status(v: Vars) -> None:
    """When did the book last pass the gate, and has anything changed since?
    The stamp records a hash per Chapters/ and Solutions/ file, so this answers
    the second half too. `gate` writes it; `verify`, `ci`, and `all` inherit
    it, since each runs `gate`.
    """
    py("tools.gate_stamp")


also("local", "spell", "prose")


section("Writing and spelling")


@task("codespell + prose_lint + full-dictionary spellcheck (CH=29 for one)")
def spell(v: Vars) -> None:
    """Spell-check the book and lint it for small mechanical slips. codespell
    catches known misspellings (prose and code comments); prose_lint catches
    spacing/blank-line/punctuation slips; spellcheck.py is a full-dictionary
    check of the prose, with accepted terms in tools/data/wordlist.txt. Run one
    chapter with CH= (e.g. `tip spell CH=29`) or a path with DOCS=.
    """
    tool("codespell", *prose_files(v))
    py("tools.prose_lint", *prose_files(v))
    py("tools.spellcheck", *prose_files(v))


@task("Accept every unknown word: spellcheck's into wordlist.txt, "
      "codespell's into codespell-ignore.txt (review the diff!)")
def spell_add(v: Vars) -> None:
    """Accept every word spellcheck.py doesn't recognize into
    tools/data/wordlist.txt and every word codespell flags into
    tools/data/codespell-ignore.txt (both sorted, deduplicated) instead of
    failing. The two checkers keep separate lists, and codespell reads code
    where spellcheck.py reads prose only, so a class name codespell dislikes
    needs the second list. It cannot tell a real term from a typo, so always
    review the diff before committing; a real typo belongs in the prose, not in
    either list.
    """
    py("tools.spellcheck", *prose_files(v), "--add")


@task("House-style lint with Vale (CH=29 for one chapter; needs vale binary)")
def prose(v: Vars) -> None:
    """House-style lint with Vale: no em-dashes and no filler phrases. Run one
    chapter with CH= (e.g. `tip prose CH=29`) or a path with DOCS=.
    Vale is a standalone binary (not uv-managed; `tip tools-check-full`
    says how to install it). Its style packages (.vale.ini's Packages)
    download into the gitignored styles/ on the first run here, since
    without them every run dies with "style 'write-good' does not exist".
    """
    if not (ROOT / "styles" / "write-good").exists():
        run(["vale", "sync"])
    run(["vale", *prose_files(v)])


also("checks", "pattern-names")


@task("Rewrite prose to one sentence per line (CH=02 for one chapter)")
def reflow(v: Vars) -> None:
    """Rewrite prose paragraphs to one sentence per line (code, tables, lists,
    and headings are left untouched; a file is rewritten only if it
    round-trips). Target one chapter with CH=, e.g. `tip reflow CH=02` or `tip
    reflow CH=Tour`.
    """
    py("tools.reflow_prose", "--write", *v.words("CH"))


@task("Report which chapters would reflow, no write (CH=02 for one)")
def reflow_check(v: Vars) -> None:
    py("tools.reflow_prose", *v.words("CH"))


@task("AI editing passes over chapters' prose (CH=\"25 28\"; MODEL=; "
      "ARGS=--list)")
def rewrite(v: Vars) -> None:
    """AI editing passes over one chapter's prose, edited in place. Each pass
    is one headless `claude -p "/<skill> <chapter>"` run. Reflow and the
    prose gates run after every pass, and the chain stops at the first
    failure. It costs tokens and is nondeterministic, so it is never part
    of verify/gate/ci, refuses to run under CI, and needs a `git diff`
    review before you commit.

    The passes, in the order they run (PASSES in tools/rewrite.py):

      elements-of-style  default  Strunk: active voice, positive form,
                                  omit needless words
      activate           opt-in   clear the passive, there-is, and
                                  weak-verb warnings from `tip prose`
      literal            default  say what the machinery does: a literal
                                  verb for each figure of speech
      positive           default  say what happens, not what does not:
                                  keep only the negations that claim
      straighten         default  one sentence, one load: name the actor,
                                  split at the seam
      cohesion           default  old before new: one topic string per
                                  paragraph, the news at the end
      antecedents        default  name what each this/it/which points at
                                  when two things could be meant
      readability        opt-in   remove AI-writing tells; its own rule
                                  is "only when asked", so it never runs
                                  unless you name it here
      bruce-edit-apply   default  apply the promoted rules in
                                  bruce_edit_db.md

    A bare `tip rewrite CH=25` runs the seven defaults. To add an opt-in
    pass to them: ARGS="--also activate". To run only the passes you
    name: ARGS="--passes activate readability". To run all nine:
    ARGS=--all. ARGS=--list prints this table; ARGS=--dry-run prints the
    commands without running them.

    Several chapters run in parallel: CH="25 28 30" or CH=30-40 (a range,
    inclusive; CH="25 30-32" mixes them) runs one pass chain per chapter,
    four at a time (ARGS=-j2 changes that). Each chain edits
    only its own chapter and checks only its own chapter, so they never
    trip each other, and their output arrives per step under a [NN]
    prefix. ARGS=--serial runs them one after another with output
    streamed live, the mode for watching a pass work.

    Each pass names its own model (PASSES in tools/rewrite.py; ARGS=--list
    shows them). MODEL= forces one model on every pass for a run:
    MODEL=claude-sonnet-5 is the cheap lap. Each pass header prints the
    model it used.
    """
    model = ["--model", v.get("MODEL")] if v.get("MODEL") else []
    py("tools.rewrite", *v.words("CH"), *model, *v.words("ARGS"))


section("Code examples (build/examples/, build/solutions/)")


@task("Run the code checks for one chapter only (CH=12), ~1s")
def check_ch(v: Vars) -> None:
    """The edit loop for one chapter's listings. `gate` checks all 44 chapters
    and spends most of its time executing listings you did not touch; this runs
    the same code-example checks (markers, listing style, ty, ruff, pytest)
    against one chapter, in about a second. It is not a substitute for `gate`,
    which also catches cross-chapter breakage: run that before committing.
    """
    py("tools.check_chapter", *v.words("CH"))


@task("Run one example and show its output "
      "(`tip run-one deque_timing`, or F=)", positional="F")
def run_one(v: Vars) -> None:
    """Run one example the way the book assumes: from inside its own chapter
    directory, with the tree's utils/ on PYTHONPATH, so its sibling imports and
    data files resolve and `from benchmark import report` finds the shared
    helper. F takes a path or just the file's name (F=deque_timing). It reads
    Examples/, the committed tree, so it needs no extract step, and it prints
    the equivalent cd + PYTHONPATH commands before running: that is what you
    type when this target is not at hand. `tip run-one deque_timing` is the
    same as F=deque_timing (`positional="F"` binds the word to F).
    """
    py("tools.run_one_example", *v.words("F"))


@task("Run every extracted .py in both build trees and report failures",
      deps=("extract",), name="run")
def run_all(v: Vars) -> None:
    """These all read the build trees, so each depends on `extract` to rebuild
    them first. tip runs `extract` once per invocation, so depending on it
    from several targets does not re-extract, and `extract` wipes each tree
    before writing it, so a stale tree (a gitignored build/ left over from an
    older Markdown) never survives to be checked. Each target covers both
    trees. `output` alone executes only a block that carries a #: marker and
    `test` only a test_*.py, which together leave two dozen Solutions answers
    that nothing else runs (importable helpers, and standalone programs whose
    behavior the answer describes in prose), so `run` runs every one. The
    absolute --tree is required, not stylistic: it goes on PYTHONPATH, and a
    relative path stops resolving the moment an example changes directory.
    """
    py("tools.run_examples")
    py("tools.run_examples", "--tree", SOLUTIONS_TREE)


@task("Open every example that needs a human, all at once, and report "
      "how each one exits (ARGS=--list to only list them)")
def by_hand(v: Vars) -> None:
    """Start every example listed under `# [by-hand]` in tools/data/norun.txt,
    all at once, each from its own chapter directory with utils/ on PYTHONPATH.
    Today that is the five Tkinter views, which no gate executes. Try each
    window and close it; the tool prints a line as each one ends, then the
    traceback of any that exited nonzero, and exits 1 if one did. ARGS=--list
    prints what would start and opens nothing. Excluded from verify-targets'
    smoke test: it opens windows and waits for a human.
    """
    py("tools.by_hand", *v.words("ARGS"))


@task("Update the #: output markers in Chapters/ and Solutions/ "
      "listings",
      deps=("extract",))
def output(v: Vars) -> None:
    """Rewrite the #: output markers inside the Markdown's ```python listings,
    in Chapters/ and Solutions/, to the stdout each listing actually produces.
    Depends on extract so each listing runs from its build directory, where its
    sibling imports and data files live. validate_output.py needs an absolute
    --tree for Solutions: a block runs with cwd inside
    build/solutions/<chapter>, and a relative tree argument stops resolving
    once cwd changes (the same gotcha run_examples.py's --tree has; see
    tools/README.md).
    """
    py("tools.validate_output", "--update", "Chapters")
    py("tools.validate_output", "--update", "--tree", SOLUTIONS_TREE,
       "Solutions")


@task("Verify the #: output markers in Chapters/ and Solutions/ without"
      " rewriting",
      deps=("extract",))
def output_check(v: Vars) -> None:
    """Same, but report mismatches instead of rewriting (a gate-friendly
    check).
    """
    py("tools.validate_output", "Chapters")
    py("tools.validate_output", "--tree", SOLUTIONS_TREE, "Solutions")


@task("Run the pytest examples (test_*.py) in both build trees",
      deps=("extract",))
def test(v: Vars) -> None:
    """One pytest run per tree, so a failure report names the tree it is in.
    """
    tool("pytest", *v.words("PYTEST_N"), "build/examples")
    tool("pytest", *v.words("PYTEST_N"), "build/solutions")


@task("Type-check build/examples/ and build/solutions/ (must be clean)",
      deps=("extract",))
def ty(v: Vars) -> None:
    """One ty run over both trees, so a failure in build/examples never hides
    one in build/solutions (a failing step stops the steps after it).
    """
    tool("ty", "check", "build/examples", "build/solutions")


@task("PEP8-lint both build trees with ruff (must be clean)",
      deps=("extract",))
def lint(v: Vars) -> None:
    tool("ruff", "check", "build/examples", "build/solutions")


@task("Sort imports and drop unused ones in the listings (ruff I,F401),"
      " in the Markdown",
      deps=("extract",))
def fix_imports(v: Vars) -> None:
    """Organize imports in the book's python listings (ruff's I rule), writing
    the result back into the Markdown. Depends on extract so ruff sees each
    listing's siblings and classifies imports the way the lint gate does.
    """
    py("tools.fix_imports", "--fix")


@task("Update the committed Examples/ and SolutionsCode/ trees from the"
      " Markdown")
def sync(v: Vars) -> None:
    """Write the extracted trees straight into the committed copies, Examples/
    from Chapters/ and SolutionsCode/ from Solutions/, so the drift check
    passes. Run after editing a code block. Each Solutions block is
    self-contained (it redeclares whatever book context it needs) rather
    than importing from Examples/, so that tree never breaks when a book
    example changes.
    """
    py("tools.extract_examples", "--write", "-o", "Examples")
    py("tools.extract_solutions", "--write", "-o", "SolutionsCode")


@task("Verify the committed Examples/ and SolutionsCode/ trees match "
      "the Markdown")
def check(v: Vars) -> None:
    py("tools.extract_examples")
    py("tools.extract_solutions")


@task("Delete orphaned stray files under Examples/ and SolutionsCode/ "
      "(see `check`)")
def prune(v: Vars) -> None:
    """`check`/`gate` already fail on an orphaned stray (a file under Examples/
    with no matching block and no mention anywhere in the book, typically left
    behind by a rename). This deletes exactly those; a stray whose filename is
    still mentioned somewhere in the book is left alone for a human to review.
    It prunes SolutionsCode/ in the same run, since a renamed listing that both
    trees copy (a utils/ helper) otherwise fails solutions-gate after the
    Examples/ prune looked complete.
    """
    py("tools.extract_examples", "--prune")
    py("tools.extract_solutions", "--prune")


@task("Write build/examples/ and build/solutions/ from the Markdown")
def extract(v: Vars) -> None:
    """Both build trees, each wiped before it is written.
    """
    py("tools.extract_examples", "--write")
    py("tools.extract_solutions", "--write")


@task("Diff pyright over both trees against the baseline (advisory; "
      "accept with `tip pyright-accept`)",
      deps=("extract",))
def pyright_review(v: Vars) -> None:
    """Pyright is a second opinion, not a gate. The listings carry no pyright
    suppressions; every disagreement with `ty` is an entry in
    tools/data/pyright_baseline.txt, and the review prints only the delta:
    NEW (a fresh disagreement) and GONE (pyright caught up, or the listing
    changed). Read it after editing listings or after `tip tools-upgrade`
    moves pyright. `pyright` is the raw run.
    """
    py("tools.pyright_review")


@task("Rewrite tools/data/pyright_baseline.txt from the current pyright"
      " run",
      deps=("extract",), secondary=True)
def pyright_accept(v: Vars) -> None:
    py("tools.pyright_review", "--accept")


@task("Run pyright raw over both build trees",
      deps=("extract",), secondary=True)
def pyright(v: Vars) -> None:
    tool("pyright", "build/examples", "build/solutions")


section("Book builds (site, EPUB, PDF)")


@task("Build the site, serve it with live reload and copy-on-select, "
      "open a browser",
      deps=("site",))
def local(v: Vars) -> None:
    """--watch polls Chapters/ and rebuilds the edited chapter (one pandoc run,
    not a full site build), then the open page reloads itself.
    --copy-on-select makes a mouse selection copy itself to the clipboard
    as «text» (Chapter › Section), for lifting passages out of the
    rendered book. Both scripts are added
    to pages as they are served; build/site/ and the published site never
    carry them, and `tip serve` gets neither.
    """
    py("tools.serve", "--open", "--watch", "--copy-on-select")


@task("Serve build/site/ at http://localhost:8000 (no rebuilding)")
def serve(v: Vars) -> None:
    py("tools.serve")


@task("Render Chapters/ into build/site/ with pandoc")
def site(v: Vars) -> None:
    py("tools.build_site")


@task("Build the site, then test its link previews under jsdom (needs "
      "node)",
      deps=("site",))
def preview_check(v: Vars) -> None:
    """Hovers and taps every link on every built page under jsdom and fails on
    a link into the book that shows no panel, a navigation link that shows
    one, or a panel with something wrong in it. In no gate: it needs node,
    and its first run installs jsdom under build/node/ from the network.
    After an edit to resources/static/link-preview.js alone, `node
    tools/site_preview_check.js` reruns it against the site already built.
    """
    run(["node", "tools/site_preview_check.js"])


@task("Render Chapters/ into "
      "build/epub/ThinkingInPython-{color,eink}.epub with pandoc")
def epub(v: Vars) -> None:
    """Two EPUBs from the same Chapters/, for e-readers: -color (syntax
    highlighting in color, for backlit readers) and -eink (bolding instead, for
    grayscale screens). The site keeps one HTML page per chapter, so a
    cross-reference stays a link between files; an EPUB is a single document,
    so build_epub.py namespaces every heading id by chapter (ch12-immutability)
    before merging. Without that, the 44 chapters ending in `## Exercises` and
    the nine other repeated headings would collide and pandoc would quietly
    retarget those links. Needs pandoc, like `site`.
    """
    py("tools.build_epub")


@task("Render Chapters/ into build/pdf/ThinkingInPython.pdf with pandoc"
      " and typst")
def pdf(v: Vars) -> None:
    """One PDF from the same merged, anchor-namespaced Markdown stream the
    EPUB uses (build_pdf.py reuses build_epub.py's assembly), rendered by
    pandoc through typst. Typst draws the SVG diagrams directly and
    highlights the listings itself, so this build needs no rasterizer.
    Needs pandoc and the typst binary (`tip tools-check-full` verifies).
    """
    py("tools.build_pdf")


@task("Send the e-ink EPUB to a Kindle via the Send to Kindle app, "
      "rebuilding it first if stale (VARIANT=color for the other)")
def kindle(v: Vars) -> None:
    """Hands the built EPUB to Amazon's Send to Kindle desktop app, which
    opens its dialog with the file queued, and opens an Explorer window
    with the file selected for drag and drop; the Send click is the app's.
    Rebuilds the EPUB first (the same build as `epub`) only when it is
    missing or older than Chapters/, resources/, or the builder, so a
    fresh build is sent as-is. Excluded from verify-targets' smoke
    test: it opens a GUI.
    """
    py("tools.send_to_kindle", *v.words("VARIANT"))


@task("Build build/figures/index.html, a numbered gallery of every "
      "figure in the book, to check style by eye (`tip figures-open` "
      "opens it)")
def figures(v: Vars) -> None:
    """Every figure the prose references, in book order and numbered, on one
    page, with the SVG the site and PDF draw (read live from
    resources/images/) and the PNG the EPUB draws, to check the drawings
    against each other by eye: arrowheads, stroke widths, fonts, palette.
    A style line under each figure lists what it draws with and marks
    what falls outside the cover palette. Fails on a reference to a
    figure with no file, since the book would render nothing there. `tip
    verify` runs it, so the gallery tracks the working tree.
    """
    py("tools.figure_gallery")


@task("Build the figure gallery and open it in a browser", secondary=True)
def figures_open(v: Vars) -> None:
    py("tools.figure_gallery", "--open")


@task("Rebuild the covers from resources/cover-source.jpg (and the favicon)")
def cover(v: Vars) -> None:
    """The cover images and favicon are generated files under
    resources/static/, committed so the builds never depend on the
    generator's tools (resvg, Pillow). To use new cover art, drop
    the image at resources/cover-source.jpg and rerun this; with no
    source image the script falls back to its own drawn serpent.
    """
    py("tools.make_cover")


section("Publishing a release")


@task("Verify, rebuild the PDF and EPUBs, publish them with the reader "
      "guides as a GitHub release, then prune releases older than the "
      "newest two (VERSION=1.0)")
def release(v: Vars) -> None:
    """Publish a GitHub release whose uploaded assets are exactly the
    freshly rebuilt PDF and the two EPUBs. release.py orchestrates:
    preflight (clean tree, HEAD pushed, tag free, gh authenticated),
    then `tip verify` so a book that fails the gate can never ship,
    then fresh `tip pdf` + `tip epub`, then
    `gh release create vVERSION`. Deliberately excluded from
    verify-targets' smoke test: it tags the repo and publishes to GitHub.
    """
    py("tools.release", *v.words("VERSION"))


@task("Delete GitHub releases older than the newest two (their tags stay)")
def release_prune(v: Vars) -> None:
    """The prune step of `release` on its own. Tags stay, so history and the
    menu's next-version guess are untouched. Excluded from verify-targets'
    smoke test: it deletes from GitHub.
    """
    py("tools.release", "--prune")


@task("Run the full local gate: check, ty, ruff, run, pytest, site",
      deps=("gate", "site"))
def ci(v: Vars) -> None:
    """Mirrors the GitHub Actions gates plus a site build, all run locally. The
    default GitHub Actions path only builds and publishes the site; these gates
    run in CI only on request (see tools/README.md).
    """
    pass


also("kindle", "libs-check", "tools-status")


section("Style gates")


@task("Check tracked text files for CRLF; `tip fix-eol` converts them")
def eol(v: Vars) -> None:
    """Fail if any tracked text file has CRLF in the working tree.
    .gitattributes keeps the committed blobs LF; this catches a drifted working
    copy. Run `tip fix-eol` to convert offenders.
    """
    py("tools.check_line_endings")


@task("Convert any CRLF in tracked text files to LF", secondary=True)
def fix_eol(v: Vars) -> None:
    py("tools.check_line_endings", "--fix")


@task("Check listings keep blank lines minimal; `tip fix-listings` "
      "strips them")
def listings(v: Vars) -> None:
    """Fail if any ```python listing has more than one blank line in a row or a
    blank line between import groups. Run `tip fix-listings` to remove them.
    """
    py("tools.listing_format")


@task("Remove the offending blank lines from listings", secondary=True)
def fix_listings(v: Vars) -> None:
    py("tools.listing_format", "--fix")


@task("Fail if a listing line exceeds the 60-character width")
def widths(v: Vars) -> None:
    """Fail if any listing line in Chapters/ or Solutions/ is wider than 60
    characters (a trailing `# type: ignore` pragma is the one exemption).
    There is no fixer: wrap the statement, move the comment, or shorten
    the printed output.
    """
    py("tools.listing_width", "Chapters", "Solutions")


@task("Fail if any tools/data/banned_phrases.txt phrase is in the book")
def banned(v: Vars) -> None:
    """Fail if any phrase in tools/data/banned_phrases.txt appears anywhere in
    the book.
    """
    py("tools.banned_phrases")


@task("Fail if a one-line comment ends with a period; `tip "
      "fix-comment-periods` strips them")
def comment_periods(v: Vars) -> None:
    """A one-line listing comment ends without a period; only multiline
    comments use periods. Run `tip fix-comment-periods` to strip the offenders.
    """
    py("tools.comment_periods")


@task("Remove those trailing periods", secondary=True)
def fix_comment_periods(v: Vars) -> None:
    py("tools.comment_periods", "--fix")


@task("Fail if a prose comment is not capitalized; `tip "
      "fix-comment-caps` applies it")
def comment_caps(v: Vars) -> None:
    """A prose comment starts with a capital. Heuristic, so false positives are
    listed in tools/data/comment_caps_allow.txt. Run `tip fix-comment-caps` to
    apply.
    """
    py("tools.capitalize_comments")


@task("Capitalize them", secondary=True)
def fix_comment_caps(v: Vars) -> None:
    py("tools.capitalize_comments", "--write")


@task("Fail if an inline comment isn't two spaces after code; `tip "
      "fix-comment-spacing` collapses the gap")
def comment_spacing(v: Vars) -> None:
    """An inline comment (code precedes it on the line) must start exactly two
    spaces after the code; a full-line comment or a #: output marker is left
    alone. Run `tip fix-comment-spacing` to collapse the gap to two spaces.
    """
    py("tools.comment_spacing")


@task("Collapse inline-comment gaps to two spaces", secondary=True)
def fix_comment_spacing(v: Vars) -> None:
    py("tools.comment_spacing", "--fix")


@task("Fail if a heading-anchor link points at no real heading")
def anchors(v: Vars) -> None:
    """Fail if a heading-anchor link (file.md#id or #id) points at no real
    heading.
    """
    py("tools.heading_links", "Chapters", *GATE_DOCS)


@task("Fail if a footnote label is defined in more than one chapter")
def footnotes(v: Vars) -> None:
    """Fail if two chapters define the same [^label] footnote. The EPUB and
    PDF concatenate every chapter before pandoc sees them, and pandoc
    keeps a label's first definition, so the second chapter's note is
    silently replaced; the site, one page per chapter, never shows it.
    """
    py("tools.footnote_labels")


@task("Fail if a claim the book makes about its own chapters is false")
def self_reference(v: Vars) -> None:
    """Fail if the book says something about its own chapters that those
    chapters disprove: an "appears nowhere else" that does appear, or an
    "earlier chapter" link pointing forward. Both are settled by substring
    search, which is why they gate. The third rule in the tool, grounding,
    is advisory and lives in `self-reference-report` below.
    """
    py("tools.check_self_reference")


@task("Diff quoted ty diagnostics against their listings and the "
      "baseline (accept with `tip quoted-diagnostics-accept`)",
      deps=("extract",))
def quoted_diagnostics(v: Vars) -> None:
    """A quoted ty diagnostic is prose, so a listing edit that shifts a
    quoted line, or a ty upgrade that rewords a message, leaves the quote
    stale with every other gate green. This compares each quote's gutter
    lines with the extracted listing it points at. The dozen quotes the
    book deliberately makes against an edited copy (a line removed, a
    line added) live in tools/data/quoted_diagnostics_baseline.txt, and
    the run prints the delta: NEW fails the gate until the quote is fixed
    or, for a new deliberate edit, accepted. Part of `gate`.
    """
    py("tools.check_quoted_diagnostics", *v.words("ARGS"))


@task("Rewrite tools/data/quoted_diagnostics_baseline.txt from the "
      "current run",
      deps=("extract",), secondary=True)
def quoted_diagnostics_accept(v: Vars) -> None:
    py("tools.check_quoted_diagnostics", "--accept")


@task("Diff prose \"exercise N\" references against the exercise titles "
      "in the baseline (accept with `tip exercise-refs-accept`)")
def exercise_refs(v: Vars) -> None:
    """A sentence that names an exercise by number ("exercise 3 makes this
    concrete") is prose, so inserting or reordering an exercise leaves it
    pointing at the wrong one with every other gate green: the chapter's
    list and its Solutions headings still agree with each other. This
    pairs each reference with the Solutions title under its number and
    compares the pairs with tools/data/exercise_refs_baseline.txt. NEW
    fails the gate: reread the sentence against that title, then fix the
    number or accept the pair. Reads Markdown only. Part of `gate`.
    """
    py("tools.exercise_refs", *v.words("ARGS"))


@task("Rewrite tools/data/exercise_refs_baseline.txt from the current "
      "run",
      secondary=True)
def exercise_refs_accept(v: Vars) -> None:
    py("tools.exercise_refs", "--accept")


@task("Fail if two chapters name two listings the same")
def unique_slugs(v: Vars) -> None:
    """Fail if two chapters give different listings the same filename. Nothing
    else catches this: the two files land in different Examples/ directories,
    so the drift check passes, while a repo search for the name returns two
    unrelated listings and a pytest run can import the wrong one. `gate` runs
    it too, so a new collision fails the build; this target is the standalone
    way to ask the same question while editing.
    """
    py("tools.check_unique_slugs")


@task("Fail if a norun.txt or timing.txt pattern matches no listing")
def skip_lists(v: Vars) -> None:
    """Fail on a pattern in tools/data/norun.txt or tools/data/timing.txt that
    matches no file under Examples/ or SolutionsCode/. A renamed or deleted
    listing, or a renumbered chapter, leaves its pattern behind, and a stale
    timing.txt entry is the dangerous one: the listing's wall-clock marker
    stops being a claim, and the gate rewrites its next flip into the chapter
    with everything green. `gate` runs this right after the drift check, so the
    committed trees it reads are known to be current.
    """
    py("tools.check_skip_lists")


@task("Verify each chapter's exercises have matching solutions")
def solutions_numbering(v: Vars) -> None:
    """The one correspondence neither tree's own checks can see: whether the
    `## N.` headings here answer the exercises the chapter asks. Pure prose
    on both sides, so extract_solutions.py (code) and heading_links.py
    (anchors) both look straight past it. It also fails an `exercise_N.py`
    listing whose N is not its heading's number, which a reordering of the
    exercises leaves behind. Takes chapter numbers to check one, e.g.
    `tip solutions-numbering ARGS=19`.
    """
    py("tools.check_solutions", *v.words("ARGS"))


@task("Check every design pattern name is written *Capitalized*; `tip "
      "fix-pattern-names` rewrites the unambiguous ones")
def pattern_names(v: Vars) -> None:
    """Every naming of a design pattern is *Capitalized* and italic, on every
    mention, since names like State, Command, and Proxy are ordinary words
    otherwise. The names live in tools/data/pattern_names.txt. In GATE_CHECKS
    since 2026-09-16, once chapter 28's misses were fixed.
    """
    py("tools.pattern_names", *prose_files(v))


@task("Wrap plain pattern names in italics (sentence-start ambiguities "
      "are reported, not rewritten)",
      secondary=True)
def fix_pattern_names(v: Vars) -> None:
    py("tools.pattern_names", "--fix", *prose_files(v))


@task("Fail if a frozen data class after chapter 18 could be @record, "
      "or a @record has an unslotted base")
def records(v: Vars) -> None:
    """From chapter 18's utils/record.py on, a frozen data class is written
    @record. Fails on @dataclass(frozen=True) where every base is slotted,
    and on @record under a base with no __slots__. The deliberate long-form
    listings are in tools/data/record_exceptions.txt; run alone, this also
    fails on an entry there that matches nothing. Covers Chapters/ and
    Solutions/.
    """
    py("tools.record_check")


@task("Fail if a chapter's coupling panel SVG differs from its spec in "
      "tools/coupling_panels.py; `tip fix-coupling-panels` regenerates,"
      " `tip coupling-panels-png` rasterizes to look")
def coupling_panels(v: Vars) -> None:
    """The coupling-notation panel at the top of each pattern chapter (23-36)
    is generated from a per-chapter spec in tools/coupling_panels.py into
    resources/images/coupling_NN.svg. The spec names that chapter's classes and
    functions, so a listing rename means editing the spec and regenerating;
    this fails when a committed SVG differs from what the spec draws, so a
    stale panel cannot ride through the gate. In `gate` since 2026-09-23, the
    day the panels merged.
    """
    py("tools.coupling_panels", "--check")


@task("Regenerate resources/images/coupling_NN.svg from the specs",
      secondary=True)
def fix_coupling_panels(v: Vars) -> None:
    py("tools.coupling_panels")


@task("Rasterize every resources/images/coupling_*.svg into "
      "build/coupling/ with the EPUB's rasterizer, to check by eye",
      secondary=True)
def coupling_panels_png(v: Vars) -> None:
    """Text that fits in a browser can collide once rasterized, so look at a
    spec edit the way the EPUB will render it. Writes only build/coupling/.
    """
    py("tools.coupling_panels", "--png")


@task("Fail if resources/images/stateMachine.svg differs from its spec "
      "in tools/state_machine_figure.py; `tip fix-state-machine-figure`"
      " regenerates")
def state_machine_figure(v: Vars) -> None:
    """Chapter 31's vending-machine diagram is drawn from the spec in
    tools/state_machine_figure.py, since its labels have to sit beside
    thirteen curved transitions; this fails when the committed SVG differs
    from what the spec draws. In `gate` since 2026-09-24.
    """
    py("tools.state_machine_figure", "--check")


@task("Regenerate resources/images/stateMachine.svg from its spec",
      secondary=True)
def fix_state_machine_figure(v: Vars) -> None:
    py("tools.state_machine_figure")


@task("Run every Markdown check the gate enforces (ARGS=--list lists "
      "them); `tip fix-checks` applies the fixable ones")
def checks(v: Vars) -> None:
    """Every Markdown check at once, parsing each file once instead of per
    tool: check_all's whole registry, which is the GATE_CHECKS list the gate
    runs, so a bare `tip checks` answers "will the gate's Markdown checks
    pass?" and `sweep` runs it. The individual targets above still work. Vale
    is `tip prose`, so `tip checks prose` is the whole prose answer.
    """
    py("tools.check_all", *v.words("ARGS"))


@task("Apply every fix those checks can make", secondary=True)
def fix_checks(v: Vars) -> None:
    py("tools.check_all", "--fix")


section("Reports (advisory, no gate)")


@task("Check the book's external URLs for link rot (advisory, needs network)")
def links(v: Vars) -> None:
    """Advisory only, and deliberately not part of `verify` or `ci`: the
    network is flaky and a dead external site should never block a build. Run
    it now and then to catch link rot; heading_links.py covers internal links.
    """
    py("tools.check_links")


@task("List TODO(tag): ... markers left in the book (advisory)")
def todos(v: Vars) -> None:
    """Advisory only, like `links` above: lists `TODO(tag): ...` HTML-comment
    markers left in the Markdown (see tools/list_todos.py), each one an
    example that stays illustrative until something outside the book's
    control changes (a dependency ships a wheel, a build becomes the
    default). Never fails, and is not part of `verify`/`gate`/`ci`.
    """
    py("tools.list_todos")


@task("List cross-chapter links whose text makes an unchecked claim")
def claims(v: Vars) -> None:
    """Advisory. heading_links.py proves a cross-chapter link resolves; this
    asks the question it cannot, whether the target says what the link text
    claims. Most links either name the chapter or quote the target heading,
    and neither can drift; what is left is the handful of author-written
    phrases describing what is over there. Run one chapter with ARGS=33.
    """
    py("tools.check_claims", *v.words("ARGS"))


@task("List chapter sections that no exercise practices")
def exercise_coverage(v: Vars) -> None:
    """Advisory. Which `##` sections no exercise practices, per chapter. A
    worklist rather than a gate: a conclusion or a table wants no exercise,
    and the matching is literal, so it under-reports coverage. Confirm a
    reported section by eye. ARGS=18 for one chapter, ARGS=--deep for ###.
    """
    py("tools.exercise_coverage", *v.words("ARGS"))


@task("List listing comments added since a git ref (SINCE=ref, default "
      "HEAD; advisory)")
def comment_report(v: Vars) -> None:
    """Advisory. Lists the comments in listings that are new since a git
    ref, for a human to judge: a comment that says what its own line says
    (`class Contact:  # A Contact has a Name and an Address`) comes out,
    and no rule can tell that one from a comment that teaches. Directives,
    `#:` markers, and the file-name line are skipped. SINCE=v0.5.9 for a
    tag or commit (default HEAD, the uncommitted edits); ARGS=--all lists
    every comment in the book.
    """
    py("tools.comment_report", "--since", v.get("SINCE", "HEAD"),
       *v.words("ARGS"))


@task("List sentences attributing terms to a chapter that lacks them "
      "(advisory)")
def self_reference_report(v: Vars) -> None:
    """Advisory, like `claims`. Adds the grounding rule: a sentence linking to
    a chapter that contains none of the code terms the sentence names. It
    catches real misattributions and also fires on sentences whose terms
    belong to the linking chapter, so it reports rather than gates.
    """
    py("tools.check_self_reference", "--advisory", *v.words("ARGS"))


@task("Show every listing line wider than WIDTH=nn (default 60) in the "
      "browser (ARGS=--tsv for rows)",
      defaults={"WIDTH": "60"})
def code_width(v: Vars) -> None:
    """A survey, not a gate: every listing line wider than WIDTH (raw width,
    no pragma exemption), with its Examples/ or SolutionsCode/ path and
    line, its Markdown path and line, its width, and the line itself.
    For sizing questions ("what breaks at 50?"), not for enforcement.
    Writes build/reports/code_width.html and opens it in the browser,
    where a slider re-filters the width live, and stays running (Ctrl+C
    to stop) so a click on a row can open that line in Zed through its
    CLI. ARGS=--tsv prints one tab-separated row per line instead;
    ARGS=--no-open only writes the page.
    """
    py("tools.code_width", "--width", v.get("WIDTH", "60"),
       *v.words("ARGS"), "Chapters", "Solutions")


also("pyright-review", "libs-check", "gate-status", "tools-status")


section("Setup and upgrades")


@task("Check the tools a reader needs (uv, ty, ruff, pytest)")
def tools_check(v: Vars) -> None:
    """What a reader needs for the everyday commands below: uv, plus the
    uv-managed dev tools (ty, ruff, pytest). git is checked too but assumed
    present, since you needed it to get this far.
    """
    py("tools.check_tools")


@task("Check every tool, including pandoc, typst, and vale (site/pdf/prose)")
def tools_check_full(v: Vars) -> None:
    """Adds the tools a book maintainer needs for the rest of `tip help`:
    pandoc (site/local/epub/pdf), typst (pdf), and the standalone vale
    binary (prose).
    """
    py("tools.check_tools", "--full")


@task("Diagnose environment problems (stale uv, locked .venv); read-only")
def doctor(v: Vars) -> None:
    """Read-only: catches a stale uv silently stuck on an old Python
    prerelease, and (Windows) a process running from .venv that would lock it
    on upgrade. Prints the exact fix command instead of applying anything
    itself.
    """
    py("tools.doctor")


@task("Run the harness's own unit tests (tools/tests/)")
def tools_test(v: Vars) -> None:
    """The harness's own unit tests (tools/tests/), covering the shared library
    modules and the pure logic inside the entry points. Distinct from `test`,
    which runs the book's example tests under build/examples/. `gate` runs this
    first: every later step trusts these tools, so a broken one makes the rest
    of the gate's verdict meaningless.
    """
    tool("pytest", *v.words("PYTEST_N"), "tools/tests")


@task("Smoke-test every task; mutating ones run in a disposable "
      "worktree")
def verify_targets(v: Vars) -> None:
    """Runs every other target here and reports which ones fail.
    Read-only/idempotent targets run directly; a target that bakes
    --fix/--write/--add into its recipe (reflow, spell-add, fix-imports,
    fix-listings, fix-comment-periods, fix-comment-caps, fix-comment-spacing,
    and the clean-* targets, which would otherwise wipe the logs below) runs in
    a disposable git worktree instead, so this working tree is never touched.
    tools-upgrade, python-upgrade, serve, and local never run
    (network/environment mutation, or a server that blocks forever); see
    tools/verify_targets.py's docstring. Logs land in build/target_test_logs/.
    """
    py("tools.verify_targets")


@task("Report when the dev tools were last upgraded, and to what")
def tools_status(v: Vars) -> None:
    """When were the dev tools last upgraded, and to what? `tools-upgrade`
    writes this stamp; `gate` reads it and prints one line (nothing more,
    and never a failure) once it is older than tool_stamp.py's threshold.
    With no stamp yet, uv.lock's mtime stands in, so a fresh clone is
    correctly treated as current.
    """
    py("tools.tool_stamp")


@task("Compare the locked library versions (Stateless, numpy, ...) with"
      " the latest on PyPI")
def libs_check(v: Vars) -> None:
    """Is a release waiting for a library the listings import (Stateless,
    numpy, hypothesis, time-machine)? Reads uv.lock, asks PyPI for each
    one's latest version, and prints the ones that are behind. It changes
    nothing and always exits 0, offline included, and it joins no gate: a
    gate that reaches the network fails for reasons the book did not
    cause. Upgrade one library alone with `uv lock --upgrade-package NAME`
    and `uv sync`; CLAUDE.md's Stateless-upgrade entry says what to
    re-check afterward.
    """
    py("tools.libs_check")


@task("Update uv, the uv-managed dev tools, and (best-effort) global "
      "ty/pandoc/typst/vale")
def tools_upgrade(v: Vars) -> None:
    """Updates uv itself (when it was installed via its standalone installer),
    best-effort upgrades a globally installed `ty` (`uv tool upgrade ty`,
    what bare `ty` on PATH resolves to), then upgrades every uv-managed dev
    tool (ty, ruff, pytest, ...) to the latest version pyproject.toml
    allows, rewriting uv.lock. pandoc, typst, and vale are updated
    best-effort through winget or Homebrew, whichever is on PATH.
    git is left alone. Review `git diff uv.lock` before committing.
    For the pinned Python version itself, use `tip python-upgrade`.

    Ends by stamping the upgrade (so the gate can stop nagging) and running
    `sweep`, which reports every check the new tools broke rather than
    stopping at the first. A failing sweep here means the upgrade landed
    and the book needs fixing, not that the upgrade failed; the stamp is
    written first for that reason.
    """
    py("tools.upgrade_tools")
    invoke("tools-check-full", v)
    py("tools.tool_stamp", "--write")
    invoke("sweep", v)


@task("Upgrade the dev Python (latest patch; TO=3.15 to repin a minor),"
      " resync, verify")
def python_upgrade(v: Vars) -> None:
    """Upgrade the development Python and re-check the book against it. `tip
    python-upgrade` pulls the latest patch of the pinned minor (from
    .python-version); `tip python-upgrade TO=3.15` repins to a new minor first
    (rewriting .python-version and the requires-python floor). Both resync the
    venv and run the gate. Run through `uv run --no-project` so the
    orchestrating interpreter is not the venv that `uv sync` rebuilds.
    """
    run(["uv", "run", "--no-project", "python", "-m",
         "tools.upgrade_python", *v.words("TO")])
    invoke("verify", v)


section("Rust examples (rust/, needs cargo)")

# The crates under rust/ that chapter 18's Rust section builds.
CRATES = ["fastcount"]


@task("Sync every crate from the book, then build and run its demo "
      "(needs cargo and rustc)", deps=("rust-sync", "rust-test"))
def rust_all(v: Vars) -> None:
    """Chapter 18's PyO3/maturin crates, kept apart from every other
    task: nothing outside this section enters rust/ or needs a Rust
    toolchain, so `verify`, `gate`, and `ci` work with none installed.
    `uv run` builds each crate through maturin (its pyproject.toml names
    maturin as the build backend) into its own .venv/ under the crate,
    so nothing here touches the repository root's .venv either.
    """


@task("Regenerate each crate's src/lib.rs and demo.py from Chapters/")
def rust_sync(v: Vars) -> None:
    """Never touches the rest of a crate (Cargo.toml, pyproject.toml,
    .gitignore, .python-version): those are real, hand-maintained
    project files, not generated by this step.
    """
    py("tools.extract_rust", "--write")


@task("Build and install every crate, via maturin, without running "
      "its demo")
def rust_build(v: Vars) -> None:
    """`uv sync` alone builds and installs a crate (via maturin, in
    release mode) without running anything, useful to separate "does it
    compile" from "does the demo pass".
    """
    for crate in CRATES:
        run(["uv", "sync"], cwd=ROOT / "rust" / crate)


@task("Build every crate and run its demo.py against the real extension")
def rust_test(v: Vars) -> None:
    for crate in CRATES:
        run(["uv", "run", "python", "demo.py"], cwd=ROOT / "rust" / crate)


@task("Remove every crate's target/ and .venv/ (does not touch the book)")
def rust_clean(v: Vars) -> None:
    for crate in CRATES:
        remove(f"rust/{crate}/target")
        remove(f"rust/{crate}/.venv")


section("Cleanup")


@task("Remove all of build/ (clean-examples, -solutions, -site, -epub, "
      "-pdf remove one subdirectory each)")
def clean(v: Vars) -> None:
    """Everything under build/ is derived and gitignored, so wiping it loses
    nothing that a gate or build cannot regenerate. The stamps go too: the
    next `gate-status` reports no passing run and the next `gate` re-checks
    the tools, which is the honest state after a full clean. On Windows a
    shell whose cwd sits inside build/ holds the directory open and the
    rmtree fails silently (ignore_errors); run this from the repo root.
    """
    remove("build")


@task("Remove build/examples/", secondary=True)
def clean_examples(v: Vars) -> None:
    remove("build/examples")


@task("Remove build/solutions/", secondary=True)
def clean_solutions(v: Vars) -> None:
    remove("build/solutions")


@task("Remove build/site/", secondary=True)
def clean_site(v: Vars) -> None:
    remove("build/site")


@task("Remove build/epub/", secondary=True)
def clean_epub(v: Vars) -> None:
    remove("build/epub")


@task("Remove build/pdf/", secondary=True)
def clean_pdf(v: Vars) -> None:
    remove("build/pdf")
