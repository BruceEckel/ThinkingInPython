> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 05_Foundations--Functions (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the sections the chapter links (chapters 2, 8, 14, 15, 17, 40, 44), the pinned interpreter (3.15.0rc2), and `ty` 0.0.84.
Verified and left as written: both quoted `SyntaxError` messages, `sentinel("MISSING") is sentinel("MISSING")` being `False`, `dict.get(key, default=None, /)`, the `<lambda>` name in a traceback, `operator.itemgetter(-1)` giving the same order as the lambda, and the override claim (`ty` accepts a renamed positional-only parameter in a subclass and reports `invalid-method-override` for the same rename without the `/`).
`tip verify-ch CH=05` passes 24 of 24.

## Applied directly

Chapter, corrections:

- Opening: the fix-triage cut of "This chapter covers defining and calling functions:" left the rest of that sentence behind as a fragment ("default and keyword arguments, scope and `global`, ... and lambdas."). Deleted the fragment, which completes the cut.
- "Names Inside a Function": the sentence said the Closures section and Effect Management "both treat a mutable global as an anti-pattern." Neither uses the word, and chapter 40's treatment of a rebinding global is in Pure Functions (`withdraw()`), not Closures. The links now say what each section does: Pure Functions shows that one call depends on every call before it, and Effect Management classifies the write as a side effect and the read as a side cause.
- "Positional-Only and Keyword-Only Parameters": "a parameter a caller must pass by position stays outside [the contract]" contradicted the section's own closing paragraph, where the name stays outside and the parameter is still required. The sentence now speaks of the parameter's name.
- "Unpacking Arguments": `*` "unpacks a sequence" is now "any iterable". A set, a string, and a generator all unpack (probed), and chapter 3 uses the word.

Chapter, teaching:

- `expect()` had no explanation at its first use in the book, which is `add.py` in this chapter; chapters 2 through 4 use `try`/`except`, and chapter 15 defines the helper. Added three lines after `add.py`, with the link on the term, and one sentence in "Unpacking Arguments" noting that `expect()` has the shape of `trace()`.
- `add.py` moved up to follow "type errors surface at runtime rather than at compile time:", the claim it demonstrates. After the cut of its lead-in it followed the tuple-return aside with nothing connecting them. The return-value material (different types, `None`, tuples) now runs together after it. Alternative considered: restoring a lead-in, which you had cut.
- After `a_function.py`: two sentences defining *parameter* and *argument*. The chapter depends on the difference (the two `SyntaxError` messages each use one of the words) and no earlier chapter defines them.
- `param_markers.py`: the `try`/`except` with two `partition()` calls is now `expect(TypeError, divide, a=10, b=2)`, which prints the whole message on two marker lines. The two prose sentences explaining the trimming are gone. `ty` reports the misuse through `expect()`, so the `# type: ignore` is still used. This also matches Solutions exercise 7, which quotes the full message.
- Exercise 2 replaced. The old one added `"volume2": None` to `prefs` and called `get()` on it, which `sentinel_default.py` already does with `"mute": None`. The new one makes `get()` re-raise, as the listing's comment says a real one would, and asks why `None` could not be the sentinel.
- Exercise 9 added (rebinding a parameter against mutating it). `mutating_arguments.py` had no exercise. Added at the end, so no existing number moves.

Chapter, prose:

- "With the [type hints]" is "With [type hints]".
- "`rebinds()` never touches" is "leaves ... alone".
- The forwarding-collision lead-in dropped "still" and "already" and names the positional argument as the second source.
- "so `trace()`, which knows nothing about the signature of the function it calls, has no way to see the clash coming" held its subject open across a clause. Now two sentences, cause first.
- "already computes the key, pass the function itself" is "computes the key, pass that function".
- "just reads" is "reads"; `operator.itemgetter`/`attrgetter` carry their parentheses and the module name on both.
- Exercise 1: `bad_append`'s is `bad_append()`'s.

Solutions:

- Exercise 1: the listing now runs the tuple version (`tuple_append()`) and shows the `AttributeError`, since the exercise asks for that change. The second paragraph said "the bug is not really about mutability by itself", which is not so: the tuple version fails for a different reason. Rewritten to say the change trades one failure for another, and that an immutable default suits a parameter the function reads.
- Exercise 2: new listing and prose for the new exercise, with `getattr()` as the built-in that behaves the same way (probed).
- Exercise 4: title said "running total"; the flag prints one sum. Now "an optional total".
- Exercise 7: "Take the `**facts` away and Python reports" is "Without `**facts`, Python reports". The closing paragraph gained the second reason to pair `/` with `**facts`: `describe("Bob", name="Robert")` works, and fails without the `/`.
- Exercise 9: new.
- Watch-list words: "lands" (twice), "ever runs", "already" (twice), "never" (twice), "here just".

## Considered and declined

- "The default looks like an expression each call evaluates, but Python evaluates it once, at the `def`" restates the subsection's first sentence. Kept: it names the misconception a C++ reader arrives with, where a default is evaluated on each call.
- "`**` unpacks a dictionary" is narrower than the truth (any mapping). Left: no mapping other than `dict` has appeared by this chapter.
- The closing paragraph of "Positional-Only and Keyword-Only Parameters" mentions a subclass overriding a method, two chapters before classes. Left: the book's reader knows the terms from another language, and the claim holds under `ty`.
- The `minmax()` fragment is indented, not a tested listing. Left: three lines, no output to check.
- `square = lambda n: n * n` draws ruff's E731 in most projects. The listing's comment and the following paragraph already say to prefer `def`, and the gate's ruff configuration accepts it.
