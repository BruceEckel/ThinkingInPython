> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: B_An_Effect_Checker (2026-09-29)

This is the appendix's first deep review.
I checked each claim against the listings, against Appendix A and the sections of chapters 04, 08, 13, 34, 42, and 44 that the appendix links, and against the pinned interpreter (3.15.0rc2).
I ran the checker on 28 small programs to test the two lists in the closing section.
`tip verify-ch CH=B_An` passes 18 of 18, `tip prose` is clean, and no `#:` marker changed, the `check_files.py` self-check included.

The main finding is the closing section's second list.
It said four limits produce no `Unknown`.
The probes found six more, and two of them are code a reader would write without thinking: `list(map(print, names))` and `p.with_suffix(".bak").write_text(text)` both read as pure.
The list now names all ten, and the one block below asks whether the listing should close the cheap ones.

## Applied directly

Corrections:

- "The Restriction": "Of the 6,442 calls" is now "roughly 6,600", and "four in five" is "nearly four in five". A recount over today's `Examples/` gives 6,615 calls in 824 files, 77.9% resolving by name. The exact figure goes stale with every listing edit and no gate watches it, so the sentence now carries a rounded one.
- "The Restriction": "With that rule the tool's reports stay true" claimed more than the rule delivers, since the closing section lists constructs that escape it. Now "every call it fails to resolve shows in a row", followed by a link to the closing section.
- "The Check": `quiet()` was "two calls away from the `print()` that `tell()` makes". The `print()` is three calls away, and its `Console` never reaches `quiet()`, because callers trust `tell()`'s declared row. The finding is `undeclared Tell`. Now "two calls away from the `tell()` whose declaration supplies the `Tell`."
- Closing section: "Four limits produce no `Unknown`" is now a bullet list of ten, each confirmed by a probe: a function passed as an argument, a method that runs without a call expression, a binding the checker does not record (and a local assigned twice), a pure pattern matching every name beneath it, calls in class bodies, decorator arguments, and defaults, and a class call that runs `__new__()`, `__post_init__()`, or an inherited `__init__()`, plus the original four.
- Closing section: "Cleverness removes none of these, because each one is a piece of type inference" was false for the original four. Finding `typing.Annotated` is name resolution and a `staticmethod` is a decorator to read. The paragraph now separates the bookkeeping limits from the ones that need types, with an operator and a call's result as the examples.
- Closing section: "They verified the architecture" is now "Here they also verify", present tense.
- "Rows to a Fixed Point": the walrus link gained its anchor, `#the-walrus-operator`.
- "Facts About a Function": "`facts_of()` records every function" is now "every top-level function". "It is never checked, because it is the program's edge" gave the design reason and left out the mechanism: the module pseudo-function declares no row, so `undeclared()` has nothing to compare. The sentence now says both.
- "From a Call to a Name": "`name()` tries those in the order Python does" did not say which order. Now "from the innermost scope outward, as Python does: variables, then the module's imports and definitions, then `builtins`."
- "Effect Names and the Table": "a typing mistake in the table" reads as a type error. Now "a misspelled Effect in the table".

Teaching:

- "Effect Names and the Table": `fnmatch` had no gloss. Added that `*` matches any run of characters, dots included. The dots matter: they are why `pathlib.Path.*` covers `pathlib.Path.read_text`, and why a pure pattern covers more than it should.
- "Facts About a Function": the `ask()` motivation now comes before `effect_marks.py`. The listing had opened the section with `Hides` before the reader knew what hiding was for.
- "Facts About a Function": `calls_in()` computes the third fact and no sentence described it. Added a paragraph: what `ast.walk()` yields, and that calls inside a nested function or a `lambda` count toward the enclosing function (probed).
- "Rows to a Fixed Point": the heading's term was never defined. Added "Rows that the rule leaves unchanged are a *fixed point* of the rule."
- "Rows to a Fixed Point": no sentence connected `UNRESOLVED` (a name) to `UNKNOWN` (a row). Added that an unresolved call has the name `"?"`, which matches no pattern, so `lookup()` answers `UNKNOWN`.
- "Rows to a Fixed Point": "The tests build `Facts` by hand" and the clause two lines later said the same thing. Merged.
- "The Check": the section opened on a listing. Added a lead-in that defines a *finding*.
- "The Check": added "The demo prints each row that is not empty, then each finding", which explains why `quiet`, the classes, and the module are absent from the first block of output.

House style:

- Six constants gained the typed `Final` form: `SOURCE`, `GREETING`, `HEAD`, `APP`, `STUB` (`Final[str]`) and `FILES` (`Final[list[str]]`). The checker's own `UNRESOLVED`, `LITERALS`, `PURE`, `UNKNOWN`, and `STDLIB` already had it.

## Close the cheap silent limits in the listing?

The closing section now lists ten constructs the checker passes without an `Unknown`.
Three of them cost a few lines each to close, and closing them would make the appendix's opening claim ("the checker treats no unresolved call as pure") hold for code a reader is likely to write.

1. **Bindings.** A third case in `assigned()`'s `match`, `case ast.Name(id=name, ctx=ast.Store())`, with `types.setdefault(name, UNRESOLVED)`, records every loop variable, `with` target, walrus target, and tuple target. `ast.walk()` visits an `Assign` before its target, so the existing cases still win. Pattern captures are `ast.MatchAs` and `ast.MatchStar` nodes and need one more case.
2. **A local assigned twice.** `assigned()` uses `setdefault()`, so `p = "text"` followed by `p = Path("x")` leaves `p` a `str`, and `p.read_text()` reads as pure. Recording `UNRESOLVED` when a second assignment disagrees with the first closes it.
3. **Call results under a pure pattern.** `type_of()` gives a call's result the callee's name as its type. That is right for a class call and wrong for every other call. `p.with_suffix(".bak").write_text(text)` becomes `pathlib.Path.with_suffix.write_text`, and `with_*` calls it pure. The same happens for a receiver annotated `Any` (`typing.*`) or `type[Shape]` (`builtins.*`). The smallest fix I found is in `callee()`: answer `UNRESOLVED` when the receiver's type came from a call whose callee is not a class the scope knows. That needs `Scope` to tell classes from functions, which `defined` does not do today.

I recommend 1 and 2. They are small, they fit the appendix's rule, and they shorten the second list by one bullet.
I would leave 3 as a documented limit, since the fix adds a field to `Scope` and the appendix is near the length it states ("about 450 lines"; the eight non-test listings total 449).

I did not make the change myself for two reasons.
It alters what the checker reports, and the `check_files.py` marker is the appendix's central evidence, so a change there deserves your eye.
It is also a choice about what the appendix is: a small tool with an honest list of limits, or a slightly larger tool with a shorter list.

`[] Reject`

## Considered and declined

- **Splitting `function_facts.py`.** At 155 lines and eleven functions it breaks "one new thing per listing". The functions build on each other in order, the test file covers them as one unit, and a split would need three or four new listing names that the self-check's `FILES` list and the "four changes" paragraph would have to follow. The prose after the listing walks the functions in order, which does the job.
- **`effect_table.py`'s one-name-per-line import.** The packed form would save seven lines but needs an `I001` entry in `pyproject.toml`. Appendix A's `effect_variable.py` uses the vertical form too, as do chapters 17, 19, 31, 33, 37, and 47.
- **The `TypeIs` link.** `08_Foundations--Static_Types.md#type-narrowing` lands on the summary table, which is the one place chapter 08 mentions `TypeIs`. The link is accurate. Whether chapter 08 should teach `TypeIs` in a section is a question for that chapter.
- **"Concludes that solving them all means rebuilding a type checker."** Appendix A says the tool "belongs inside the type checker" and that one outside must "repeat the checker's inference". The opening's paraphrase is fair.
- **"The checker confirms that its core is pure."** With ten silent limits the verb looks strong. I read the five core listings for each silent construct (a function passed as an argument, an operator on a class of the book's own, a property, a `with`, a shadowing binding, a reassigned local, a method on a call's result) and found none, so the claim holds for this code.
- **"Each change is small, and two of them improved the code."** A judgment, and yours to make.
- **Removing `"typing.*": PURE` from the table.** It is what makes a receiver annotated `Any` read as pure. No listing or test needs the entry. It belongs to the block above, item 3.

## Verified and left as written

- `print` has no `__annotations__` and no `__dict__`, and the assignment raises an `AttributeError`.
- `os.remove.__module__` is `nt`, `open.__module__` is `_io`, `random.random.__module__` is `None`, and its `__qualname__` is `Random.random`.
- Appendix A lists five problems and three answers for untracked code, its rule's third line reads "the Effects f handles", `row(shout)` prints `[]`, and `row()` skips metadata that is not a `Performs`.
- Every limit in the `Unknown` list produces `Unknown` (probed: a parameter call, a call of a call's result, a loop variable, a union, an inherited method, a tuple target).
- Chapter 44 says "pushing the Effects to the edges" in the linked section, and chapter 34's "Interpreter" section names `ast.NodeVisitor` and *Visitor*.
- Only `Ok.bind()` in `utils/result.py` calls its argument; `Err.bind()` returns `self`.
- I did not repeat the 2026-09-18 check of the "four changes" paragraph, which restored each old form in turn.
