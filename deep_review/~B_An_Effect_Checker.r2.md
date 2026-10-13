> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: B_An_Effect_Checker (2026-10-13)

The appendix's second deep review, carrying forward `~B_An_Effect_Checker.md` and `deep_review_db.md`.
I checked each claim against the listings and against Appendix A's `tracked_greeting.py` and its three answers for untracked code,
on Python 3.15.0 and `ty` 0.0.86.
I ran `greeting_check.py`, `binding_check.py`, `third_party_stub.py`, and `check_files.py` directly; every `#:` marker matches, and the `check_files.py` self-check is unchanged before and after the edits.
I probed eight more programs against the checker to test the closing section's two lists.
`tip verify-ch CH=B ISOLATED=1` passes 21 of 21 before and after (pytest 44 tests before, 45 after); `tip prose CH=B` is clean.
No live blocks.

The main finding: a parameter of a `lambda` or nested function that shares a name with a built-in passed silently.
`lambda dir: dir.rmdir()` resolved to `builtins.dir.rmdir`, which `builtins.*` calls pure, and the prose said `assigned()` records "every other name a body binds".
None of the checker's own files holds a `lambda` or a nested function, so closing it leaves the self-check marker as it was.

## Applied directly

- `local_types.py`: `assigned()`'s or-pattern gained `| ast.arg(arg=name)`, which records every parameter of a nested function or `lambda` in the body as `UNRESOLVED`. This follows the previous review's accepted items 1 and 2 (a small tool with a shorter list of limits).
- `test_function_facts.py`: `test_a_binding_shadows_the_builtin()` gained the case `"key = lambda str: str"`; it fails without the code change and passes with it. The prose count "eight ways" is now "nine ways".
- "Facts About a Function": the list of names `assigned()` records now ends with "a parameter of a nested function or a `lambda`".
- Closing section, `Unknown` list: "A method on a record's field" is now "A method on an attribute, such as a record's field" (probed: `self.path.unlink()` gives `Unknown` too), and the binding list gained "or a parameter of a nested function or a `lambda`".
- Closing section: "Cleverness removes none of the rest, in either list" was false. Collecting calls from class bodies, decorator arguments, and defaults, reading `__new__()` and `__post_init__()`, and resolving an imported alias are all bookkeeping. Now the bookkeeping examples include "collecting the calls in a class body", and "Most of the rest, in either list, are pieces of type inference."
- "Effect Names and the Table" (teaching, near-miss): added why `lookup()` calls `fnmatchcase()` and not `fnmatch()`. `fnmatch()` follows the OS rule for file names and ignores case on Windows (probed: `fnmatch('pathlib.path.x', 'pathlib.Path.*')` is `True`, `fnmatchcase()` gives `False`). A reader adapting the table would write `fnmatch()`.
- "Effect Names and the Table": "A name that matches nothing is `UNKNOWN`" is now "A name that matches no pattern gets `UNKNOWN`."
- "The Check": "reads the Effect name from its own field" fit `Undeclared` and not `Unparsed`, which carries a message. Now "reads the fields of that kind: the Effect name of an `Undeclared`, the parse error of an `Unparsed`."
- "Effects for Code You Don't Own": "The checker's existing rule covers `requests.get`. Callers trust a declared row." was two clipped sentences that left out the consequence. Now "Callers trust a declared row, so `fetch()` draws no finding."

## Considered and declined

- **The full `check()` signature in prose** ("`check(sources: dict[str, str], table: Table = STDLIB) -> Report` receives ..."). It reads heavily, but commit 0fb66d60 put it there on purpose, replacing a paraphrase.
- **"About 450 lines."** The nine non-test listings are 477 lines with blanks and 434 without, so the round figure holds.
- **A nested function whose name shadows a built-in** (`def print(x): ...` inside a function). The call resolves to the built-in, but the nested body's calls count toward the enclosing function, so its Effects still reach the row. Not a silent limit worth a bullet.
- **"All four are what the tool requires."** The cleft is followed by a clause, which the style rule keeps.

## Verified and left as written

- Adding `hides(Console)` to `ask()` and `tell()` clears both findings (probed).
- Appendix A's `tracked_greeting.py` defines `shout()` and prints `shout []`; its three answers are "undeclared means pure", "undeclared means `Unknown`", and "declare the libraries separately".
- Calls in a class body and in a parameter's default produce no row and no finding (probed), as the second list says.
- A comprehension variable and an augmented assignment both give `Unknown` (probed).

## For the session

- `verify-ch` regenerated `Examples/B_An_Effect_Checker/local_types.py` and `test_function_facts.py` from the edited listings; they belong in the same commit.
- No NEW `exercise_refs` or `quoted_diagnostics` hits. No cross-chapter errors found.
