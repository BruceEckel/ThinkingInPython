When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Deep review of `Chapters/05_Functions.md`. Fixes I was confident in are already
applied to the chapter (five prose edits: a forward link for "keyword-only
parameters", a sharper statement of when the `None`-sentinel default is needed,
an `is None`-not-truthiness warning, the "each `sentinel()` call builds a new
object" caveat, a first-class-function note at `trace()`, and disambiguating
"A `*args` parameter does the same thing"). Everything below is reported
instead.

Verified against Python 3.15.0b2 in this workspace: the `SyntaxError` text,
both `TypeError` messages, `dict.get(key, default=None, /)`, `ty`'s Liskov
behavior on renamed positional-only vs. named override parameters, and PEP 661's
non-caching `sentinel()`. PEP 661 is Final for 3.15 and `sentinel` is a real
builtin, so the chapter's claim is correct.

---

[] Reject

**Line 137 — "This behavior commonly confuses newcomers."**

Two problems. The book states its audience in the Introduction ("I am writing
for the programmer who already knows how to program"), so "newcomers" points at
someone who is not reading this book. And the sentence carries no information:
it says the trap is a trap, which the three preceding sentences already
demonstrated.

Proposed replacement, which says *why* it surprises instead:

```
The default looks like an expression the call evaluates, and it is not.
```

Alternative if you want to keep the "famous trap" signal: "It is the most
reported surprise in Python's function semantics." I recommend the first.

---

[] Reject

**Lines 139-144 — "changes made inside the function are visible outside it" is
asserted, never shown**

This paragraph carries the pass-by-object-reference rule, the single thing a
C++/Java reader most needs from a Functions chapter, and it arrives as prose
between two listings about something else. `references.py` in
[Variables and References](02_Tour.md#variables-and-references) shows aliasing
(`b = a; b.append(4)`) but never across a call boundary, and the linked
paragraph asks the reader to make that jump unaided.

The half that is missing is the contrast: mutating the argument is visible to
the caller, rebinding the parameter is not. Those two are a lookalike pair the
chapter never separates, and the second one is what a reader assumes when they
write `def f(x): x = something` and wonder why nothing happened outside.

Proposed listing, inserted after the paragraph at 139-144 (verified: runs
clean, markers correct, ruff clean at width 70):

````
```python
# mutating_arguments.py

def append_all(target, extras):
    target.extend(extras)

mine = [1, 2]
append_all(mine, [3, 4])
print(mine)  # The caller's list changed
#: [1, 2, 3, 4]

def rebind(target):
    target = ["replaced"]  # Rebinds the local name only
    print(target)

rebind(mine)
#: ['replaced']
print(mine)
#: [1, 2, 3, 4]
```

`append_all()` calls a method on the object the caller passed,
so the caller sees the change.
`rebind()` assigns to the parameter,
which points the local name at a new list and leaves the caller's list alone.
Mutating an argument reaches outside the function; rebinding one does not.
````

Cost: one more listing in a section that already has three, and it pushes the
sentinel material further down. If you would rather not grow the section, the
cheaper version is to add the second half of the contrast as one prose sentence
at line 142: "Rebinding the parameter instead of mutating it changes nothing
outside, because assignment moves the local name rather than the object."

---

[] Reject

**Lines 187-192, `sentinel_default.py` — LBYL where the book teaches EAFP**

```python
def get(data, key, default=MISSING):
    if key in data:
        return data[key]
```

[Control Flow](04_Control_Flow.md) teaches EAFP over LBYL with `eafp.py`, and
the house style names a dict lookup as the canonical case. This listing, one
chapter later, does the LBYL form and pays for two hash lookups on the hit path.

The deviation is not explained, and the two candidate reasons both fail on
inspection: it is not that the demo must print rather than raise (the `try`
form can return `MISSING` just as easily), and it is not clarity (the `try`
form makes "normally raises an exception here" literal instead of a comment
about code that isn't there).

Proposed body, verified to produce identical output for all four calls:

```python
def get(data, key, default=MISSING):
    try:
        return data[key]
    except KeyError:
        if default is MISSING:
            return MISSING  # Normally re-raises here
        return default
```

I recommend the change. The alternative is to keep `key in data` and say in
prose why the membership test is the clearer teaching form here, since the
point of the listing is the three-way distinction (present, present-as-`None`,
absent) rather than the lookup itself.

---

[] Reject

**Line 252, `unpacking.py` — inline comment narrates the next line**

```python
# ** unpacks a dictionary into keyword arguments:
d = {"a": 3.14, "b": 1.62, "c": 2.72}
```

The house style says new descriptions belong in prose and "Never narrate what
the next line does." The prose thirteen lines above already says exactly this
("`**` unpacks a dictionary into keyword arguments"), so the comment is a
verbatim repeat inside the listing.

Proposed change: delete the comment line. Nothing else in the listing carries a
narrating comment, so its removal makes the block consistent with itself.

---

[] Reject

**Lines 286-293 and 342-347 — the reason for `/` arrives 55 lines after the
mechanism**

The section opens with "Two markers in a parameter list control how callers may
pass arguments" and then spends a listing on the syntax. The reader learns
*why* anyone writes `/` only in the closing paragraph: it keeps the parameter
name out of the contract, so a subclass can rename it. (I confirmed the claim
under `ty` 0.0.65: renaming a positional-only parameter in an override is
clean, renaming a positional-or-keyword one raises `invalid-method-override`
citing Liskov.)

Proposed change: move the motivation into the opener. Replace lines 286-287

```
Two markers in a parameter list control how callers may pass arguments.
A `/` ends the *positional-only* parameters.
```

with

```
Two markers in a parameter list control how callers may pass arguments,
which decides how much of a signature you are committed to keeping.
A parameter a caller can name is part of the contract; one it cannot is not.
A `/` ends the *positional-only* parameters.
```

and leave the subclass-override paragraph where it is as the concrete payoff.

Cost: three section titles in this chapter are named by cross-references from
other chapters, and this is one of them
(`22_Data_Transfer_Objects.md`, `34_Composite_and_Interpreter.md`,
`40_Functional_Foundations.md` all link
`#positional-only-and-keyword-only-parameters`). This edit does not touch the
heading, so those links are safe; do not rename the section.

---

[] Reject

**Lines 286-293 — the combined form and the parameter order rule are never
stated**

`param_markers.py` shows `/` alone, `*` alone, and `*args`, but never two
markers in one signature, and the chapter never states the order the forms must
appear in. The reader first meets the combined form in the *answer* to exercise
3 (`Solutions/05_Functions.md`, `def divide(a, b, /, *, label="result")`),
which is the wrong place to learn a grammar rule.

Proposed addition at the end of the prose block at 286-293:

````
A signature can use every form at once, in one fixed order:
positional-only, positional-or-keyword, `*args`, keyword-only, `**kwargs`.

```python
# all_markers.py

def f(a, /, b, *args, c, **kwargs):
    print(a, b, args, c, kwargs)

f(1, 2, 3, 4, c=5, d=6)
#: 1 2 (3, 4) 5 {'d': 6}
```

`a` can only arrive positionally, `c` can only arrive by name,
and `b` can do either.
````

Verified: runs, marker correct, ruff clean. Cheaper alternative if you do not
want a sixth listing in this section: keep the sentence naming the order and
drop the block.

---

[] Reject

**Line 323 — `param_markers.py` prints the exception type here and the message
below, with no visible reason**

```python
try:
    divide(a=10, b=2)  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

Twelve lines later the same listing prints `e` in full for `make_user()`, and
the prose then quotes the message this block withheld. A reader sees two
identical situations handled two ways.

The cause is the 70-column limit: the marker would have to read
`#: divide() got some positional-only arguments passed as keyword arguments:
'a, b'`, which is 82 characters and fails ruff. There is no shorter function
name that fits, so the current form is correct and should stay.

Proposed change: none to the code. Recording it here so a future pass does not
"fix" the inconsistency by printing `e` and then discover why it cannot.
Optionally, one prose word acknowledging it: change line 337 from "It reports"
to "The full message reports", which tells the reader the listing is showing
them less than Python said.

---

[] Reject

**Whole chapter — local scope and `global` are never introduced, and two later
chapters use `global` before it is explained**

The chapter covers every way an argument can enter a function and never covers
what happens to a name assigned inside one. The consequence is book-wide:
`global` is *used* with no explanation in `Chapters/18_Performance.md` (line
691) and five times in `Chapters/19_Concurrency.md`, and is first *explained* in
`Chapters/24_Singleton.md` (lines 245-255). `Chapters/40_Functional_Foundations.md`
explains `nonlocal` by asserting "assignment is how Python decides a name is
local", a rule the reader has never been shown.

This is the third of the three surprises a C++/Java reader hits with Python
functions. The chapter already covers the other two (mutable defaults, and
argument mutation if the block above is accepted), so the natural home is here.

Proposed section, placed after "Default and Keyword Arguments" (verified: runs,
markers correct, ruff clean):

````
## Names Inside a Function

A function can read a module-level name,
but assigning to that name anywhere in the function makes it local for the
whole function.
`global` says the assignment should rebind the module-level name instead:

```python
# function_scope.py

count = 0

def read_only():
    print(count)

def rebinds():
    count = 99  # A local, unrelated to the module-level count
    print(count)

def writes_global():
    global count
    count += 1

read_only()
#: 0
rebinds()
#: 99
writes_global()
print(count)
#: 1
```

`rebinds()` never touches the module-level `count`.
Drop the `global` from `writes_global()` and `count += 1` reads a local that
was never assigned, so the call raises `UnboundLocalError`.
`global` governs rebinding, not reading, which is why `read_only()` needs
nothing.
[Closures](40_Functional_Foundations.md#closures) covers `nonlocal`,
the same idea one scope in.
````

Cost: a sixth section in a chapter of five, and it is the only section not about
the parameter list, so the chapter's one-sentence claim widens from "how
arguments get in" to "how names work in a function." Judge that against the
alternative, which is leaving chapters 18 and 19 using an unexplained keyword.

## Cross-chapter

If this block is rejected, the cheaper repair belongs in the two chapters that
use `global` early, not here: `Chapters/18_Performance.md` line 691 and the
first use in `Chapters/19_Concurrency.md` (line 590) could each carry a link to
`[Singleton](24_Singleton.md#...)`, where `global` is actually explained. I did
not touch either chapter.

---

[] Reject

**Whole chapter — returning more than one value is never shown**

`return a, b` and `x, y = f()` is one of the first things a reader coming from
C or Java notices about Python functions, and this chapter never shows it.
`02_Tour.md` teaches tuple unpacking (`a, b = 1, 2`) and `03_Containers.md`
teaches the general form, but neither pairs it with a `return`, so the
function-side idiom appears nowhere in Part I.

Proposed change: one sentence and a two-line block in the opening section,
after "A bare `return` and a missing `return` both produce `None`." at line 54:

````
A `return` with several expressions produces a tuple,
which the caller usually unpacks:

    def minmax(values):
        return min(values), max(values)

    low, high = minmax([3, 1, 4])
````

An indented block, not a fenced one, matching the `items: Sequence[str] = ()`
aside already in the chapter, so it costs no new extractable example.

---

[] Reject

**Lines 375-393, Exercises — `/` and `**kwargs` are the two forms nothing
exercises**

Six exercises cover mutable defaults, sentinels, keyword-only, `*args` plus a
keyword-only flag, lambdas, and unpacking. Two gaps:

- No exercise makes the reader write `/`. Exercise 3 mentions `divide()` but
  adds a keyword-only parameter to it; the `/` is inherited, not authored.
- No exercise makes the reader collect with `**kwargs`. Exercise 6 unpacks
  *into* one, which is the other direction.

Proposed addition as exercise 7:

```
7.  Write `describe(name, /, **facts)` that prints `name` followed by each
    keyword argument as `key=value`, one per line.
    Confirm that `describe(name="Bob")` is a `TypeError`,
    and explain which marker caused it.
```

One exercise closes both gaps. If you prefer six, the alternative is to change
exercise 3's second half from the keyword-only check to the positional-only
one.
