---
name: rename-chapter
description: >-
  Checklist for renumbering, renaming, or splitting a chapter or appendix: every file, data list, pyproject entry, and prose reference that must change, and the filename characters the link regexes allow. Use before moving, renaming, or splitting any chapter.
---

# Renumbering, renaming, or splitting a chapter

Moved from `CLAUDE.md`'s Traps. The filename convention itself (`NN_<Part>--<Chapter_Name>.md`) stays there.

- **Renumbering or renaming a chapter** touches, in all four trees
  (`Chapters/`, `Solutions/`, `Examples/`, `SolutionsCode/`): the filenames, every
  `NN_*.md` cross-reference and its link text, `build_site.py` `PARTS`,
  `tools/data/norun.txt`, `tools/data/timing.txt` (since 2026-09-18 the
  gate's `skip-lists` step, `tools/check_skip_lists.py`, fails on a
  pattern in either that matches no file under `Examples/` or
  `SolutionsCode/`, so a missed one is loud; renaming one *listing*
  trips it the same way),
  `tools/data/record_exceptions.txt` and
  `tools/data/exercise_refs_baseline.txt` (both keyed by chapter name,
  so a rename only; after one, `make exercise-refs` shows each pair as
  GONE plus NEW, and `make exercise-refs-accept` settles it), the
  `README.md` tracking table,
  `deep_review_db.md`/`readability_db.md`/`bruce_edit_db.md`, and any
  `tools/tests/` fixture naming a chapter. Appendices use letter prefixes
  (`A_...`); build_site labels them "Appendix X".
  The ones that hide, both in `pyproject.toml`: **`per-file-ignores` keys a few
  entries by chapter directory** (`"**/46_Effects--Stateless/exercise_8.py"`), so
  a rename silently drops the waiver and the listing fails `I001` at
  `solutions-gate`, several steps after the rename looked done; and
  **`[tool.ty.environment] extra-paths` names one**
  (`build/examples/06_Foundations--Modules_and_Packages`), where a stale entry
  makes `ty` refuse to start with "does not point to a directory". Grep
  `pyproject.toml` for the old directory name before running `verify`.
  Renaming the *chapter title* additionally means the H1, the Solutions H1
  (`<Title>: Solutions`), and every link whose text was the old title.
- **Splitting a chapter silently invalidates every relative cross-reference in
  the later half.** Nothing greps for prose, so no gate catches this. Splitting
  Generators out of Stateless left chapter 46 with fourteen phrases
  ("the previous chapter", "the previous chapter's second exercise",
  "the previous section") that still meant 44, not the newly-inserted 45.
  After any split, `grep -n "previous chapter\|previous section\|last chapter"`
  the later half and check each hit against the content it names, since some
  will legitimately point at the new neighbor. Prefer a named link
  (`[Effect Management](44_Effects--Effect_Management.md#anchor)`) over a relative
  phrase, so the next split fails loudly at `heading_links.py` instead of
  quietly misleading a reader. Where three references cluster in one section,
  resolve the later ones with "that chapter" against a nearby link rather than
  repeating the same hyperlink.
- **Filename characters.**
  **A regex that matches chapter filenames must allow `-`.** `check_solutions.py`'s
  `BARE_CHAPTER_LINK` was `\d{2}_[A-Za-z_]+\.md` and stopped matching every chapter
  the moment the `--` landed, so the check reported nothing instead of failing.
  Its own unit test caught that one. Grep `re.compile` for `\.md` before adding a
  character to a filename.
  Only `[\w./-]` is safe in a filename, because that is the character class in
  all three link regexes (`build_site.MD_LINK`, `build_epub.ANCHOR_TARGET`,
  `heading_links.ANCHOR_TARGET`). A character outside it fails *silently*, which
  is why brackets were tried and rejected: with `43_[Functional]_Confidence.md`,
  `heading_links` reported "Anchor links OK" for a link to a nonexistent anchor,
  and `build_site` emitted un-rewritten `.md` hrefs (404s on the site). No gate
  went red. Also avoid `[`/`]` because `norun.txt` and `timing.txt` patterns are
  `fnmatch` globs, where brackets are a character class.
