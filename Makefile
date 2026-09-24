# Thinking in Python: build and verification targets.
# Tooling is managed by uv, so targets run through `uv run`. Override with
# `make PY=python ...` to use a plain interpreter. On Windows the quickest way to
# get GNU Make is winget (pre-installed on modern Windows):
#   winget install ezwinports.make
# Restart the terminal, then `make --version` to confirm.

PY ?= uv run python
TY ?= uv run ty
PYRIGHT ?= uv run pyright
PYTEST ?= uv run pytest
RUFF ?= uv run ruff
# Extra pytest args. The suite is tiny, so serial is fastest today; enable
# xdist as it grows with `make test PYTEST_N="-n auto"`.
PYTEST_N ?=
SPELL ?= uv run codespell
VALE ?= vale
DOCS ?= Chapters Solutions
# Files for spell/prose: all of DOCS, or one chapter via CH= (a number or
# stem prefix), e.g. `make prose CH=33` or `make prose CH=33_Patterns--Visitor`.
# CH= covers the chapter and its Solutions file together; $(wildcard)
# drops the half that does not exist, and a CH matching nothing falls
# back to the unmatched Chapters pattern so the tool still errors
# loudly instead of silently linting everything.
PROSE_CH = $(wildcard Chapters/$(CH)*.md Solutions/$(CH)*.md)
PROSE_FILES = $(if $(CH),$(if $(PROSE_CH),$(PROSE_CH),Chapters/$(CH)*.md),$(DOCS))
# Extra args for `make verify`, e.g. `make verify ARGS=--help` to list
# its steps (tools/verify.py's VERIFY_TARGETS) without running them.
ARGS ?=

# Every target here is phony: none names a file it builds. This used to be
# one 70-name line that nothing kept in step with the file, so it is now
# split per section, each list sitting under the heading it covers. GNU Make
# accumulates .PHONY across lines, so the effect is the same.
.PHONY: help

# Self-documenting help, interactive in a terminal. `make` and `make help`
# both open tools/help_picker.py when stdin and stdout are a terminal:
# arrow keys or the mouse choose a target, Enter runs it, Esc leaves. A
# pipe, CI, or `--pick never` gets the static listing instead, which is
# what verify-targets and the tests see. Every target below carries an inline
# `## text` doc comment, and a `##@ Name` line starts a new section. Put a
# target's one-line doc on its own target line so `make help` and the recipe
# never drift apart; anything longer goes in a plain `#` comment above it.
# `##-` in place of `##` marks a target secondary: still documented and still
# smoke-tested by `make verify-targets`, but folded out of the listing because
# a sibling's doc text names it (`fix-eol` under `eol`). A `##+ name name`
# line repeats targets defined in other sections into the section it sits
# in, at that point in the listing, so the everyday section can show
# `check-ch` and `spell` without moving their definitions. The sections
# run from the everyday loop down to setup and cleanup: what you run most
# is at the top of the menu, what you run rarely at the bottom.
# Parsed by tools/make_help.py instead of grep/awk, so help has no dependency
# on a POSIX toolchain being on PATH (every other target already needs Python).
#
# `make help style` names a section. Make has no subcommands, so it would
# otherwise read `style` as a second goal and fail with "No rule to make
# target 'style'". This turns the word after `help` into a do-nothing target,
# and only when `help` is the first goal, so a typo in any other position
# still fails loudly. make_help.py refuses to run if a section slug ever
# equals a real target name, which is the one case where this guard would
# override a recipe.
ifeq ($(firstword $(MAKECMDGOALS)),help)
  HELP_TOPIC := $(word 2,$(MAKECMDGOALS))
  ifneq ($(HELP_TOPIC),)
    .PHONY: $(HELP_TOPIC)
    $(eval $(HELP_TOPIC):;@:)
  endif
endif

help:  ## Pick a target to run, or list them all when piped (`make help style` narrows to one section)
	@$(PY) -m tools.make_help $(HELP_TOPIC)

# `make run-one box_view` names the listing as a second word, the same
# way `make help style` names a section: the word after `run-one`
# becomes a do-nothing target and is exported as F, which the child
# make that runs the real `run-one` rule reads from its environment.
# `make run-one F=box_view` still works, and an F= on the command line
# takes precedence over the word. Only the first word after `run-one`
# gets this treatment, so a third word fails loudly. Under `TIMED=0`
# the real rules share this make's namespace, so a listing whose name
# is also a target (`make TIMED=0 run-one test`) needs the F= form.
ifeq ($(firstword $(MAKECMDGOALS)),run-one)
  RUN_ONE_ARG := $(word 2,$(MAKECMDGOALS))
  ifneq ($(RUN_ONE_ARG),)
    export F ?= $(RUN_ONE_ARG)
    .PHONY: $(RUN_ONE_ARG)
    $(eval $(RUN_ONE_ARG):;@:)
  endif
endif

# Every goal named on the command line runs in a child make under
# tools/timed_make.py, which prints `make <goal>: 12.3s` (or the exit
# code and the time, on failure) after the goal's own output. The child
# runs with TIMED=1, which selects the real rules below, and GNU Make
# hands a command-line variable on to every make the child starts, so a
# nested `$(MAKE)` or a per-target subprocess in verify.py and
# sweep_checks.py prints no line of its own (those two time each step
# themselves). `make TIMED=0 verify` runs the rules directly with no
# timing. `make -n` still shows the real recipe: GNU Make runs a recipe
# line that names $(MAKE) even under -n, and the child inherits -n.
# `help` is never timed. The matching `endif` is the last line of this
# file.
TIMED ?=
ifeq ($(TIMED),)
TIMED_GOALS := $(filter-out help $(HELP_TOPIC) $(RUN_ONE_ARG),$(MAKECMDGOALS))
ifneq ($(TIMED_GOALS),)
.PHONY: $(TIMED_GOALS)
$(TIMED_GOALS):
	@$(PY) -m tools.timed_make "$(MAKE)" $@
endif
else

##@ Everyday

.PHONY: verify-ch verify sweep gate solutions-gate gate-status

# `make verify` scoped to one chapter and its Solutions file, in a few
# seconds instead of tens: fix-eol, reflow, both extracts, this chapter's
# #: markers (chapter and Solutions), both syncs and drift checks, the
# Markdown gates on these two files, then ty/ruff/run/pytest over the
# chapter's directory in each build tree. GATE_CHECKS is passed through so
# the Markdown checks are the gate's by construction. It writes no gate
# stamp: a change that can reach other chapters (a renamed listing, a
# utils/ helper, a heading others link to) still needs `make verify`.
verify-ch:  ## The verify loop for one chapter and its Solutions file (CH=28), a few seconds
	$(PY) -m tools.verify_chapter $(CH) --checks $(GATE_CHECKS)

##+ check-ch run-one

# The edit-and-check loop to repeat after touching a chapter: every
# mutating fixer (the comment-style fixers, import sorting, blank-line
# cleanup), a refresh of the #: output markers, a sync of the committed
# Examples/ and SolutionsCode/ trees, the figure gallery, then the full
# gate. Each fixer repairs something the gate would otherwise fail on,
# and the gate already self-heals line endings, reflow, and markers, so
# a fixer-free loop would only trade a fix for a failure. The marker
# refresh runs before the sync on purpose: the gate refreshes markers
# too, but only after its own sync step already copied the Markdown, so
# a stale marker would otherwise stay one sync behind until the next
# run caught it up. The ordered step list, and the doc text ARGS=--help
# prints for each one, both live in tools/verify.py (VERIFY_TARGETS);
# add a target there to include it, nothing else needs to change.
verify:  ## The everyday loop: every fixer, refresh #: markers, sync Examples/ and SolutionsCode/, figures, then every gate but the site build (ARGS=--help lists the steps)
	$(PY) -m tools.verify $(ARGS)

# `gate` stops at its first failure, and since `solutions-gate` is one of
# its prerequisites, that half runs first and can hide every Chapters/
# failure behind it. So one `gate` rarely shows the whole blast radius of
# a tool upgrade. This runs every static check over both trees to
# completion and summarizes which failed. `tools-upgrade` ends with it;
# run it directly after any change wide enough that the first failure is
# unlikely to be the only one. The #: markers are excluded on purpose
# (see the script docstring).
sweep:  ## Run every check over both trees, reporting all failures instead of the first
	$(PY) -m tools.sweep_checks

# The Markdown checks the gate enforces, run together by check_all.py in one
# process with one parse per file, rather than as separate scripts. Names
# come from `make checks ARGS=--list`. This is check_all's whole registry:
# prose-lint joined once its last findings were cleared, and widths joined
# when the book moved to 60-character listings, so a new violation of
# either now fails the gate rather than sitting in a backlog. widths also
# runs over Solutions/ (a separate recipe line below), since Solutions
# listings render on the same small screens. records runs there too:
# most of the book's frozen data classes are in Solutions/.
GATE_CHECKS = listings widths banned comment-periods comment-caps comment-spacing anchors footnotes self-reference prose-lint pattern-names records

# Markdown outside Chapters/ that still carries intra-document links worth
# gating. Only `anchors` runs over it: `banned` would fire on the tooling
# README's own worked example of a banned phrase (and on the `from
# __future__ import annotations` lines still in a few Solutions listings),
# and the listing checks have no ```python blocks to inspect in the README.
# Two of these links were dead for a while precisely because nothing looked
# outside Chapters/, and three anchors in Solutions/ were dead for the same
# reason. check_solutions.py covers the other half of a Solutions link, the
# `../Chapters/` prefix that `anchors` cannot see is missing.
GATE_DOCS = tools/README.md Solutions

# The local gate without the site build: line endings, listing density, drift
# check, output markers, ty, ruff, run, pytest, plus the same checks for
# Solutions/ (solutions-gate). `verify` runs `sync` first;
# `ci` adds the site. validate_output.py runs with --update: a stale #: marker
# self-heals (rewriting Chapters/) the same way fix-eol/sync already do,
# rather than failing the build. A raised exception where none is expected
# still fails the gate; only marker text is self-corrected. The drift check
# also fails on an orphaned stray under Examples/ (a file no block generates
# and no chapter mentions); run `make prune` to delete those.
# solutions-gate applies the same stray check to SolutionsCode/ against
# Solutions/*.md; `prune` covers that tree too.
# reflow_prose.py runs here with --write, so prose that drifts out of
# Semantic Line Breaks self-heals (rewriting Chapters/) the same way
# fix-eol and validate_output's marker --update do, instead of failing the
# build and forcing a `make reflow` plus a second full run. The safety
# valve stays: a paragraph that fails reflow's round-trip check is never
# rewritten, and that failure still exits nonzero and stops the gate.
gate: solutions-gate  ## The gate without sync or site (check, reflow, slugs, output, ty, ruff, run, pytest, solutions-gate)
	$(PYTEST) $(PYTEST_N) tools/tests
	$(PY) -m tools.check_line_endings
	$(PY) -m tools.check_all $(GATE_CHECKS)
	$(PY) -m tools.check_all anchors --paths $(GATE_DOCS)
	$(PY) -m tools.check_all widths records --paths Solutions
	$(PY) -m tools.coupling_panels --check
	$(PY) -m tools.check_quoted_diagnostics
	$(PY) -m tools.exercise_refs
	$(PY) -m tools.reflow_prose --write
	$(PY) -m tools.check_unique_slugs
	$(PY) -m tools.extract_examples
	$(PY) -m tools.check_skip_lists
	$(PY) -m tools.extract_examples --write
	$(PY) -m tools.validate_output --update Chapters
	$(TY) check build/examples
	$(RUFF) check build/examples
	$(PY) -m tools.run_examples
	$(PYTEST) $(PYTEST_N) build/examples
	$(PY) -m tools.gate_stamp --write gate
	$(PY) -m tools.tool_stamp --nag

# Mirrors `gate`, but for Solutions/: numbering, drift check, output
# markers, ty, ruff, run, pytest. This skipped the run step until
# 2026-08-31, on the reasoning that every extractable block carries a #:
# marker and so is already executed by the marker refresh. That was wrong:
# 24 answers carry no marker and are not tests, so nothing ran them, and
# the first run over the tree found one that could not execute at all. It costs
# about six seconds. The numbering check runs first because it is the
# cheapest and reports a missing answer, which no later step here would
# notice. extract_solutions.py also fails on an orphaned stray under
# SolutionsCode/; `make prune` deletes exactly those. Folded out of the
# listing: `gate` names it, and `gate` is what you run.
solutions-gate:  ##- The Solutions gate: numbering, check, output, ty, ruff, run, pytest
	$(PY) -m tools.check_solutions
	$(PY) -m tools.extract_solutions
	$(PY) -m tools.extract_solutions --write
	$(PY) -m tools.validate_output --update --tree "$(CURDIR)/build/solutions" Solutions
	$(TY) check build/solutions
	$(RUFF) check build/solutions
	$(PY) -m tools.run_examples --tree "$(CURDIR)/build/solutions"
	$(PYTEST) $(PYTEST_N) build/solutions

# When did the book last pass the gate, and has anything changed since?
# The stamp records a hash per Chapters/ and Solutions/ file, so this
# answers the second half too. `gate` writes it; `verify`, `ci`, and `all`
# inherit it, since each runs `gate`.
gate-status:  ## Report when the gate last passed and what changed since
	$(PY) -m tools.gate_stamp

##+ local spell prose

# Headed "Writing" rather than "Prose" for the same reason as "Code
# examples" above: `prose` is a target in this section.
##@ Writing and spelling

.PHONY: spell spell-add prose reflow reflow-check rewrite

# Spell-check the book and lint it for small mechanical slips. codespell
# catches known misspellings (prose and code comments); prose_lint catches
# spacing/blank-line/punctuation slips; spellcheck.py is a full-dictionary check
# of the prose, with accepted terms in tools/data/wordlist.txt. Run one chapter with
# CH= (e.g. `make spell CH=29`) or a path with DOCS=.
spell:  ## codespell + prose_lint + full-dictionary spellcheck (CH=29 for one)
	$(SPELL) $(PROSE_FILES)
	$(PY) -m tools.prose_lint $(PROSE_FILES)
	$(PY) -m tools.spellcheck $(PROSE_FILES)

# Accept every word spellcheck.py doesn't recognize into tools/data/wordlist.txt
# and every word codespell flags into tools/data/codespell-ignore.txt (both
# sorted, deduplicated) instead of failing. The two checkers keep separate
# lists, and codespell reads code where spellcheck.py reads prose only, so
# a class name codespell dislikes needs the second list. It cannot tell a
# real term from a typo, so always review the diff before committing; a
# real typo belongs in the prose, not in either list.
spell-add:  ## Accept every unknown word: spellcheck's into wordlist.txt, codespell's into codespell-ignore.txt (review the diff!)
	$(PY) -m tools.spellcheck $(PROSE_FILES) --add

# House-style lint with Vale: no em-dashes and no filler phrases. Run one
# chapter with CH= (e.g. `make prose CH=29`) or a path with DOCS=.
# Vale is a standalone binary (not uv-managed); see .vale.ini for install notes.
prose:  ## House-style lint with Vale (CH=29 for one chapter; needs vale binary)
	$(VALE) $(PROSE_FILES)

##+ checks pattern-names

# Rewrite prose paragraphs to one sentence per line (code, tables, lists, and
# headings are left untouched; a file is rewritten only if it round-trips).
# Target one chapter with CH=, e.g. `make reflow CH=02` or `make reflow CH=Tour`.
reflow:  ## Rewrite prose to one sentence per line (CH=02 for one chapter)
	$(PY) -m tools.reflow_prose --write $(CH)

reflow-check:  ## Report which chapters would reflow, no write (CH=02 for one)
	$(PY) -m tools.reflow_prose $(CH)

# AI editing passes over one chapter's prose, edited in place. Each pass
# is one headless `claude -p "/<skill> <chapter>"` run. Reflow and the
# prose gates run after every pass, and the chain stops at the first
# failure. It costs tokens and is nondeterministic, so it is never part
# of verify/gate/ci, refuses to run under CI, and needs a `git diff`
# review before you commit.
#
# The passes, in the order they run (PASSES in tools/rewrite.py):
#
#   elements-of-style  default  Strunk: active voice, positive form,
#                               omit needless words
#   activate           opt-in   clear the passive, there-is, and
#                               weak-verb warnings from `make prose`
#   literal            default  say what the machinery does: a literal
#                               verb for each figure of speech
#   positive           default  say what happens, not what does not:
#                               keep only the negations that claim
#   straighten         default  one sentence, one load: name the actor,
#                               split at the seam
#   cohesion           default  old before new: one topic string per
#                               paragraph, the news at the end
#   antecedents        default  name what each this/it/which points at
#                               when two things could be meant
#   readability        opt-in   remove AI-writing tells; its own rule
#                               is "only when asked", so it never runs
#                               unless you name it here
#   bruce-edit-apply   default  apply the promoted rules in
#                               bruce_edit_db.md
#
# A bare `make rewrite CH=25` runs the seven defaults. To add an opt-in
# pass to them: ARGS="--also activate". To run only the passes you
# name: ARGS="--passes activate readability". To run all nine:
# ARGS=--all. ARGS=--list prints this table; ARGS=--dry-run prints the
# commands without running them.
#
# Several chapters run in parallel: CH="25 28 30" or CH=30-40 (a range,
# inclusive; CH="25 30-32" mixes them) runs one pass chain per chapter,
# four at a time (ARGS=-j2 changes that). Each chain edits
# only its own chapter and checks only its own chapter, so they never
# trip each other, and their output arrives per step under a [NN]
# prefix. ARGS=--serial runs them one after another with output
# streamed live, the mode for watching a pass work.
#
# Each pass names its own model (PASSES in tools/rewrite.py; ARGS=--list
# shows them). MODEL= forces one model on every pass for a run:
# MODEL=claude-sonnet-5 is the cheap lap. Each pass header prints the
# model it used.
MODEL ?=
rewrite:  ## AI editing passes over chapters' prose (CH="25 28"; MODEL=; ARGS=--list)
	$(PY) -m tools.rewrite $(CH) $(if $(MODEL),--model $(MODEL)) $(ARGS)

##@ Code examples (build/examples/, build/solutions/)

.PHONY: check-ch run-one run by-hand output output-check test ty lint \
        fix-imports sync check prune extract pyright-review pyright-accept \
        pyright

# The edit loop for one chapter's listings. `gate` checks all 44 chapters and
# spends most of its time executing listings you did not touch; this runs the
# same code-example checks (markers, listing style, ty, ruff, pytest) against
# one chapter, in about a second. It is not a substitute for `gate`, which
# also catches cross-chapter breakage: run that before committing.
check-ch:  ## Run the code checks for one chapter only (CH=12), ~1s
	$(PY) -m tools.check_chapter $(CH)

# Run one example the way the book assumes: from inside its own chapter
# directory, with the tree's utils/ on PYTHONPATH, so its sibling imports
# and data files resolve and `from benchmark import report` finds the shared
# helper. F takes a path or just the file's name (F=deque_timing). It reads
# Examples/, the committed tree, so it needs no extract step, and it prints
# the equivalent cd + PYTHONPATH commands before running: that is what you
# type when this target is not at hand. `make run-one deque_timing` is the
# same as F=deque_timing (the block under `help` turns the word into F).
run-one:  ## Run one example and show its output (`make run-one deque_timing`, or F=)
	$(PY) -m tools.run_one_example $(F)

# These all read the build trees, so each depends on `extract` to rebuild
# them first. make builds `extract` once per invocation, so depending on it
# from several targets does not re-extract, and `extract` wipes each tree
# before writing it, so a stale tree (a gitignored build/ left over from an
# older Markdown) never survives to be checked. Each target covers both
# trees. `output` alone executes only a block that carries a #: marker and
# `test` only a test_*.py, which together leave two dozen Solutions answers
# that nothing else runs (importable helpers, and standalone programs whose
# behavior the answer describes in prose), so `run` runs every one. The
# absolute --tree is required, not stylistic: it goes on PYTHONPATH, and a
# relative path stops resolving the moment an example changes directory.
run: extract  ## Run every extracted .py in both build trees and report failures
	$(PY) -m tools.run_examples
	$(PY) -m tools.run_examples --tree "$(CURDIR)/build/solutions"

# Start every example listed under `# [by-hand]` in tools/data/norun.txt,
# all at once, each from its own chapter directory with utils/ on
# PYTHONPATH. Today that is the five Tkinter views, which no gate executes.
# Try each window and close it; the tool prints a line as each one ends,
# then the traceback of any that exited nonzero, and exits 1 if one did.
# ARGS=--list prints what would start and opens nothing. Excluded from
# verify-targets' smoke test: it opens windows and waits for a human.
by-hand:  ## Open every example that needs a human, all at once, and report how each one exits (ARGS=--list to only list them)
	$(PY) -m tools.by_hand $(ARGS)

# Rewrite the #: output markers inside the Markdown's ```python listings, in
# Chapters/ and Solutions/, to the stdout each listing actually produces.
# Depends on extract so each listing runs from its build directory, where its
# sibling imports and data files live. validate_output.py needs an absolute
# --tree for Solutions: a block runs with cwd inside build/solutions/<chapter>,
# and a relative tree argument stops resolving once cwd changes (the same
# gotcha run_examples.py's --tree has; see tools/README.md).
output: extract  ## Update the #: output markers in Chapters/ and Solutions/ listings
	$(PY) -m tools.validate_output --update Chapters
	$(PY) -m tools.validate_output --update --tree "$(CURDIR)/build/solutions" Solutions

# Same, but report mismatches instead of rewriting (a gate-friendly check).
output-check: extract  ## Verify the #: output markers in Chapters/ and Solutions/ without rewriting
	$(PY) -m tools.validate_output Chapters
	$(PY) -m tools.validate_output --tree "$(CURDIR)/build/solutions" Solutions

# One pytest run per tree, so a failure report names the tree it is in.
test: extract  ## Run the pytest examples (test_*.py) in both build trees
	$(PYTEST) $(PYTEST_N) build/examples
	$(PYTEST) $(PYTEST_N) build/solutions

# One ty run over both trees, so a failure in build/examples never hides
# one in build/solutions (a failing recipe line stops the lines after it).
ty: extract  ## Type-check build/examples/ and build/solutions/ (must be clean)
	$(TY) check build/examples build/solutions

lint: extract  ## PEP8-lint both build trees with ruff (must be clean)
	$(RUFF) check build/examples build/solutions

# Organize imports in the book's python listings (ruff's I rule), writing the
# result back into the Markdown. Depends on extract so ruff sees each listing's
# siblings and classifies imports the way the lint gate does.
fix-imports: extract  ## Sort imports and drop unused ones in the listings (ruff I,F401), in the Markdown
	$(PY) -m tools.fix_imports --fix

# Write the extracted trees straight into the committed copies, Examples/
# from Chapters/ and SolutionsCode/ from Solutions/, so the drift check
# passes. Run after editing a code block. Each Solutions block is
# self-contained (it redeclares whatever book context it needs) rather
# than importing from Examples/, so that tree never breaks when a book
# example changes.
sync:  ## Update the committed Examples/ and SolutionsCode/ trees from the Markdown
	$(PY) -m tools.extract_examples --write -o Examples
	$(PY) -m tools.extract_solutions --write -o SolutionsCode

check:  ## Verify the committed Examples/ and SolutionsCode/ trees match the Markdown
	$(PY) -m tools.extract_examples
	$(PY) -m tools.extract_solutions

# `check`/`gate` already fail on an orphaned stray (a file under Examples/
# with no matching block and no mention anywhere in the book, typically left
# behind by a rename). This deletes exactly those; a stray whose filename is
# still mentioned somewhere in the book is left alone for a human to review.
# It prunes SolutionsCode/ in the same run, since a renamed listing that
# both trees copy (a utils/ helper) otherwise fails solutions-gate after
# the Examples/ prune looked complete.
prune:  ## Delete orphaned stray files under Examples/ and SolutionsCode/ (see `check`)
	$(PY) -m tools.extract_examples --prune
	$(PY) -m tools.extract_solutions --prune

# Both build trees, each wiped before it is written.
extract:  ## Write build/examples/ and build/solutions/ from the Markdown
	$(PY) -m tools.extract_examples --write
	$(PY) -m tools.extract_solutions --write

# Pyright is a second opinion, not a gate. The listings carry no pyright
# suppressions; every disagreement with `ty` is an entry in
# tools/data/pyright_baseline.txt, and the review prints only the delta:
# NEW (a fresh disagreement) and GONE (pyright caught up, or the listing
# changed). Read it after editing listings or after `make tools-upgrade`
# moves pyright. `pyright` is the raw run.
pyright-review: extract  ## Diff pyright over both trees against the baseline (advisory; accept with `make pyright-accept`)
	$(PY) -m tools.pyright_review

pyright-accept: extract  ##- Rewrite tools/data/pyright_baseline.txt from the current pyright run
	$(PY) -m tools.pyright_review --accept

pyright: extract  ##- Run pyright raw over both build trees
	$(PYRIGHT) build/examples build/solutions

##@ Book builds (site, EPUB, PDF)

.PHONY: local serve site preview-check epub pdf kindle figures figures-open \
        cover

# --watch polls Chapters/ and rebuilds the edited chapter (one pandoc run,
# not a full site build), then the open page reloads itself.
# --copy-on-select makes a mouse selection copy itself to the clipboard
# as «text» (Chapter › Section), for lifting passages out of the
# rendered book. Both scripts are added
# to pages as they are served; build/site/ and the published site never
# carry them, and `make serve` gets neither.
local: site  ## Build the site, serve it with live reload and copy-on-select, open a browser
	$(PY) -m tools.serve --open --watch --copy-on-select

serve:  ## Serve build/site/ at http://localhost:8000 (no rebuilding)
	$(PY) -m tools.serve

site:  ## Render Chapters/ into build/site/ with pandoc
	$(PY) -m tools.build_site

# Hovers and taps every link on every built page under jsdom and fails on
# a link into the book that shows no panel, a navigation link that shows
# one, or a panel with something wrong in it. In no gate: it needs node,
# and its first run installs jsdom under build/node/ from the network.
# After an edit to resources/static/link-preview.js alone, `node
# tools/site_preview_check.js` reruns it against the site already built.
preview-check: site  ## Build the site, then test its link previews under jsdom (needs node)
	node tools/site_preview_check.js

# Two EPUBs from the same Chapters/, for e-readers: -color (syntax
# highlighting in color, for backlit readers) and -eink (bolding
# instead, for grayscale screens). The site keeps one HTML page per
# chapter, so a cross-reference stays a link between files; an EPUB
# is a single document, so build_epub.py namespaces every heading id by
# chapter (ch12-immutability) before merging. Without that, the 44 chapters
# ending in `## Exercises` and the nine other repeated headings would collide
# and pandoc would quietly retarget those links. Needs pandoc, like `site`.
epub:  ## Render Chapters/ into build/epub/ThinkingInPython-{color,eink}.epub with pandoc
	$(PY) -m tools.build_epub

# One PDF from the same merged, anchor-namespaced Markdown stream the
# EPUB uses (build_pdf.py reuses build_epub.py's assembly), rendered by
# pandoc through typst. Typst draws the SVG diagrams directly and
# highlights the listings itself, so this build needs no rasterizer.
# Needs pandoc and the typst binary (`make tools-check-full` verifies).
pdf:  ## Render Chapters/ into build/pdf/ThinkingInPython.pdf with pandoc and typst
	$(PY) -m tools.build_pdf

# Hands the built EPUB to Amazon's Send to Kindle desktop app, which
# opens its dialog with the file queued, and opens an Explorer window
# with the file selected for drag and drop; the Send click is the app's.
# Rebuilds the EPUB first (the same build as `epub`) only when it is
# missing or older than Chapters/, resources/, or the builder, so a
# fresh build is sent as-is. Excluded from verify-targets' smoke
# test: it opens a GUI.
kindle:  ## Send the e-ink EPUB to a Kindle via the Send to Kindle app, rebuilding it first if stale (VARIANT=color for the other)
	$(PY) -m tools.send_to_kindle $(VARIANT)

# Every figure the prose references, in book order and numbered, on one
# page, with the SVG the site and PDF draw (read live from
# resources/images/) and the PNG the EPUB draws, to check the drawings
# against each other by eye: arrowheads, stroke widths, fonts, palette.
# A style line under each figure lists what it draws with and marks
# what falls outside the cover palette. Fails on a reference to a
# figure with no file, since the book would render nothing there. `make
# all` runs it, so the gallery tracks the working tree.
figures:  ## Build build/figures/index.html, a numbered gallery of every figure in the book, to check style by eye (`make figures-open` opens it)
	$(PY) -m tools.figure_gallery

figures-open:  ##- Build the figure gallery and open it in a browser
	$(PY) -m tools.figure_gallery --open

# The cover images and favicon are generated files under
# resources/static/, committed so the builds never depend on the
# generator's tools (resvg, Pillow). To use new cover art, drop
# the image at resources/cover-source.jpg and rerun this; with no
# source image the script falls back to its own drawn serpent.
cover:  ## Rebuild the covers from resources/cover-source.jpg (and the favicon)
	$(PY) -m tools.make_cover

##@ Publishing a release

.PHONY: release release-prune ci

# Publish a GitHub release whose uploaded assets are exactly the
# freshly rebuilt PDF and the two EPUBs. release.py orchestrates:
# preflight (clean tree, HEAD pushed, tag free, gh authenticated),
# then `make verify` so a book that fails the gate can never ship,
# then fresh `make pdf` + `make epub`, then
# `gh release create v$(VERSION)`. Deliberately excluded from
# verify-targets' smoke test: it tags the repo and publishes to GitHub.
release:  ## Verify, rebuild the PDF and EPUBs, publish them with the reader guides as a GitHub release, then prune releases older than the newest two (VERSION=1.0)
	$(PY) -m tools.release $(VERSION)

# The prune step of `release` on its own. Tags stay, so history and the
# menu's next-version guess are untouched. Excluded from verify-targets'
# smoke test: it deletes from GitHub.
release-prune:  ## Delete GitHub releases older than the newest two (their tags stay)
	$(PY) -m tools.release --prune

# Mirrors the GitHub Actions gates plus a site build, all run locally. The
# default GitHub Actions path only builds and publishes the site; these gates
# run in CI only on request (see tools/README.md).
ci: gate site  ## Run the full local gate: check, ty, ruff, run, pytest, site

##+ kindle libs-check tools-status

##@ Style gates

.PHONY: eol fix-eol listings fix-listings widths banned comment-periods \
        fix-comment-periods comment-caps fix-comment-caps comment-spacing \
        fix-comment-spacing anchors footnotes self-reference \
        quoted-diagnostics quoted-diagnostics-accept exercise-refs \
        exercise-refs-accept unique-slugs skip-lists solutions-numbering \
        pattern-names fix-pattern-names records coupling-panels \
        fix-coupling-panels coupling-panels-png checks fix-checks

# Every check here has a `fix-` counterpart, named in the check's own doc
# text and marked `##-` so the listing shows one row per rule instead of two.

# Fail if any tracked text file has CRLF in the working tree. .gitattributes
# keeps the committed blobs LF; this catches a drifted working copy. Run
# `$(PY) -m tools.check_line_endings --fix` to convert offenders.
eol:  ## Check tracked text files for CRLF; `make fix-eol` converts them
	$(PY) -m tools.check_line_endings

fix-eol:  ##- Convert any CRLF in tracked text files to LF
	$(PY) -m tools.check_line_endings --fix

# Fail if any ```python listing has more than one blank line in a row or a
# blank line between import groups. Run `make fix-listings` to remove them.
listings:  ## Check listings keep blank lines minimal; `make fix-listings` strips them
	$(PY) -m tools.listing_format

fix-listings:  ##- Remove the offending blank lines from listings
	$(PY) -m tools.listing_format --fix

# Fail if any listing line in Chapters/ or Solutions/ is wider than 60
# characters (a trailing `# type: ignore` pragma is the one exemption).
# There is no fixer: wrap the statement, move the comment, or shorten
# the printed output.
widths:  ## Fail if a listing line exceeds the 60-character width
	$(PY) -m tools.listing_width Chapters Solutions

# Fail if any phrase in tools/data/banned_phrases.txt appears anywhere in the book.
banned:  ## Fail if any tools/data/banned_phrases.txt phrase is in the book
	$(PY) -m tools.banned_phrases

# A one-line listing comment ends without a period; only multiline comments use
# periods. Run `make fix-comment-periods` to strip the offenders.
comment-periods:  ## Fail if a one-line comment ends with a period; `make fix-comment-periods` strips them
	$(PY) -m tools.comment_periods

fix-comment-periods:  ##- Remove those trailing periods
	$(PY) -m tools.comment_periods --fix

# A prose comment starts with a capital. Heuristic, so false positives are
# listed in tools/data/comment_caps_allow.txt. Run `make fix-comment-caps` to apply.
comment-caps:  ## Fail if a prose comment is not capitalized; `make fix-comment-caps` applies it
	$(PY) -m tools.capitalize_comments

fix-comment-caps:  ##- Capitalize them
	$(PY) -m tools.capitalize_comments --write

# An inline comment (code precedes it on the line) must start exactly two
# spaces after the code; a full-line comment or a #: output marker is left
# alone. Run `make fix-comment-spacing` to collapse the gap to two spaces.
comment-spacing:  ## Fail if an inline comment isn't two spaces after code; `make fix-comment-spacing` collapses the gap
	$(PY) -m tools.comment_spacing

fix-comment-spacing:  ##- Collapse inline-comment gaps to two spaces
	$(PY) -m tools.comment_spacing --fix

# Fail if a heading-anchor link (file.md#id or #id) points at no real heading.
anchors:  ## Fail if a heading-anchor link points at no real heading
	$(PY) -m tools.heading_links Chapters $(GATE_DOCS)

# Fail if two chapters define the same [^label] footnote. The EPUB and
# PDF concatenate every chapter before pandoc sees them, and pandoc
# keeps a label's first definition, so the second chapter's note is
# silently replaced; the site, one page per chapter, never shows it.
footnotes:  ## Fail if a footnote label is defined in more than one chapter
	$(PY) -m tools.footnote_labels

# Fail if the book says something about its own chapters that those
# chapters disprove: an "appears nowhere else" that does appear, or an
# "earlier chapter" link pointing forward. Both are settled by substring
# search, which is why they gate. The third rule in the tool, grounding,
# is advisory and lives in `self-reference-report` below.
self-reference:  ## Fail if a claim the book makes about its own chapters is false
	$(PY) -m tools.check_self_reference

# A quoted ty diagnostic is prose, so a listing edit that shifts a
# quoted line, or a ty upgrade that rewords a message, leaves the quote
# stale with every other gate green. This compares each quote's gutter
# lines with the extracted listing it points at. The dozen quotes the
# book deliberately makes against an edited copy (a line removed, a
# line added) live in tools/data/quoted_diagnostics_baseline.txt, and
# the run prints the delta: NEW fails the gate until the quote is fixed
# or, for a new deliberate edit, accepted. Part of `gate`.
quoted-diagnostics: extract  ## Diff quoted ty diagnostics against their listings and the baseline (accept with `make quoted-diagnostics-accept`)
	$(PY) -m tools.check_quoted_diagnostics $(ARGS)

quoted-diagnostics-accept: extract  ##- Rewrite tools/data/quoted_diagnostics_baseline.txt from the current run
	$(PY) -m tools.check_quoted_diagnostics --accept

# A sentence that names an exercise by number ("exercise 3 makes this
# concrete") is prose, so inserting or reordering an exercise leaves it
# pointing at the wrong one with every other gate green: the chapter's
# list and its Solutions headings still agree with each other. This
# pairs each reference with the Solutions title under its number and
# compares the pairs with tools/data/exercise_refs_baseline.txt. NEW
# fails the gate: reread the sentence against that title, then fix the
# number or accept the pair. Reads Markdown only. Part of `gate`.
exercise-refs:  ## Diff prose "exercise N" references against the exercise titles in the baseline (accept with `make exercise-refs-accept`)
	$(PY) -m tools.exercise_refs $(ARGS)

exercise-refs-accept:  ##- Rewrite tools/data/exercise_refs_baseline.txt from the current run
	$(PY) -m tools.exercise_refs --accept

# Fail if two chapters give different listings the same filename. Nothing
# else catches this: the two files land in different Examples/ directories,
# so the drift check passes, while a repo search for the name returns two
# unrelated listings and a pytest run can import the wrong one. `gate` runs
# it too, so a new collision fails the build; this target is the standalone
# way to ask the same question while editing.
unique-slugs:  ## Fail if two chapters name two listings the same
	$(PY) -m tools.check_unique_slugs

# Fail on a pattern in tools/data/norun.txt or tools/data/timing.txt that
# matches no file under Examples/ or SolutionsCode/. A renamed or deleted
# listing, or a renumbered chapter, leaves its pattern behind, and a stale
# timing.txt entry is the dangerous one: the listing's wall-clock marker
# stops being a claim, and the gate rewrites its next flip into the chapter
# with everything green. `gate` runs this right after the drift check, so
# the committed trees it reads are known to be current.
skip-lists:  ## Fail if a norun.txt or timing.txt pattern matches no listing
	$(PY) -m tools.check_skip_lists

# The one correspondence neither tree's own checks can see: whether the
# `## N.` headings here answer the exercises the chapter asks. Pure prose
# on both sides, so extract_solutions.py (code) and heading_links.py
# (anchors) both look straight past it. It also fails an `exercise_N.py`
# listing whose N is not its heading's number, which a reordering of the
# exercises leaves behind. Takes chapter numbers to check one, e.g.
# `make solutions-numbering ARGS=19`.
solutions-numbering:  ## Verify each chapter's exercises have matching solutions
	$(PY) -m tools.check_solutions $(ARGS)

# Every naming of a design pattern is *Capitalized* and italic, on every
# mention, since names like State, Command, and Proxy are ordinary words
# otherwise. The names live in tools/data/pattern_names.txt. In GATE_CHECKS
# since 2026-09-16, once chapter 28's misses were fixed.
pattern-names:  ## Check every design pattern name is written *Capitalized*; `make fix-pattern-names` rewrites the unambiguous ones
	$(PY) -m tools.pattern_names $(PROSE_FILES)

fix-pattern-names:  ##- Wrap plain pattern names in italics (sentence-start ambiguities are reported, not rewritten)
	$(PY) -m tools.pattern_names --fix $(PROSE_FILES)

# From chapter 18's utils/record.py on, a frozen data class is written
# @record. Fails on @dataclass(frozen=True) where every base is slotted,
# and on @record under a base with no __slots__. The deliberate long-form
# listings are in tools/data/record_exceptions.txt; run alone, this also
# fails on an entry there that matches nothing. Covers Chapters/ and
# Solutions/.
records:  ## Fail if a frozen data class after chapter 18 could be @record, or a @record has an unslotted base
	$(PY) -m tools.record_check

# The coupling-notation panel at the top of each pattern chapter (23-36)
# is generated from a per-chapter spec in tools/coupling_panels.py into
# resources/images/coupling_NN.svg. The spec names that chapter's classes
# and functions, so a listing rename means editing the spec and
# regenerating; this fails when a committed SVG differs from what the spec
# draws, so a stale panel cannot ride through the gate. In `gate` since
# 2026-09-23, the day the panels merged.
coupling-panels:  ## Fail if a chapter's coupling panel SVG differs from its spec in tools/coupling_panels.py; `make fix-coupling-panels` regenerates, `make coupling-panels-png` rasterizes to look
	$(PY) -m tools.coupling_panels --check

fix-coupling-panels:  ##- Regenerate resources/images/coupling_NN.svg from the specs
	$(PY) -m tools.coupling_panels

# Text that fits in a browser can collide once rasterized, so look at a
# spec edit the way the EPUB will render it. Writes only build/coupling/.
coupling-panels-png:  ##- Rasterize every resources/images/coupling_*.svg into build/coupling/ with the EPUB's rasterizer, to check by eye
	$(PY) -m tools.coupling_panels --png

# Every Markdown check at once, parsing each file once instead of per tool:
# check_all's whole registry, which is the GATE_CHECKS list the gate runs,
# so a bare `make checks` answers "will the gate's Markdown checks pass?"
# and `sweep` runs it. The individual targets above still work. Vale is
# `make prose`, so `make checks prose` is the whole prose answer.
checks:  ## Run every Markdown check the gate enforces (ARGS=--list lists them); `make fix-checks` applies the fixable ones
	$(PY) -m tools.check_all $(ARGS)

fix-checks:  ##- Apply every fix those checks can make
	$(PY) -m tools.check_all --fix

##@ Reports (advisory, no gate)

.PHONY: links todos claims exercise-coverage comment-report \
        self-reference-report code-width

# Advisory only, and deliberately not part of `verify` or `ci`: the network
# is flaky and a dead external site should never block a build. Run it now
# and then to catch link rot; heading_links.py covers internal links.
links:  ## Check the book's external URLs for link rot (advisory, needs network)
	$(PY) -m tools.check_links

# Advisory only, like `links` above: lists `TODO(tag): ...` HTML-comment
# markers left in the Markdown (see tools/list_todos.py), each one an
# example that stays illustrative until something outside the book's
# control changes (a dependency ships a wheel, a build becomes the
# default). Never fails, and is not part of `verify`/`gate`/`ci`.
todos:  ## List TODO(tag): ... markers left in the book (advisory)
	$(PY) -m tools.list_todos

# Advisory. heading_links.py proves a cross-chapter link resolves; this
# asks the question it cannot, whether the target says what the link text
# claims. Most links either name the chapter or quote the target heading,
# and neither can drift; what is left is the handful of author-written
# phrases describing what is over there. Run one chapter with ARGS=33.
claims:  ## List cross-chapter links whose text makes an unchecked claim
	$(PY) -m tools.check_claims $(ARGS)

# Advisory. Which `##` sections no exercise practices, per chapter. A
# worklist rather than a gate: a conclusion or a table wants no exercise,
# and the matching is literal, so it under-reports coverage. Confirm a
# reported section by eye. ARGS=18 for one chapter, ARGS=--deep for ###.
exercise-coverage:  ## List chapter sections that no exercise practices
	$(PY) -m tools.exercise_coverage $(ARGS)

# Advisory. Lists the comments in listings that are new since a git
# ref, for a human to judge: a comment that says what its own line says
# (`class Contact:  # A Contact has a Name and an Address`) comes out,
# and no rule can tell that one from a comment that teaches. Directives,
# `#:` markers, and the file-name line are skipped. SINCE=v0.5.9 for a
# tag or commit (default HEAD, the uncommitted edits); ARGS=--all lists
# every comment in the book.
comment-report:  ## List listing comments added since a git ref (SINCE=ref, default HEAD; advisory)
	$(PY) -m tools.comment_report --since $(or $(SINCE),HEAD) $(ARGS)

# Advisory, like `claims`. Adds the grounding rule: a sentence linking to
# a chapter that contains none of the code terms the sentence names. It
# catches real misattributions and also fires on sentences whose terms
# belong to the linking chapter, so it reports rather than gates.
self-reference-report:  ## List sentences attributing terms to a chapter that lacks them (advisory)
	$(PY) -m tools.check_self_reference --advisory $(ARGS)

# A survey, not a gate: every listing line wider than WIDTH (raw width,
# no pragma exemption), with its Examples/ or SolutionsCode/ path and
# line, its Markdown path and line, its width, and the line itself.
# For sizing questions ("what breaks at 50?"), not for enforcement.
# Writes build/reports/code_width.html and opens it in the browser,
# where a slider re-filters the width live, and stays running (Ctrl+C
# to stop) so a click on a row can open that line in Zed through its
# CLI. ARGS=--tsv prints one tab-separated row per line instead;
# ARGS=--no-open only writes the page.
WIDTH ?= 60
code-width:  ## Show every listing line wider than WIDTH=nn (default 60) in the browser (ARGS=--tsv for rows)
	$(PY) -m tools.code_width --width $(WIDTH) $(ARGS) Chapters Solutions

##+ pyright-review libs-check gate-status tools-status

##@ Setup and upgrades

.PHONY: tools-check tools-check-full doctor tools-test verify-targets \
        tools-status libs-check tools-upgrade python-upgrade

# What a reader needs for the everyday commands below: uv, plus the
# uv-managed dev tools (ty, ruff, pytest). make and git are checked too but
# assumed present, since you needed both to get this far.
tools-check:  ## Check the tools a reader needs (uv, ty, ruff, pytest)
	$(PY) -m tools.check_tools

# Adds the tools a book maintainer needs for the rest of `make help`:
# pandoc (site/local/epub/pdf), typst (pdf), and the standalone vale
# binary (prose).
tools-check-full:  ## Check every tool, including pandoc, typst, and vale (site/pdf/prose)
	$(PY) -m tools.check_tools --full

# Read-only: catches a stale uv silently stuck on an old Python prerelease,
# and (Windows) a process running from .venv that would lock it on upgrade.
# Prints the exact fix command instead of applying anything itself.
doctor:  ## Diagnose environment problems (stale uv, locked .venv); read-only
	$(PY) -m tools.doctor

# The harness's own unit tests (tools/tests/), covering the shared library
# modules and the pure logic inside the entry points. Distinct from `test`,
# which runs the book's example tests under build/examples/. `gate` runs
# this first: every later step trusts these tools, so a broken one makes
# the rest of the gate's verdict meaningless.
tools-test:  ## Run the harness's own unit tests (tools/tests/)
	$(PYTEST) $(PYTEST_N) tools/tests

# Runs every other target here and reports which ones fail. Read-only/idempotent
# targets run directly; a target that bakes --fix/--write/--add into its recipe
# (reflow, spell-add, fix-imports, fix-listings, fix-comment-periods,
# fix-comment-caps, fix-comment-spacing, and the clean-* targets, which
# would otherwise wipe the logs below) runs in a disposable git worktree
# instead, so this working tree is never touched. tools-upgrade, python-upgrade,
# serve, and local never run (network/environment mutation, or a server that
# blocks forever); see tools/verify_targets.py's docstring. Logs land in
# build/target_test_logs/.
verify-targets:  ## Smoke-test every make target; mutating ones run in a disposable worktree
	$(PY) -m tools.verify_targets

# When were the dev tools last upgraded, and to what? `tools-upgrade`
# writes this stamp; `gate` reads it and prints one line (nothing more,
# and never a failure) once it is older than tool_stamp.py's threshold.
# With no stamp yet, uv.lock's mtime stands in, so a fresh clone is
# correctly treated as current.
tools-status:  ## Report when the dev tools were last upgraded, and to what
	$(PY) -m tools.tool_stamp

# Is a release waiting for a library the listings import (Stateless,
# numpy, hypothesis, time-machine)? Reads uv.lock, asks PyPI for each
# one's latest version, and prints the ones that are behind. It changes
# nothing and always exits 0, offline included, and it joins no gate: a
# gate that reaches the network fails for reasons the book did not
# cause. Upgrade one library alone with `uv lock --upgrade-package NAME`
# and `uv sync`; CLAUDE.md's Stateless-upgrade entry says what to
# re-check afterward.
libs-check:  ## Compare the locked library versions (Stateless, numpy, ...) with the latest on PyPI
	$(PY) -m tools.libs_check

# Updates uv itself (when it was installed via its standalone installer),
# best-effort upgrades a globally installed `ty` (`uv tool upgrade ty`,
# what bare `ty` on PATH resolves to), then upgrades every uv-managed dev
# tool (ty, ruff, pytest, ...) to the latest version pyproject.toml
# allows, rewriting uv.lock. pandoc, typst, and vale are updated
# best-effort through winget or Homebrew, whichever is on PATH.
# make/git are left alone. Review `git diff uv.lock` before committing.
# For the pinned Python version itself, use `make python-upgrade`.
#
# Ends by stamping the upgrade (so the gate can stop nagging) and running
# `sweep`, which reports every check the new tools broke rather than
# stopping at the first. A failing sweep here means the upgrade landed
# and the book needs fixing, not that the upgrade failed; the stamp is
# written first for that reason.
tools-upgrade:  ## Update uv, the uv-managed dev tools, and (best-effort) global ty/pandoc/typst/vale
	$(PY) -m tools.upgrade_tools
	$(MAKE) tools-check-full
	$(PY) -m tools.tool_stamp --write
	$(MAKE) sweep

# Upgrade the development Python and re-check the book against it.
# `make python-upgrade` pulls the latest patch of the pinned minor (from
# .python-version); `make python-upgrade TO=3.15` repins to a new minor first
# (rewriting .python-version and the requires-python floor). Both resync the
# venv and run the gate. Run through `uv run --no-project` so the orchestrating
# interpreter is not the venv that `uv sync` rebuilds.
python-upgrade:  ## Upgrade the dev Python (latest patch; TO=3.15 to repin a minor), resync, verify
	uv run --no-project python -m tools.upgrade_python $(TO)
	$(MAKE) verify

##@ Cleanup

.PHONY: clean clean-examples clean-solutions clean-site clean-epub clean-pdf

# Everything under build/ is derived and gitignored, so wiping it loses
# nothing that a gate or build cannot regenerate. The stamps go too: the
# next `gate-status` reports no passing run and the next `gate` re-checks
# the tools, which is the honest state after a full clean. On Windows a
# shell whose cwd sits inside build/ holds the directory open and the
# rmtree fails silently (ignore_errors); run this from the repo root.
clean:  ## Remove all of build/ (clean-examples, -solutions, -site, -epub, -pdf remove one subdirectory each)
	$(PY) -c "import shutil; shutil.rmtree('build', ignore_errors=True)"

clean-examples:  ##- Remove build/examples/
	$(PY) -c "import shutil; shutil.rmtree('build/examples', ignore_errors=True)"

clean-solutions:  ##- Remove build/solutions/
	$(PY) -c "import shutil; shutil.rmtree('build/solutions', ignore_errors=True)"

clean-site:  ##- Remove build/site/
	$(PY) -c "import shutil; shutil.rmtree('build/site', ignore_errors=True)"

clean-epub:  ##- Remove build/epub/
	$(PY) -c "import shutil; shutil.rmtree('build/epub', ignore_errors=True)"

clean-pdf:  ##- Remove build/pdf/
	$(PY) -c "import shutil; shutil.rmtree('build/pdf', ignore_errors=True)"

endif  # TIMED
