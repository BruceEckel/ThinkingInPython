> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: A_Effect_Tracking (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the sections it links in chapters 44, 46, and 47, Appendix B's opening, the installed Stateless source (`need.py`, `handler.py`), and `ty` 0.0.84.
The claims about other systems were checked on the web: Koka's `map()` signature, OCaml 5's untyped handlers, and the absence of a plugin interface in `ty`.
`tip verify-ch CH=A_Effect` passes 18 of 18, `check_self_reference` is clean, and `tip prose` reports nothing.

## Applied directly

Corrections:

- "Why a Native System Tracks Best", opening: "each later section finds one of them missing" did not match the appendix. Four properties map to the first four of the five problems in "What a Checker for the Row Must Do", in the same order; "Find a Place to Run" and "Tracking Is Not Management" map to none. The sentence now says that.
- Same section, "The compiler infers the row": "when a `Log` Effect appears three levels down" miscounted. In `bookkeeping_scales.py` the chain is `main()`, `menu()`, `session()`, `greet()`, then the new helper, so the helper sits four calls below `main()`. Now "when a helper four calls below `main()` needs a `Log` Effect."
- "The Tracking Problem": "follow this rule because they implement algebraic effects" made the row a consequence of the handlers. Chapter 44 says OCaml 5 has the handlers and tracks nothing. Now "compute this rule as part of algebraic effects", and the two-halves sentence adds that a language can have one half without the other, with OCaml 5 as the case. That is also the appendix's premise: the row half alone.
- "Handling subtracts": "`main()` handles `ask` and `tell`, so its row is `<console,exn>`" skipped a step, since handling explains what is absent from the row and the handler bodies explain what is present. Now "so neither appears in its row, `<console,exn>`."
- "The Tracking Problem", first link: the text read "Effect Management Systems" and the anchor is that section's subsection, "Tracking and Management". The text now names the heading the link opens.

Teaching:

- After the `shout()` paragraph: added the lookalike pair. `row()` returns an empty list for a function that declares `performs()` with no arguments and for one that declares nothing. Appendix B uses the first form to declare a function pure, and the appendix had not said the list cannot tell the two apart. The new paragraph points to "Decide What Untracked Code Performs".
- "Subtract What a Handler Discharges": `Scripted` appeared in the `handling()` fragment with no introduction. One sentence now says it is the stand-in from `ask_tell.py`.
- "Resolve Every Call": "Of the three checkers" assumed the reader recalls chapter 08's list. Now "Of the three checkers this book names".

Tense:

- "a place [Resolve Every Call] ruled out" is now "rules out", and "[The Tracking Problem] divided" is now "divides".

## Verified and left as written

- `reveal_type(ask)` reports `def ask(prompt: str) -> str`, and `reveal_type(twice(hello))` reports `Generator[Need[Console], Any, None]`, both on `ty` 0.0.84.
- A `hello_twice()` annotated `Success[None]` draws `invalid-yield` on its `yield from`.
- `supply(Console())` reveals `Handler[Need[Console]]`, and applying it to `hello` reveals `() -> Generator[Never, Any, None]`, so the `Handler`'s type does the subtracting.
- `Annotated[int]` raises a `TypeError`, `get_type_hints()` strips the metadata without `include_extras=True`, and `__metadata__` holds the tuple.
- Koka's documentation gives `map()` as `fun map( xs : list<a>, ^f : (a) -> e b ) : e list<b>`. The appendix drops the borrow marker `^` and the optional parentheses, which leaves the same type.
- `ty` has no plugin interface and Astral states no plan for one. Pyright has none by design.

## Considered and declined

- **A runtime checker listing.** "Find a Place to Run" describes the decorator and `ContextVar` design in prose alone. A listing would show `shout()` caught at the call. Declined: you asked for an analysis with no implementation in this appendix, and Appendix B is where the building happens.
- **Packed parentheses for `effect_variable.py`'s import.** The `from stateless import (...)` block runs one name per line, eight lines, where `catch_score.py` in chapter 46 packs the same kind of import into two. Converting needs a per-file `I001` entry in `pyproject.toml`, which other branches of this sweep also edit. Chapter 47 has two imports in the same form, so the three are better changed together.
- **"As you read down the table, the work moves from you to the compiler."** Four of the five rows say "You" in the computing column, so the movement is in the checking column until the last row. The sentence reads as a fair summary of the table as a whole.
- **`get_type_hints()` named before `include_extras=True`.** The paragraph before `effect_rows.py` says the runtime reads metadata back with `get_type_hints()`, and the default call strips it. The paragraph after the listing says so, two sentences after the reader meets the argument.
- **An "Appendices" divider.** `build_site.PARTS` still has no entry for the appendices. That is a build decision outside this file.
