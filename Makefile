# Thinking in Python: build and verification targets.
# Tooling is managed by uv, so targets run through `uv run`. Override with
# `make PY=python ...` to use a plain interpreter. On Windows the quickest way to
# get GNU Make is winget (pre-installed on modern Windows):
#   winget install ezwinports.make
# Restart the terminal, then `make --version` to confirm.

PY ?= uv run python
TY ?= uv run ty
PYTEST ?= uv run pytest
RUFF ?= uv run ruff
# Extra pytest args. The suite is tiny, so serial is fastest today; enable
# xdist as it grows with `make test PYTEST_N="-n auto"`.
PYTEST_N ?=
SPELL ?= uv run codespell
VALE ?= vale
DOCS ?= Chapters Solutions
# Files for spell/prose: all of DOCS, or one chapter via CH= (a number or
# stem prefix), e.g. `make prose CH=29` or `make prose CH=29_Visitor`.
# CH= covers the chapter and its Solutions file together; $(wildcard)
# drops the half that does not exist, and a CH matching nothing falls
# back to the unmatched Chapters pattern so the tool still errors
# loudly instead of silently linting everything.
PROSE_CH = $(wildcard Chapters/$(CH)*.md Solutions/$(CH)*.md)
PROSE_FILES = $(if $(CH),$(if $(PROSE_CH),$(PROSE_CH),Chapters/$(CH)*.md),$(DOCS))
# Extra args for `make all`, e.g. `make all ARGS=--help` to list its
# targets (tools/run_all.py's ALL_TARGETS) without running them.
ARGS ?=

# Every target here is phony: none names a file it builds. This used to be
# one 70-name line that nothing kept in step with the file, so it is now
# split per section, each list sitting under the heading it covers. GNU Make
# accumulates .PHONY across lines, so the effect is the same.
.PHONY: help

# Self-documenting help, in two levels. Every target below carries an inline
# `## text` doc comment, and a `##@ Name` line starts a new section. Put a
# target's one-line doc on its own target line so `make help` and the recipe
# never drift apart; anything longer goes in a plain `#` comment above it.
# `##-` in place of `##` marks a target secondary: still documented and still
# smoke-tested by `make verify-targets`, but folded out of the listing because
# a sibling's doc text names it (`fix-eol` under `eol`).
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

help:  ## Show this help (`make help style` expands one section)
	@$(PY) tools/make_help.py $(HELP_TOPIC)

##@ Setup

.PHONY: tools-check tools-check-full doctor verify-targets tools-test \
        tools-upgrade

# What a reader needs for the everyday commands below: uv, plus the
# uv-managed dev tools (ty, ruff, pytest). make and git are checked too but
# assumed present, since you needed both to get this far.
tools-check:  ## Check the tools a reader needs (uv, ty, ruff, pytest)
	$(PY) tools/check_tools.py

# Adds the tools a book maintainer needs for the rest of `make help`:
# pandoc (site/local/epub/pdf), typst (pdf), and the standalone vale
# binary (prose).
tools-check-full:  ## Check every tool, including pandoc, typst, and vale (site/pdf/prose)
	$(PY) tools/check_tools.py --full

# Read-only: catches a stale uv silently stuck on an old Python prerelease,
# and (Windows) a process running from .venv that would lock it on upgrade.
# Prints the exact fix command instead of applying anything itself.
doctor:  ## Diagnose environment problems (stale uv, locked .venv); read-only
	$(PY) tools/doctor.py

# Runs every other target here and reports which ones fail. Read-only/idempotent
# targets run directly; a target that bakes --fix/--write/--add into its recipe
# (reflow, spell-add, fix-imports, fix-listings, fix-comment-periods,
# fix-comment-caps, fix-comment-spacing) runs in a disposable git worktree
# instead, so this working tree is never touched. tools-upgrade, python-upgrade,
# serve, and local never run (network/environment mutation, or a server that
# blocks forever); see tools/verify_targets.py's docstring. Logs land in
# build/target_test_logs/.
verify-targets:  ## Smoke-test every make target; mutating ones run in a disposable worktree
	$(PY) tools/verify_targets.py

# The harness's own unit tests (tools/tests/), covering the shared library
# modules and the pure logic inside the entry points. Distinct from `test`,
# which runs the book's example tests under build/examples/. `gate` runs
# this first: every later step trusts these tools, so a broken one makes
# the rest of the gate's verdict meaningless.
tools-test:  ## Run the harness's own unit tests (tools/tests/)
	$(PYTEST) $(PYTEST_N) tools/tests

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
	$(PY) tools/upgrade_tools.py
	$(MAKE) tools-check-full
	$(PY) tools/tool_stamp.py --write
	$(MAKE) sweep

##@ Everyday

.PHONY: all verify sync-ci gate gate-status tools-status sweep ci reset \
        python-upgrade

# The edit-and-check loop to repeat after touching a chapter: every
# mutating fixer (reflow, the comment-style fixers, import sorting,
# blank-line cleanup), a refresh of the #: output markers, a sync of the
# generated trees, then the full gate. The marker refresh runs before the
# sync on purpose, so a stale #: marker converges in this one run instead
# of needing a second `make all` to catch up. The ordered target list, and
# the doc text `ARGS=--help` prints for each one, both live in
# tools/run_all.py (ALL_TARGETS) -- add a target there to include it,
# nothing else needs to change.
all:  ## Run every everyday fixer plus sync and gate; ARGS=--help lists them without running
	$(PY) tools/run_all.py $(ARGS)

# Fix any CRLF in the working tree, refresh the #: output markers, sync
# Examples/ and SolutionsCode/ from the Markdown, then run every gate except
# the site build. The everyday "is everything still good?" command after
# editing Chapters/ or Solutions/. Order matters: fix-eol runs first so the
# eol check inside gate sees an already-clean tree, and output/
# solutions-output (which rewrite stale #: markers) run before sync/
# solutions-sync so the marker rewrite is what gets synced, not a since-
# corrected-in-place Markdown -- reversing that leaves Examples/
# SolutionsCode one run behind whenever a marker needed fixing.
verify: fix-eol output solutions-output sync solutions-sync gate  ## Fix line endings, refresh #: markers, sync Examples/ and SolutionsCode/, then run every gate except the site build

# Same as verify, plus the site build at the end.
sync-ci: output solutions-output sync solutions-sync ci  ## Like verify, plus the site build (the full CI gate)

# The Markdown checks the gate enforces, run together by check_all.py in one
# process with one parse per file, rather than as separate scripts. Names
# come from `make checks ARGS=--list`. This is check_all's whole registry:
# prose-lint joined once its last findings were cleared, and widths joined
# when the book moved to 60-character listings, so a new violation of
# either now fails the gate rather than sitting in a backlog. widths also
# runs over Solutions/ (a separate recipe line below), since Solutions
# listings render on the same small screens.
GATE_CHECKS = listings widths banned comment-periods comment-caps comment-spacing anchors prose-lint

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
# Solutions/ (solutions-gate). `verify` runs `sync`/`solutions-sync` first;
# `ci` adds the site. validate_output.py runs with --update: a stale #: marker
# self-heals (rewriting Chapters/) the same way fix-eol/sync already do,
# rather than failing the build. A raised exception where none is expected
# still fails the gate; only marker text is self-corrected. The drift check
# also fails on an orphaned stray under Examples/ (a file no block generates
# and no chapter mentions); run `make prune` to delete those.
# solutions-gate applies the same stray check to SolutionsCode/ against
# Solutions/*.md, with `make solutions-prune` as its counterpart.
# reflow_prose.py runs here with --write, so prose that drifts out of
# Semantic Line Breaks self-heals (rewriting Chapters/) the same way
# fix-eol and validate_output's marker --update do, instead of failing the
# build and forcing a `make reflow` plus a second full run. The safety
# valve stays: a paragraph that fails reflow's round-trip check is never
# rewritten, and that failure still exits nonzero and stops the gate.
gate: solutions-gate  ## The gate without sync or site (check, reflow, slugs, output, ty, ruff, run, pytest, solutions-gate)
	$(PYTEST) $(PYTEST_N) tools/tests
	$(PY) tools/check_line_endings.py
	$(PY) tools/check_all.py $(GATE_CHECKS)
	$(PY) tools/check_all.py anchors --paths $(GATE_DOCS)
	$(PY) tools/check_all.py widths --paths Solutions
	$(PY) tools/reflow_prose.py --write
	$(PY) tools/check_unique_slugs.py
	$(PY) tools/extract_examples.py
	$(PY) tools/extract_examples.py --write
	$(PY) tools/validate_output.py --update Chapters
	$(TY) check build/examples
	$(RUFF) check build/examples
	$(PY) tools/run_examples.py
	$(PYTEST) $(PYTEST_N) build/examples
	$(PY) tools/gate_stamp.py --write gate
	$(PY) tools/tool_stamp.py --nag

# When did the book last pass the gate, and has anything changed since?
# The stamp records a hash per Chapters/ and Solutions/ file, so this
# answers the second half too. `gate` writes it; `verify`, `ci`, and `all`
# inherit it, since each runs `gate`.
gate-status:  ## Report when the gate last passed and what changed since
	$(PY) tools/gate_stamp.py

# When were the dev tools last upgraded, and to what? `tools-upgrade`
# writes this stamp; `gate` reads it and prints one line (nothing more,
# and never a failure) once it is older than tool_stamp.py's threshold.
# With no stamp yet, uv.lock's mtime stands in, so a fresh clone is
# correctly treated as current.
tools-status:  ## Report when the dev tools were last upgraded, and to what
	$(PY) tools/tool_stamp.py

# `gate` stops at its first failure, and since `solutions-gate` is one of
# its prerequisites, that half runs first and can hide every Chapters/
# failure behind it. So one `gate` rarely shows the whole blast radius of
# a tool upgrade. This runs every static check over both trees to
# completion and summarizes which failed. `tools-upgrade` ends with it;
# run it directly after any change wide enough that the first failure is
# unlikely to be the only one. The #: markers are excluded on purpose
# (see the script docstring).
sweep:  ## Run every check over both trees, reporting all failures instead of the first
	$(PY) tools/sweep_checks.py

# Mirrors the GitHub Actions gates plus a site build, all run locally. The
# default GitHub Actions path only builds and publishes the site; these gates
# run in CI only on request (see tools/README.md).
ci: gate site  ## Run the full local gate: check, ty, ruff, run, pytest, site

# Throw away build/examples/ and rebuild it from the Markdown. Run this when
# a check reports drift you cannot explain (a stale tree from an older Markdown,
# or one carried over from another machine).
reset: clean-examples extract  ## Regenerate build/examples/ from the Markdown (fixes drift)
	@echo "build/examples/ regenerated from the Markdown."

# Upgrade the development Python and re-check the book against it.
# `make python-upgrade` pulls the latest patch of the pinned minor (from
# .python-version); `make python-upgrade TO=3.15` repins to a new minor first
# (rewriting .python-version and the requires-python floor). Both resync the
# venv and run the gate. Run through `uv run --no-project` so the orchestrating
# interpreter is not the venv that `uv sync` rebuilds.
python-upgrade:  ## Upgrade the dev Python (latest patch; TO=3.15 to repin a minor), resync, verify
	uv run --no-project python tools/upgrade_python.py $(TO)
	$(MAKE) verify

##@ Build and site

.PHONY: sync check prune site cover epub pdf release local serve

# Write the extracted tree straight into Examples/, syncing the committed copy
# to the Markdown. Run after editing a code block so the drift check passes.
sync:  ## Update the committed Examples/ tree from the Markdown
	$(PY) tools/extract_examples.py --write -o Examples

check:  ## Verify book examples match the committed Examples/ tree
	$(PY) tools/extract_examples.py

# `check`/`gate` already fail on an orphaned stray (a file under Examples/
# with no matching block and no mention anywhere in the book, typically left
# behind by a rename). This deletes exactly those; a stray whose filename is
# still mentioned somewhere in the book is left alone for a human to review.
prune:  ## Delete orphaned stray files under Examples/ (see `check`)
	$(PY) tools/extract_examples.py --prune

site:  ## Render Chapters/ into build/site/ with pandoc
	$(PY) tools/build_site.py

# The cover images and favicon are generated files under
# resources/static/, committed so the builds never depend on the
# generator's tools (resvg, Pillow). To use new cover art, drop
# the image at resources/cover-source.jpg and rerun this; with no
# source image the script falls back to its own drawn serpent.
cover:  ## Rebuild the covers from resources/cover-source.jpg (and the favicon)
	$(PY) tools/make_cover.py

# Two EPUBs from the same Chapters/, for e-readers: -color (syntax
# highlighting in color, for backlit readers) and -eink (bolding
# instead, for grayscale screens). The site keeps one HTML page per
# chapter, so a cross-reference stays a link between files; an EPUB
# is a single document, so build_epub.py namespaces every heading id by
# chapter (ch12-immutability) before merging. Without that, the 44 chapters
# ending in `## Exercises` and the nine other repeated headings would collide
# and pandoc would quietly retarget those links. Needs pandoc, like `site`.
epub:  ## Render Chapters/ into build/epub/ThinkingInPython-{color,eink}.epub with pandoc
	$(PY) tools/build_epub.py

# One PDF from the same merged, anchor-namespaced Markdown stream the
# EPUB uses (build_pdf.py reuses build_epub.py's assembly), rendered by
# pandoc through typst. Typst draws the SVG diagrams directly and
# highlights the listings itself, so this build needs no rasterizer.
# Needs pandoc and the typst binary (`make tools-check-full` verifies).
pdf:  ## Render Chapters/ into build/pdf/ThinkingInPython.pdf with pandoc and typst
	$(PY) tools/build_pdf.py

# Publish a GitHub release whose uploaded assets are exactly the
# freshly rebuilt PDF and the two EPUBs. release.py orchestrates:
# preflight (clean tree, HEAD pushed, tag free, gh authenticated),
# then `make verify` so a book that fails the gate can never ship,
# then fresh `make pdf` + `make epub`, then
# `gh release create v$(VERSION)`. Deliberately excluded from
# verify-targets' smoke test: it tags the repo and publishes to GitHub.
release:  ## Verify, rebuild the PDF and both EPUBs, publish all three as a GitHub release (VERSION=1.0)
	$(PY) tools/release.py $(VERSION)

# --watch polls Chapters/ and rebuilds the edited chapter (one pandoc run,
# not a full site build), then the open page reloads itself.
local: site  ## Build the site, serve it with live reload, open a browser
	$(PY) tools/serve.py --open --watch

serve:  ## Serve build/site/ at http://localhost:8000 (no rebuilding)
	$(PY) tools/serve.py

# Headed "Code examples" rather than "Examples" so its slug is `code`: a
# section slug must not equal a target name (make_help.py enforces this),
# and `examples` is a target below.
##@ Code examples (build/examples/)

.PHONY: check-ch examples run output output-check test ty lint fix-imports \
        extract

# The edit loop for one chapter's listings. `gate` checks all 44 chapters and
# spends most of its time executing listings you did not touch; this runs the
# same code-example checks (markers, listing style, ty, ruff, pytest) against
# one chapter, in about a second. It is not a substitute for `gate`, which
# also catches cross-chapter breakage: run that before committing.
check-ch:  ## Run the code checks for one chapter only (CH=12), ~1s
	$(PY) tools/check_chapter.py $(CH)

# An alias for `run`, kept because older notes name it: `run` already
# depends on `extract`, so both build the same two targets in the same order.
examples: extract run  ##- Extract then run (an alias for `run`)

# These all read build/examples/, so each depends on `extract` to rebuild it
# first. make builds `extract` once per invocation, so depending on it from
# several targets does not re-extract. This is what stops a stale tree (e.g. a
# gitignored build/examples/ left over from an older Markdown) from being
# checked. Use `make reset` to force a clean regeneration.
run: extract  ## Run every extracted .py and report failures (`make examples` is an alias)
	$(PY) tools/run_examples.py

# Rewrite the #: output markers inside the Markdown's ```python listings to the
# stdout each listing actually produces. Depends on extract so each listing runs
# from build/examples/<chapter>/, where its sibling imports and data files live.
output: extract  ## Update the #: output markers in the book's listings
	$(PY) tools/validate_output.py --update Chapters

# Same, but report mismatches instead of rewriting (a gate-friendly check).
output-check: extract  ## Verify the #: output markers without rewriting
	$(PY) tools/validate_output.py Chapters

test: extract  ## Run the book's pytest examples (test_*.py)
	$(PYTEST) $(PYTEST_N) build/examples

ty: extract  ## Type-check the extracted examples (must be clean)
	$(TY) check build/examples

lint: extract  ## PEP8-lint the extracted examples with ruff (must be clean)
	$(RUFF) check build/examples

# Organize imports in the book's python listings (ruff's I rule), writing the
# result back into the Markdown. Depends on extract so ruff sees each listing's
# siblings and classifies imports the way the lint gate does.
fix-imports: extract  ## Sort imports and drop unused ones in the listings (ruff I,F401), in the Markdown
	$(PY) tools/fix_imports.py --fix

extract:  ## Write build/examples/ from the Markdown
	$(PY) tools/extract_examples.py --write

##@ Solutions (Solutions/, build/solutions/)

.PHONY: solutions-sync solutions-check solutions-prune solutions-extract \
        solutions-output solutions-output-check solutions-ty solutions-lint \
        solutions-test solutions-numbering solutions-gate

# Same idea as `sync`/`check`/`extract` above, applied to Solutions/*.md
# instead of Chapters/. Each Solutions code block is self-contained (it
# redeclares whatever book context it needs) rather than importing from
# Examples/, so this tree never breaks when a book example changes.
solutions-sync:  ## Update the committed SolutionsCode/ tree from Solutions/*.md
	$(PY) tools/extract_solutions.py --write -o SolutionsCode

solutions-check:  ## Verify Solutions/*.md matches the committed SolutionsCode/ tree
	$(PY) tools/extract_solutions.py

# The solutions counterpart of `prune`. A renumbered exercise is the
# usual source: the block moves from exercise_2 to exercise_1 and the old
# file stays, with nothing generating it and nothing importing it.
solutions-prune:  ## Delete orphaned stray files under SolutionsCode/ (see `solutions-check`)
	$(PY) tools/extract_solutions.py --prune

solutions-extract:  ## Write build/solutions/ from Solutions/*.md
	$(PY) tools/extract_solutions.py --write

# validate_output.py needs an absolute --tree: Solutions/*.md's blocks run
# with cwd inside build/solutions/<chapter>, and a relative tree argument
# stops resolving once cwd changes (the same gotcha run_examples.py's
# --tree has; see tools/README.md).
solutions-output: solutions-extract  ## Update the #: output markers in Solutions/*.md
	$(PY) tools/validate_output.py --update --tree "$(CURDIR)/build/solutions" Solutions

solutions-output-check: solutions-extract  ## Verify the #: output markers in Solutions/*.md, no rewrite
	$(PY) tools/validate_output.py --tree "$(CURDIR)/build/solutions" Solutions

solutions-ty: solutions-extract  ## Type-check build/solutions/ (must be clean)
	$(TY) check build/solutions

solutions-lint: solutions-extract  ## PEP8-lint build/solutions/ with ruff (must be clean)
	$(RUFF) check build/solutions

solutions-test: solutions-extract  ## Run Solutions' pytest examples (test_*.py)
	$(PYTEST) $(PYTEST_N) build/solutions

# The one correspondence neither tree's own checks can see: whether the
# `## N.` headings here answer the exercises the chapter asks. Pure prose
# on both sides, so extract_solutions.py (code) and heading_links.py
# (anchors) both look straight past it. Takes chapter numbers to check
# one, e.g. `make solutions-numbering ARGS=19`.
solutions-numbering:  ## Verify each chapter's exercises have matching solutions
	$(PY) tools/check_solutions.py $(ARGS)

# Mirrors `gate`, but for Solutions/: numbering, drift check, output
# markers, ty, ruff, pytest. No run_examples.py equivalent: every
# extractable Solutions block already carries a #: marker (checked by
# solutions-output above), and a block with none is a deliberately-unrun
# illustrative fragment (no `# file.py` slug), so there is nothing further
# to execute. The numbering check runs first because it is the cheapest and
# reports a missing answer, which no later step here would notice.
# extract_solutions.py also fails on an orphaned stray under SolutionsCode/;
# `make solutions-prune` deletes exactly those.
solutions-gate:  ## The Solutions gate: numbering, check, output, ty, ruff, pytest
	$(PY) tools/check_solutions.py
	$(PY) tools/extract_solutions.py
	$(PY) tools/extract_solutions.py --write
	$(PY) tools/validate_output.py --update --tree "$(CURDIR)/build/solutions" Solutions
	$(TY) check build/solutions
	$(RUFF) check build/solutions
	$(PYTEST) $(PYTEST_N) build/solutions

# Headed "Writing" rather than "Prose" for the same reason as "Code
# examples" above: `prose` is a target in this section.
##@ Writing and spelling

.PHONY: reflow reflow-check spell spell-add prose links todos claims \
        exercise-coverage

# Rewrite prose paragraphs to one sentence per line (code, tables, lists, and
# headings are left untouched; a file is rewritten only if it round-trips).
# Target one chapter with CH=, e.g. `make reflow CH=02` or `make reflow CH=Tour`.
reflow:  ## Rewrite prose to one sentence per line (CH=02 for one chapter)
	$(PY) tools/reflow_prose.py --write $(CH)

reflow-check:  ## Report which chapters would reflow, no write (CH=02 for one)
	$(PY) tools/reflow_prose.py $(CH)

# Spell-check the book and lint it for small mechanical slips. codespell
# catches known misspellings (prose and code comments); prose_lint catches
# spacing/blank-line/punctuation slips; spellcheck.py is a full-dictionary check
# of the prose, with accepted terms in tools/data/wordlist.txt. Run one chapter with
# CH= (e.g. `make spell CH=29`) or a path with DOCS=.
spell:  ## codespell + prose_lint + full-dictionary spellcheck (CH=29 for one)
	$(SPELL) $(PROSE_FILES)
	$(PY) tools/prose_lint.py $(PROSE_FILES)
	$(PY) tools/spellcheck.py $(PROSE_FILES)

# Accept every word spellcheck.py doesn't recognize into tools/data/wordlist.txt
# (sorted, deduplicated) instead of failing. It cannot tell a real term from
# a typo, so always review the diff before committing; a real typo belongs
# in the prose, not the wordlist.
spell-add:  ## Accept every spellcheck-unknown word into wordlist.txt, sorted (review the diff!)
	$(PY) tools/spellcheck.py $(PROSE_FILES) --add

# House-style lint with Vale: no em-dashes and no filler phrases. Run one
# chapter with CH= (e.g. `make prose CH=29`) or a path with DOCS=.
# Vale is a standalone binary (not uv-managed); see .vale.ini for install notes.
prose:  ## House-style lint with Vale (CH=29 for one chapter; needs vale binary)
	$(VALE) $(PROSE_FILES)

# Advisory only, and deliberately not part of `verify` or `ci`: the network
# is flaky and a dead external site should never block a build. Run it now
# and then to catch link rot; heading_links.py covers internal links.
links:  ## Check the book's external URLs for link rot (advisory, needs network)
	$(PY) tools/check_links.py

# Advisory only, like `links` above: lists `TODO(tag): ...` HTML-comment
# markers left in the Markdown (see tools/list_todos.py), each one an
# example that stays illustrative until something outside the book's
# control changes (a dependency ships a wheel, a build becomes the
# default). Never fails, and is not part of `verify`/`gate`/`ci`.
todos:  ## List TODO(tag): ... markers left in the book (advisory)
	$(PY) tools/list_todos.py

# Advisory. heading_links.py proves a cross-chapter link resolves; this
# asks the question it cannot, whether the target says what the link text
# claims. Most links either name the chapter or quote the target heading,
# and neither can drift; what is left is the handful of author-written
# phrases describing what is over there. Run one chapter with ARGS=33.
claims:  ## List cross-chapter links whose text makes an unchecked claim
	$(PY) tools/check_claims.py $(ARGS)

# Advisory. Which `##` sections no exercise practices, per chapter. A
# worklist rather than a gate: a conclusion or a table wants no exercise,
# and the matching is literal, so it under-reports coverage. Confirm a
# reported section by eye. ARGS=18 for one chapter, ARGS=--deep for ###.
exercise-coverage:  ## List chapter sections that no exercise practices
	$(PY) tools/exercise_coverage.py $(ARGS)

##@ Style gates

.PHONY: eol fix-eol listings fix-listings widths banned comment-periods \
        fix-comment-periods comment-caps fix-comment-caps comment-spacing \
        fix-comment-spacing anchors unique-slugs checks fix-checks gate-checks

# Every check here has a `fix-` counterpart, named in the check's own doc
# text and marked `##-` so the listing shows one row per rule instead of two.

# Fail if any tracked text file has CRLF in the working tree. .gitattributes
# keeps the committed blobs LF; this catches a drifted working copy. Run
# `$(PY) tools/check_line_endings.py --fix` to convert offenders.
eol:  ## Check tracked text files for CRLF; `make fix-eol` converts them
	$(PY) tools/check_line_endings.py

fix-eol:  ##- Convert any CRLF in tracked text files to LF
	$(PY) tools/check_line_endings.py --fix

# Fail if any ```python listing has more than one blank line in a row or a
# blank line between import groups. Run `make fix-listings` to remove them.
listings:  ## Check listings keep blank lines minimal; `make fix-listings` strips them
	$(PY) tools/listing_format.py

# Fail if any listing line in Chapters/ or Solutions/ is wider than 60
# characters (a trailing `# type: ignore` pragma is the one exemption).
# There is no fixer: wrap the statement, move the comment, or shorten
# the printed output.
widths:  ## Fail if a listing line exceeds the 60-character width
	$(PY) tools/listing_width.py Chapters Solutions

fix-listings:  ##- Remove the offending blank lines from listings
	$(PY) tools/listing_format.py --fix

# Fail if any phrase in tools/data/banned_phrases.txt appears anywhere in the book.
banned:  ## Fail if any tools/data/banned_phrases.txt phrase is in the book
	$(PY) tools/banned_phrases.py

# A one-line listing comment ends without a period; only multiline comments use
# periods. Run `make fix-comment-periods` to strip the offenders.
comment-periods:  ## Fail if a one-line comment ends with a period; `make fix-comment-periods` strips them
	$(PY) tools/comment_periods.py

fix-comment-periods:  ##- Remove those trailing periods
	$(PY) tools/comment_periods.py --fix

# A prose comment starts with a capital. Heuristic, so false positives are
# listed in tools/data/comment_caps_allow.txt. Run `make fix-comment-caps` to apply.
comment-caps:  ## Fail if a prose comment is not capitalized; `make fix-comment-caps` applies it
	$(PY) tools/capitalize_comments.py

fix-comment-caps:  ##- Capitalize them
	$(PY) tools/capitalize_comments.py --write

# An inline comment (code precedes it on the line) must start exactly two
# spaces after the code; a full-line comment or a #: output marker is left
# alone. Run `make fix-comment-spacing` to collapse the gap to two spaces.
comment-spacing:  ## Fail if an inline comment isn't two spaces after code; `make fix-comment-spacing` collapses the gap
	$(PY) tools/comment_spacing.py

fix-comment-spacing:  ##- Collapse inline-comment gaps to two spaces
	$(PY) tools/comment_spacing.py --fix

# Fail if a heading-anchor link (file.md#id or #id) points at no real heading.
anchors:  ## Fail if a heading-anchor link points at no real heading
	$(PY) tools/heading_links.py Chapters $(GATE_DOCS)

# Fail if two chapters give different listings the same filename. Nothing
# else catches this: the two files land in different Examples/ directories,
# so the drift check passes, while a repo search for the name returns two
# unrelated listings and a pytest run can import the wrong one. `gate` runs
# it too, so a new collision fails the build; this target is the standalone
# way to ask the same question while editing.
unique-slugs:  ## Fail if two chapters name two listings the same
	$(PY) tools/check_unique_slugs.py

# Every Markdown check at once, parsing each file once instead of per tool.
# The individual targets above still work; this is the fast whole-book answer.
# Vale (`make prose`) runs after them, so this one target answers "is the prose
# clean?" as well. Vale runs only on a bare `make checks`: with ARGS set the
# caller asked for something narrower (`ARGS=--list`, or one check by name),
# and a whole-book Vale pass is no part of that answer. Vale is a standalone
# binary rather than a uv-managed one, so this target now needs it installed;
# `make tools-check-full` reports whether it is. `gate` and `ci` do not run
# Vale, and still pass without it.
checks:  ## Run every Markdown check plus the Vale prose lint (ARGS=--list lists the checks); `make fix-checks` applies them
	$(PY) tools/check_all.py $(ARGS)
	$(if $(ARGS),,$(VALE) $(PROSE_FILES))

fix-checks:  ##- Apply every fix those checks can make
	$(PY) tools/check_all.py --fix

# The subset `gate` enforces (GATE_CHECKS above, now check_all's whole
# registry). `checks` is the one to run while editing, since it adds the Vale
# pass; this one answers the narrower "will the gate pass?" and is what `sweep`
# runs, so the sweep's verdict matches the gate's.
gate-checks:  ## Run just the Markdown checks the gate enforces
	$(PY) tools/check_all.py $(GATE_CHECKS)

##@ Cleanup

.PHONY: clean-examples clean-solutions clean-site clean-epub clean-pdf

clean-examples:  ## Remove build/examples/
	$(PY) -c "import shutil; shutil.rmtree('build/examples', ignore_errors=True)"

clean-solutions:  ## Remove build/solutions/
	$(PY) -c "import shutil; shutil.rmtree('build/solutions', ignore_errors=True)"

clean-site:  ## Remove build/site/
	$(PY) -c "import shutil; shutil.rmtree('build/site', ignore_errors=True)"

clean-epub:  ## Remove build/epub/
	$(PY) -c "import shutil; shutil.rmtree('build/epub', ignore_errors=True)"

clean-pdf:  ## Remove build/pdf/
	$(PY) -c "import shutil; shutil.rmtree('build/pdf', ignore_errors=True)"
