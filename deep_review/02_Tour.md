[[Reviewed]]
# Deep review: 02_Tour.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Say that an indented block does not create a scope

**Kind:** teaching
**Where:** section "Scripting vs. Programming" (listing `if.py`, line ~29; prose line ~60)
**Problem:** the chapter's stated audience is programmers coming from C/C++/Java, where a brace-delimited block *does* create a scope. `if.py` assigns `val` inside the `if` and the prose says only "The next line assigns to a variable named `val`." Such a reader will assume `val` dies at the dedent. Nothing in the chapter corrects that, and the listing prints nothing that would. (I already fixed the sentence that made the misconception worse: it used to say indentation "determines scoping.")

**Proposal:** extend `if.py` by two lines and add one short paragraph.

```python
# if.py

response = "yes"
if response == "yes":
    print("affirmative")
    val = 1
#: affirmative
print("continuing...")
#: continuing...
print(val)
#: 1
```

Prose to follow the existing "The subsequent statement is not indented so it is no longer part of the `if`.":

> An indented block groups statements but does not create a scope.
> `val` is assigned inside the `if` and is still visible after it,
> unlike a variable declared inside braces in C++ or Java.
> Functions, classes, and modules introduce new scopes; an `if` or a `for` block does not.

Output verified: `affirmative` / `continuing...` / `1`.

**Cost:** `Examples/02_Tour/if.py` regenerates. Exercise 1 and the other exercises do not touch `if.py`. No other chapter references it.

---

## 2. Warn that `x or default` swallows legitimate falsy values

**Kind:** teaching
**Where:** section "Booleans, None, and Truthiness" (line ~229)
**Problem:** the chapter teaches truthiness, then presents `x or default` as "a common way to supply a fallback" with no caveat. It is also one of the most common bugs the idiom produces: a legitimate `0`, `""`, or `[]` is replaced by the fallback. `truthiness.py` has already shown the reader that `0` and `""` are falsy, so the trap is fully set up and never sprung.

**Proposal:** add to the end of `truthiness.py`:

```python
count = 0
print(count or 10)  # 0 is falsy, so the fallback wins
#: 10
```

and after the existing "`x or default` is a common way to supply a fallback.":

> It has a sharp edge.
> `x or default` replaces every falsy `x`, not only a missing one,
> so a legitimate `0` or `""` is thrown away.
> When zero or an empty string is a legal value, test for `None` instead:
> `default if x is None else x`.

Output verified: `10`.

**Cost:** `truthiness.py` regenerates. Exercise 2 edits `truthiness.py`'s list of test values, which this addition leaves untouched.

---

## 3. Show that `//` and `%` do not truncate the way C and Java do

**Kind:** teaching
**Where:** section "Numbers and Arithmetic" (line ~127 and listing `numbers.py`)
**Problem:** the chapter says `//` is "floor division (divide, then round down to the nearest integer)" and shows only `7 // 2`, where Python and C agree. They disagree on negatives: `-7 // 2` is `-4` in Python and `-3` in C, and `-7 % 2` is `1` in Python and `-1` in C. A reader translating an algorithm from the language they came from gets a silently wrong answer, and the chapter's own examples cannot show it.

**Proposal:** add to `numbers.py`, right after the `7 % 2` line:

```python
print(-7 // 2, -7 % 2)  # Floors, not truncates toward zero
#: -4 1
```

and after the paragraph introducing `/` and `//`:

> Floor division rounds toward negative infinity, not toward zero,
> so `-7 // 2` is `-4` where C and Java give `-3`.
> The remainder follows from that: `-7 % 2` is `1` in Python and `-1` in C.
> The sign of `%` matches the divisor.

Output verified: `-4 1`.

**Alternative:** put the two extra prints in their own tiny listing (`floor_division.py`) rather than growing `numbers.py`, if you would rather keep `numbers.py` as the "operators you expect" listing.

**Cost:** `numbers.py` regenerates. Exercise 4 renames identifiers in `numbers.py` and is unaffected (see proposal 7, which rewrites that exercise anyway).

---

## 4. Say that iterating a `Template` skips empty literal strings

**Kind:** teaching
**Where:** section "t-Strings" (line ~339)
**Problem:** the listing prints `message.strings` as `('', ' scored ', '%')`, three strings, and then the prose says "Iterating a `Template` produces the pieces in order, each either a `str` the author typed or an `Interpolation`." Iteration yields four pieces, not five: the empty leading `''` is dropped. (Verified: `[type(p).__name__ for p in message]` is `['Interpolation', 'str', 'Interpolation', 'str']`.) A reader who takes the prose literally will write a consumer that assumes strings and interpolations alternate, which they do not.

**Proposal:** append to that paragraph:

> Iteration skips empty literal strings,
> so the leading `''` in `message.strings` never reaches the loop.
> A consumer cannot assume that literals and interpolations alternate.

**Cost:** prose only. [Composite and Interpreter](34_Composite_and_Interpreter.md#a-template-is-a-tree) builds a `Template` consumer and should not contradict this; it does not.

---

## 5. Do not use "shallow copy" 18 chapters before defining it

**Kind:** teaching
**Where:** section "Variables and References" (`references.py`, line ~92)
**Problem:** the comment reads `c = a[:]  # A shallow copy`. "Shallow" is first explained in [Rethinking Objects](20_Rethinking_Objects.md), chapter 20. Here it is a label with no content: the reader learns a word without learning that the copy duplicates the list but shares whatever the list holds. The very misconception the section exists to fix (a name is a binding, not a box) reappears one level down, and the chapter closes it off with a word the reader cannot cash in.

**Proposal:** change the comment to `# Copies the list, not its contents` and add one sentence after the listing's explanatory paragraph:

> `a[:]` copies the list but not the objects inside it,
> so a nested list would still be shared between `a` and `c`.

**Alternatives:** (a) drop the word "shallow" and say nothing more, leaving the depth question for chapter 20; (b) keep "shallow" and link forward to [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution).

**Cost:** `references.py` regenerates. Exercise 1 already asks the reader to append to `c` and explain why `a` does not change, so this sentence sharpens that exercise rather than answering it.

---

## 6. "Scripting vs. Programming" carries material its title does not name

**Kind:** structure
**Where:** section "Scripting vs. Programming" (lines 9-69)
**Problem:** three unrelated things live under one heading: an argument about scripting languages, the book's own example conventions (what `#` means, what `#:` means, where the file lives), and the first look at `if` and indentation. A reader hunting for "what does `#:` mean" a hundred pages later will not look under "Scripting vs. Programming," and the heading gives no hint that the reading conventions for every listing in the book are defined there.

**Proposal:** split at line ~41 ("The '`#`' denotes a comment..."), leaving lines 9-39 under "Scripting vs. Programming" and moving the rest under a new `## How to Read the Examples`. The `if`/indentation discussion stays with the conventions, since it explains the same listing.

**Alternatives:** (a) leave the section whole and just retitle it "Scripting, Programming, and Reading the Examples," which is worse but a one-line diff; (b) move only the two conventions paragraphs (the `#` and `#:` explanations) into chapter 1, where the book's apparatus is already described.

**Cost:** a new `##` heading adds an anchor. Nothing currently links to `#scripting-vs-programming`; check with `heading_links.py` after the change. `build_site.py` needs nothing.

---

## 7. Exercise 4 does not work as written

**Kind:** exercise
**Where:** section "Exercises" (line ~419)
**Problem:** it says "Rename every identifier in `numbers.py` to camelCase (`totalSum` instead of `total`, and so on)". `numbers.py` has exactly one identifier, `total`, so there is no "and so on"; and `total` is a single word, so `totalSum` is not its camelCase form but a different name. The reader cannot follow the instruction as given, and the naming point it aims at never lands.

**Proposal:** replace with

> 4.  `numbers.py` and `bitwise.py` each define one variable, `total` and `flags`.
>     Rename them to `totalSum` and `flagBits`, then to `TOTAL_SUM` and `FLAG_BITS`.
>     Every version runs. Using [Naming Conventions](#naming-conventions),
>     say what each form signals to a reader who did not write the code,
>     and which of the three a linter would object to.

**Cost:** none. The anchor it links to already exists and is already used by the current exercise.

---

## 8. Point forward for slicing, unpacking, and typing

**Kind:** teaching
**Where:** `references.py` (line ~92), `multiple_assignment.py` (line ~111), `string_methods.py` (line ~374), "Variables and References" (line ~78)
**Problem:** the tour uses four constructs before they are taught and never says where they are taught: `a[:]` and `s.strip()[0:5]` (slicing, [Containers](03_Containers.md#lists-and-slicing)), `first, *rest` (starred unpacking, [Containers](03_Containers.md#tuples-and-unpacking)), and dynamic typing, which the book then contradicts in practice by using type hints in every later listing ([Static Typing](08_Static_Typing.md)). Each is shown with output, so the reader can infer the behavior, but a reader who wants the rules has nowhere to go.

**Proposal:** three short pointers, using named links rather than "later" so a future split fails at `heading_links.py`:
- after "This is *dynamic typing*.": "Python also has a full static type system layered on top, which this book uses from [Static Typing](08_Static_Typing.md) onward."
- after the `multiple_assignment.py` listing: "`*rest` collects whatever is left over. [Containers](03_Containers.md#tuples-and-unpacking) covers the general form."
- in the "Common String Operations" lead-in, link "slicing" to [Containers](03_Containers.md#lists-and-slicing).

**Cost:** three cross-references into chapters 3 and 8, gated by `heading_links.py`. Both target headings exist today (`## Lists and Slicing`, `## Tuples and Unpacking`).

---

## 9. `@` means two different things and the chapter names only one

**Kind:** teaching
**Where:** section "Numbers and Arithmetic" (line ~186)
**Problem:** "Python reserves one further operator, `@` ... for matrix multiplication" is correct, but `@` is far more likely to reach the reader first as decorator syntax (`@dataclass`), which this book uses heavily. A reader who has seen a decorator anywhere will read this paragraph as a contradiction.

**Proposal:** append one clause: "The same character in front of a `def` or a `class` is unrelated: that is decorator syntax, covered in [Decorators](14_Decorators.md)."

**Cost:** one cross-reference to chapter 14.

---

## 10. "The language forces everyone to indent code the same way" overstates the case

**Kind:** prose
**Where:** section "Scripting vs. Programming" (line ~64)
**Problem:** Python enforces consistent indentation within a block, not one style across programs. Two spaces, four spaces, and tabs all compile. The claim as written is false, and a reader who has seen a two-space codebase will notice.

**Proposal:** replace "there are no options with Python formatting. The language forces everyone to indent code the same way" with

> the indentation is not a matter of taste: it is the structure.
> Python code from any two authors therefore lines up the same way

**Alternative:** keep the sentence and qualify it with "by convention, four spaces," pointing at PEP 8.

**Cost:** none.

---

## 11. "This can be useful for counting" with nothing to show

**Kind:** teaching
**Where:** section "Numbers and Arithmetic" (line ~156)
**Problem:** the chapter states that `bool` is a subtype of `int`, then says "This can be useful for counting" and stops. A reader who has not seen the idiom cannot reconstruct it from the claim, so the sentence tells them a fact is useful without letting them use it.

**Proposal:** replace the sentence with a two-line addition to `numbers.py`,

```python
scores = [90, 0, 71, 0, 55]
print(sum(s > 60 for s in scores))  # True counts as 1
#: 2
```

and prose: "Summing a sequence of comparisons therefore counts how many were true."

Output verified: `2`.

**Alternative:** cut "This can be useful for counting" and leave the subtype fact alone, letting [Comprehensions](16_Comprehensions.md) carry the idiom.

**Cost:** `numbers.py` regenerates; the generator expression arrives before comprehensions are taught, which is the reason for the alternative above.

---

## 12. `numbers.py` shadows a standard library module

**Kind:** code
**Where:** section "Numbers and Arithmetic" (line ~131)
**Problem:** `Examples/02_Tour/numbers.py` has the same name as the stdlib `numbers` module, which `decimal`, `fractions`, and `statistics` all import. Running the file directly puts its directory first on `sys.path`, so any future import chain reaching `numbers` from that directory would load the example instead. Nothing breaks today because the listing imports nothing, which is what makes it easy to break later.

**Proposal:** rename the listing to `arithmetic.py` and update the two exercise references.

**Alternative:** leave it and accept the latent hazard; it is contained as long as the listing stays import-free.

**Cost:** the file marker, `Examples/02_Tour/numbers.py` (run `make prune-examples` after the sync so the orphan is removed), and exercise 4's text. `tools/data/norun.txt` does not list it. No other chapter names it.

---

## 13. Small prose and style items

**Kind:** prose
**Where:** various

- line ~3: "syntax and the scalar types here, then containers, ... in the chapters after it." "it" points back to "This chapter" across an intervening clause. Suggest "in the chapters that follow this one" or restructure so the antecedent is adjacent.
- line ~163: `bitwise.py` opens with a full-line comment explaining binary literals. House style puts descriptions in prose, not comments; this one would read fine as the sentence before the listing.
- line ~197: "Everything else is true" holds for the built-in types but not for a class defining `__bool__` or `__len__`. A half-clause ("and any object that does not say otherwise") keeps it honest without dragging classes into chapter 2.
- line ~220: `print(name)  # default` duplicates the `#:` marker on the next line. The comment can go.
- line ~280: "It is readable, fast, and preferred" is a three-item flourish with no agent for "preferred." Suggest "It is readable and fast, and it is what modern code uses."
- line ~382: "use `snake_case` for identifiers, functions, and file names" is both redundant (functions are identifiers) and too broad (the next paragraph excepts classes, which are also identifiers). Suggest "for variables, functions, methods, and file names."
- line ~355: "You can use slicing to select portions and `in` to test membership" leads into a listing that is mostly methods and shows one slice at the end. Either lead with the methods or move the slice up.

**Cost:** none of these touch code output.

---

## Already fixed directly (no decision needed)

- line ~26: "indentation determines scoping in Python" changed to "indentation determines how statements group into blocks." Indentation determines block structure; scope in Python comes from functions, classes, modules, and comprehensions. An `if` block creates no scope, which is precisely what the listing below it demonstrates without saying so (see proposal 1).
- line ~58: "The `print()` statement sends the result to standard output" changed to "The `print()` function sends its argument to standard output." `print` has been a function since Python 3, and "the result" had no antecedent in that paragraph.

## Verified clean (no action)

- `ty check` and `ruff check` pass on `build/examples/02_Tour`; all ten listings were executed and every `#:` marker matches stdout exactly.
- `banned_phrases.py` and `heading_links.py` both pass; the cross-reference to `34_Composite_and_Interpreter.md#a-template-is-a-tree` resolves.
- Watch-list sweep found five hits (`only` x3, `never`, `exactly`), all legitimate: "only one statement per line," "never overflow," "bits set in exactly one."
- Technical claims spot-checked and correct: unlimited-precision ints, `10 ** 30` being 31 digits, `bool` as an `int` subtype, `bin(~0b1100) == '-0b1101'`, `@`/`@=` reserved for matrix multiplication and unimplemented by the built-in numeric types, `format(91.5, '.0f') == '92'`, raw-string semantics, and the `string.templatelib` API (`strings`, `interpolations`, `Interpolation.value`/`.expression`/`.format_spec`).
- "F-strings replaced them, so this book does not use them" holds: the only `%`-formatting or `str.format()` in `Chapters/` is the illustration in this chapter.
- The absence of a conclusion section matches chapters 3, 4, and 5, so it is a deliberate pattern for the tour chapters rather than an omission here.
