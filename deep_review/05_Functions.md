# Deep review: 05_Functions.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

Every listing in the chapter runs clean as it stands: `ruff check`, `ty check`, and each script's stdout matches its `#:` markers. Every cross-reference resolves (`08_Static_Typing.md#type-hints`, and the three anchors other chapters aim at this one: `#default-and-keyword-arguments`, `#positional-only-and-keyword-only-parameters`, `#lambdas`). No banned phrases, no em-dashes. `sentinel` as a 3.15 builtin is confirmed both against the pinned interpreter and against PEP 661's acceptance (Steering Council, April 2026). So everything below is a teaching or wording judgment, not a correction.

Every output marker quoted below was produced by running the proposed code under `uv run python`, and every proposed line fits the 70-column limit.

---

## 1. Say that a `*args` parameter makes every later parameter keyword-only

**Kind:** teaching
**Where:** section "Positional-Only and Keyword-Only Parameters" (line ~232), with exercise 4 depending on it (line ~299)

**Problem:** The chapter teaches `*args` in one section and the bare `*` marker in another, and never says they do the same thing to whatever follows them. Exercise 4 then asks the reader to add a keyword-only `total` flag to `report(label, *values, **options)`, which requires knowing that a parameter written after `*values` is automatically keyword-only. The solution file says so ("`total` sits between `*values` and `**options`, which makes it keyword-only"), but the chapter never does, so the exercise is not answerable from the chapter. A reader who has not met the rule will write `def report(label, *values, total=False)` and then wonder why `report("nums", 1, 2, True)` does not set the flag.

**Proposal:** After "A `*` begins the *keyword-only* parameters. You must pass every parameter after it by name." (line ~233), add:

```
A `*args` parameter does the same thing.
It absorbs every remaining positional argument,
so a parameter declared after it can only be passed by name.
```

Then add a second listing to `param_markers.py`, after `make_user()`:

```python
def tally(label, *values, total=False):
    print(label, values, total)

tally("nums", 1, 2, True)
#: nums (1, 2, True) False
tally("nums", 1, 2, total=True)
#: nums (1, 2) True
```

with prose after the block:

```
The `True` in the first call joins `values` like any other positional argument.
Only the named form reaches `total`.
```

While here, the "Variable Argument Lists" section could gain one sentence, since nothing in the chapter says the names are not fixed: "The names `args` and `kwargs` are convention; the `*` and `**` do the collecting, so `*values` and `**options` behave identically."

**Cost:** `tally()` is deliberately not named `report()` so that exercise 4 keeps its point. Adds a listing to `param_markers.py`, which exercise 3 also edits; the exercise says "add a parameter to `divide()`", so the extra function does not collide.

---

## 2. Show that a function with no `return` returns `None`

**Kind:** teaching
**Where:** section opener, `flexible_args_and_returns.py` (line ~35)

**Problem:** The chapter never states that every function returns a value and that falling off the end produces `None`. Its second listing sets the question up perfectly and then walks past it: `flexible_args_and_returns()` has two `if`s and no `else`, so any other argument returns `None` silently. This is one of the most common early Python surprises (a reader assigns the result of a `list.sort()` or of their own `print`-only function and gets `None`), and the chapter's own code is one call away from demonstrating it.

**Proposal:** Add a third call to the listing:

```python
print(flexible_args_and_returns(2))
#: None
```

and after the block:

```
The third call matches neither test,
so the function reaches its end without returning anything and produces `None`.
Every Python function returns a value.
A bare `return` and a missing `return` both produce `None`.
```

**Cost:** none. Verified output.

---

## 3. `report()` does not demonstrate the forwarding claim

**Kind:** prose | code
**Where:** section "Unpacking Arguments" (line ~222)

**Problem:** The closing prose reads "a function can gather arguments with `*args` and `**kwargs`, then pass them on unchanged, as seen in `report()`. This is the standard way to write a wrapper around another function." But `report()` gathers and prints. Nothing in the chapter passes collected arguments on to another function, so the reader is pointed at a demonstration that is not there and does not see the shape the sentence is describing.

**Proposal:** Add the forwarding case to `unpacking.py`, after the existing `report()` call:

```python
def trace(func, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

trace(report, "point", *nums, **opts)
#: calling report
#: point (1, 2, 3) {'color': 'red', 'size': 10}
```

and replace the closing paragraph with:

```
Because collecting and unpacking are inverses,
a function can gather arguments it knows nothing about and pass them on unchanged.
`trace()` accepts any call and forwards it,
which is the standard shape of a wrapper.
[Decorators](14_Decorators.md) builds on this.
```

Alternative, if the chapter should stay short here: keep the prose and delete only "as seen in `report()`", so the sentence describes the technique without claiming to have shown it.

**Cost:** `unpacking.py` grows by five lines and now teaches three things (unpack, collect, forward). If that is too much for one listing, split `trace()` into its own file. The `[Decorators](14_Decorators.md)` link is new; the anchor is the chapter file, so nothing can go stale.

---

## 4. Name the general rule behind the mutable-default trap

**Kind:** teaching
**Where:** section "Default and Keyword Arguments" (line ~112)

**Problem:** The chapter explains the shared default as a property of default values, which is half the story. The other half is that a parameter is a name bound to the caller's object, so mutating a mutable argument is visible outside the function. [Variables and References](02_Tour.md#variables-and-references) taught the binding, but the chapter never connects it, and a reader can leave believing that mutable defaults are a quirk of `def` rather than a case of aliasing they will meet again with any list they pass in.

**Proposal:** After "This behavior commonly confuses newcomers to the language." (line ~113), add:

```
Underneath, a parameter is another name bound to the caller's object,
the binding described in [Variables and References](02_Tour.md#variables-and-references).
When that object is mutable, changes made inside the function are visible outside it.
`bad_append()` combines this with a default built once,
so each call mutates the object the next call will use.
```

**Cost:** none. Adds a back-link that `heading_links.py` will gate.

---

## 5. State the parameter-ordering rule

**Kind:** teaching
**Where:** section "Default and Keyword Arguments", after `default_args.py` (line ~84)

**Problem:** The first thing a reader does after learning defaults is write one in the wrong position, and Python rejects it at compile time with a message they have not been prepared for. The chapter shows only well-formed parameter lists, so nothing tells them the ordering is constrained at all.

**Proposal:** After the `default_args.py` block, add:

```
A parameter with a default cannot come before one without.
`def f(a=1, b):` is a `SyntaxError`:
`parameter without a default follows parameter with a default`.
Keyword-only parameters are exempt, because the caller names them.
```

The last sentence forward-references "Positional-Only and Keyword-Only Parameters"; drop it if the forward reference is unwelcome this early.

**Cost:** none. Message text verified on the pinned interpreter.

---

## 6. The lambda in `lambdas.py` is the one case where a lambda is unnecessary

**Kind:** code | teaching
**Where:** section "Lambdas" (line ~276)

**Problem:** `sorted(words, key=lambda w: len(w))` wraps a builtin that could be passed directly: `key=len` produces the same result. The chapter's one motivating example for lambdas is the textbook case for *not* writing one, which teaches the reader a habit the rest of the book would flag in review. The section also never says what `key` does, so a reader meeting `sorted()` for the first time here (its first appearance in the book is this line) sees a sorted list without knowing the function was called once per element.

**Proposal:** Replace the `sorted()` line with two:

```python
print(sorted(words, key=len))
#: ['fig', 'kiwi', 'apple', 'banana']
print(sorted(words, key=lambda w: w[-1]))
#: ['banana', 'apple', 'fig', 'kiwi']
```

and open the section's prose with the mechanism:

```
`sorted()` calls `key` on each element and orders by the results.
When a function already computes the key, pass it by name: `key=len` needs no lambda.
Write a lambda when nothing existing computes what you want,
such as ordering by a word's last letter.
```

**Cost:** the `# Sort by length` comment goes away with the line it annotates. `lambdas.py` keeps its `E731` per-file ignore, which the `square = lambda ...` line still needs. Both outputs verified.

---

## 7. Show the mechanism of the shared default, not only its effect

**Kind:** teaching
**Where:** `mutable_default.py` (line ~98)

**Problem:** The prose says the default "lives on the function object," which is the mechanism, but the listing shows only the surprising output. A reader cannot see the claim; they take it on faith. One line makes the storage visible and makes the sentence checkable.

**Proposal:** After `print(bad_append(2))` and its marker, add:

```python
print(bad_append.__defaults__)
#: ([1, 2],)
```

and adjust the following prose to point at it: "`__defaults__` holds the tuple of default values stored on the function object, and it is the same list both calls appended to."

**Cost:** introduces a dunder attribute early. If function attributes are meant to wait for [Function Objects](28_Function_Objects.md), reject this and leave the claim in prose. Output verified.

---

## 8. Demonstrate the two call errors instead of asserting them

**Kind:** teaching
**Where:** section "Positional-Only and Keyword-Only Parameters" (line ~255)

**Problem:** "Calling `divide(a=10, b=2)` is an error" and "Calling `make_user("Sue", True)` is an error" are stated but never shown. These are the errors the reader will actually hit, and the messages are the only clue they will get at the time. The positional-only message in particular ("got some positional-only arguments passed as keyword arguments") is unlike any other `TypeError` and worth recognizing on sight.

**Proposal:** Append to `param_markers.py`:

```python
try:
    divide(a=10, b=2)
except TypeError as e:
    print(type(e).__name__)
#: TypeError
try:
    make_user("Sue", True)
except TypeError as e:
    print(e)
#: make_user() takes 1 positional argument but 2 were given
```

and quote the first message in prose, since it does not fit in 70 columns as a marker: "The first reports `got some positional-only arguments passed as keyword arguments: 'a, b'`."

Alternative: print `type(e).__name__` for both and put both messages in prose, which is more symmetric but shows the reader less.

**Cost:** `try`/`except` is taught in [Control Flow](04_Control_Flow.md#errors-and-exceptions), so nothing is used before it is taught. Both outputs verified.

---

## 9. Drop the type annotations from exercises 3 and 4

**Kind:** exercise
**Where:** exercises 3 and 4 (lines ~295, ~299)

**Problem:** The chapter opens by saying signatures here carry no types and that [Static Typing](08_Static_Typing.md#type-hints) covers them three chapters later, and every listing honors that. The exercises then ask for `label: str = "result"` and `total: bool = False`. Both solutions write the parameters without annotations, so the exercises ask for something the chapter has not taught and the answers do not use. Exercise 3 also says the call "prints `"half: 5.0"`" when the solution returns the string and the caller prints it; a reader following the wording literally will make `divide()` print and return `None`.

**Proposal:** Write `label="result"` and `total=False` in the exercise text, and reword exercise 3's outcome as "so `print(divide(10, 2, label="half"))` shows `half: 5.0`".

**Cost:** none in `Solutions/`, which already matches the proposed wording.

---

## 10. Define "sentinel" where the word first appears

**Kind:** prose
**Where:** line ~115

**Problem:** "You only need the `None` sentinel when the function modifies the argument" is the first use of the word, and it goes undefined until line ~141, twenty-five lines and two listings later. In between the reader has to carry a term whose meaning they are guessing at.

**Proposal:** Change line ~115 to introduce it: "The `None` default in `good_append()` is a *sentinel*: a value chosen to mean "nothing was supplied" rather than to be used. You need one when the function modifies the argument."

The italics follow the chapter's own convention for a term at first use (`*positional-only*`, `*keyword-only*`).

**Cost:** two other chapters link to this section for the word "sentinel" ([Context Managers](15_Context_Managers.md) and [Iterators](23_Iterators.md)); defining it earlier in the same section only makes those links land better, and the section heading they aim at does not change.

---

## 11. `dict.get()`'s second parameter has a default

**Kind:** prose
**Where:** line ~261

**Problem:** The text writes the signature as `dict.get(key, default, /)`. The real signature is `dict.get(key, default=None, /)`, and the omission makes `default` look required in a method the reader almost always calls with one argument.

**Proposal:** Write `dict.get(key, default=None, /)`.

**Cost:** none.

---

## 12. Demonstrate the "only constraint" claim

**Kind:** teaching
**Where:** line ~63, after `add.py`

**Problem:** "The only constraint on a function argument is that the function can apply its operations to that object" is the chapter's sharpest sentence about dynamic typing, and it closes the section with no evidence. The reader has just seen `add()` succeed on two argument types and is given no picture of what failure looks like or when it arrives.

**Proposal:** Add to `add.py`:

```python
try:
    add(42, "spam")
except TypeError as e:
    print(e)
#: unsupported operand type(s) for +: 'int' and 'str'
```

and follow the existing sentence with:

```
The failure comes from `+`, inside the call, not from the call itself.
Nothing checks the arguments on the way in.
```

**Cost:** puts a `try`/`except` in the chapter's third listing. If that is too early, keep the listing as it is and add only the prose sentence. Output verified.

---

## 13. Header comments in `param_markers.py` repeat the prose above them

**Kind:** code
**Where:** `param_markers.py` (lines ~237-238)

**Problem:** The two comment lines under the file marker restate, nearly word for word, the two sentences printed immediately above the block. A reader reads the same rule twice in six lines, and the listing carries description that the book's convention puts in prose.

**Proposal:** Delete both comment lines, leaving `# param_markers.py` alone as the first line.

**Cost:** none.

---

## 14. The exercises miss two of the chapter's six sections

**Kind:** exercise
**Where:** section "Exercises" (line ~286)

**Problem:** The four exercises cover mutable defaults, sentinels, and the two parameter markers. Nothing exercises call-site unpacking or lambdas, which are two of the chapter's six sections, and unpacking is the one the reader is most likely to use the same day.

**Proposal:** Add two exercises:

```
5.  Write `apply_twice(func, value)` that returns `func(func(value))`,
    then call it with a lambda that appends `"!"` to a string.
    Predict the result of `apply_twice(lambda s: s + "!", "hi")` before running it.
6.  Given `args = ("point", 3, 4)` and `opts = {"color": "red"}`,
    call `report()` from `var_args.py` so it prints
    `point (3, 4) {'color': 'red'}`,
    passing both containers without naming their contents.
```

**Cost:** `Solutions/05_Functions.md` needs two new sections, which is outside this review's edit scope. Reject unless you want to write them, or accept and let the solutions follow in a separate pass.

---

## 15. The quoting around `+` at line ~49

**Kind:** prose
**Where:** line ~49

**Problem:** "the same function applies the '`+`' operator" wraps a code span in single quotes, a form used nowhere else in the chapter and rare elsewhere in the book. It reads as a typo.

**Proposal:** Write "applies the `+` operator".

**Cost:** none.

---

## Already fixed directly (no decision needed)

None. Nothing in the chapter met the bar for a direct edit: no listing fails, no `#:` marker disagrees with real stdout, no technical claim is wrong or version-stale, no cross-reference or relative phrase points at the wrong target, and no banned phrase appears.
