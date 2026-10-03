# Tour: Solutions

## 1. Aliasing vs. slicing

> In `references.py`, add a line after `c = a[:]` that appends `99` to `c`.
> Print `a` and `c` and confirm only `c` changed,
> then explain why `b.append(4)` earlier did change what `a` sees,
> but appending to `c` does not.

<details>
<summary>Where to look</summary>

[Variables and References](../../Chapters/02_Foundations--Tour.md#variables-and-references) shows that assignment copies a reference, not the list.
A slice builds a new list object, so `a` and `c` stop sharing.
Check which of `b` and `c` names the same list as `a` before you explain the difference.

<details>
<summary>Solution</summary>

```python
# exercise_1.py
a = [1, 2, 3]
b = a  # b is another name for the same list
b.append(4)
c = a[:]  # A shallow copy: a new list, same values
c.append(99)
print(a, c)
#: [1, 2, 3, 4] [1, 2, 3, 4, 99]
```

`b.append(4)` changes `a` too, because `b` and `a` name the same list
object. `c = a[:]` makes a new list with the same elements, so
`c.append(99)` only changes `c`. Slicing copies. Assignment does not.

</details>
</details>

## 2. Truthiness of empty and non-empty containers

> In `truthiness.py`, add an empty dictionary `{}` and a dictionary with one entry to the list of test values.
> Predict what `bool()` reports for each before running it,
> then check your prediction.

<details>
<summary>Where to look</summary>

[Booleans, None, and Truthiness](../../Chapters/02_Foundations--Tour.md#booleans-none-and-truthiness) lists which values `bool()` reports as false.
Add the two dictionaries to the loop's list and write your predictions down first.
Then ask whether the rule you see for lists and strings extends to a `dict`.

<details>
<summary>Solution</summary>

```python
# exercise_2.py
for value in [0, 1, "", "hi", [], [1], None, {}, {"k": 1}]:
    print(repr(value), "->", bool(value))
#: 0 -> False
#: 1 -> True
#: '' -> False
#: 'hi' -> True
#: [] -> False
#: [1] -> True
#: None -> False
#: {} -> False
#: {'k': 1} -> True
```

An empty dictionary is falsy, the same as an empty list or an empty
string. A dictionary with even one entry is truthy. The rule is the
same for every container: falsy when empty, truthy otherwise.

</details>
</details>

## 3. f-string precision and the debug specifier

> In `fstrings.py`, add a line that formats `score` with two decimal places instead of zero,
> using `{score:.2f}` in place of `{score:.0f}%`,
> and a second line using the debug specifier, `f"{score = }"`.

<details>
<summary>Where to look</summary>

[f-Strings](../../Chapters/02_Foundations--Tour.md#f-strings) covers the format spec after the colon in a replacement field.
Change the digit after the `.` in `.0f` to set the precision.
A trailing `=` inside the braces makes the field print its own source text before the value.

<details>
<summary>Solution</summary>

```python
# exercise_3.py
name = "Alice"
score = 91.5
print(f"{name} scored {score:.2f}")
#: Alice scored 91.50
print(f"{score = }")
#: score = 91.5
```

`.2f` always shows two digits after the decimal point, even when the
second digit is a trailing zero. `{score = }` prints both the
expression's source text and its value, so a quick debugging print
needs no separate `print("score", score)`.

</details>
</details>

## 4. What a name signals

> `augmented.py` defines `total` and `bitwise.py` defines `flags`.
> Rename them to `totalSum` and `flagBits`,
> then to `TOTAL_SUM` and `FLAG_BITS`.
> Every version runs.
> Using [Naming Conventions](../../Chapters/02_Foundations--Tour.md#naming-conventions),
> say what each form signals to a reader who did not write the code,
> and which of the three a linter flags.

<details>
<summary>Where to look</summary>

[Naming Conventions](../../Chapters/02_Foundations--Tour.md#naming-conventions) says what each casing form tells a reader.
Rename the variables in both styles and run each version to confirm the interpreter does not care.
Then run `ruff check` on the camelCase file and see which rule code it reports.

<details>
<summary>Solution</summary>

The camelCase versions of `total` and `flags`:

```python
# exercise_4.py
totalSum = 0  # noqa: N816
totalSum += 5  # noqa: N816
flagBits = 0b0010  # noqa: N816
flagBits |= 0b1000  # noqa: N816
print(totalSum, bin(flagBits))
#: 5 0b1010
```

And the all-uppercase versions:

```python
# exercise_4_constants.py
TOTAL_SUM = 0
TOTAL_SUM += 5
FLAG_BITS = 0b0010
FLAG_BITS |= 0b1000
print(TOTAL_SUM, bin(FLAG_BITS))
#: 5 0b1010
```

All three forms run, since Python does not enforce a naming convention
at the language level. What differs is what a reader infers.
`total` and `flags` say "an ordinary variable that changes,"
which is what both of these are. `TOTAL_SUM` and `FLAG_BITS` say "a
constant, fixed for the life of the program," and the second line of
`exercise_4_constants.py` changes `TOTAL_SUM` anyway. Neither Python nor the linter objects,
so the name misleads every reader who trusts it.
`totalSum` and `flagBits` say nothing about the value. They only say the
author came from Java or JavaScript.

Only the camelCase form breaks
[Naming Conventions](../../Chapters/02_Foundations--Tour.md#naming-conventions), and it
is the only one a linter objects to: ruff's PEP 8 checks report `N816`
for a mixed-case global. The uppercase form is legal style, merely a
false claim about the value. CapWords stays reserved for class names.

</details>
</details>

## 5. A third `Template` consumer

> In `tstrings.py`, write a third consumer, `quoted(template)`,
> that wraps every interpolated value in single quotes and leaves the literal text alone,
> then print `quoted(message)`.
> Explain why you cannot post-process an f-string the same way.

<details>
<summary>Where to look</summary>

[t-Strings](../../Chapters/02_Foundations--Tour.md#t-strings) shows a `Template` as a sequence of literal strings and `Interpolation` objects.
Iterate over the template, test each piece with `isinstance()`, and build the result from the pieces.
For the explanation, consider what an f-string has already done by the time you receive its result.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from string.templatelib import Interpolation, Template

def quoted(template: Template) -> str:
    ...
```

<details>
<summary>Solution</summary>

If you build each value with `str(piece.value)`, the way the chapter's `safe()` does,
the output reads `'Alice' scored '91.5'%`.
The value drops the template's `:.0f`,
because `str()` receives the value alone and the `Interpolation` keeps the spec separately, in `piece.format_spec`.
The solution passes the value and its spec to `format()`, as `shout()` does, so `score` still prints as `'92'`.

```python
# exercise_5.py
from string.templatelib import Interpolation, Template

name = "Alice"
score = 91.5
message: Template = t"{name} scored {score:.0f}%"

def quoted(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            value = format(piece.value, piece.format_spec)
            parts.append(f"'{value}'")
        else:
            parts.append(piece)
    return "".join(parts)

print(quoted(message))
#: 'Alice' scored '92'%
```

**Tell values from literal text.** `quoted()` is `shout()` with the two branches swapped over: the
`Interpolation` branch is the one that changes something, and the
literal branch passes its text through. The `isinstance()` test does
all the work. Each piece arrives already labelled as text the author
typed or as a value the program supplied, so deciding what to do with
each is a two-line `if` rather than a parsing problem.

You cannot post-process an f-string this way, because the string it
produces carries no label. `f"{name} scored {score:.0f}%"` evaluates to
the single string `Alice scored 92%`, and nothing in that string records
that `Alice` came from a variable and ` scored ` came from the source.
A post-processor has only the characters, so it must guess
which spans to quote by matching them against the values. The guess
fails as soon as a literal looks like a value: with
`name = "scored"`, the finished string reads `scored scored 92%`, and
nothing in it says which of the two words is the value.

That failed guess is the argument for `Template` in one example.
Quoting is a harmless demonstration, but the same reasoning covers
escaping a value before it enters SQL or HTML, where a wrong guess is a
security hole rather than a typo.

</details>
</details>
</details>

## 6. Negative floor division and modulo

> Before running anything,
> write down what C or Java prints for `-9 / 4` and `-9 % 4` using integer math,
> then what Python prints for `-9 // 4` and `-9 % 4`.
> Run `print(-9 // 4, -9 % 4)` and check.
> State the rule that predicts the sign of the result of `%`.

<details>
<summary>Where to look</summary>

[Numbers and Arithmetic](../../Chapters/02_Foundations--Tour.md#numbers-and-arithmetic) describes `//` and `%` on integers.
Work the C or Java answer by truncating toward zero, then the Python answer by flooring.
Use the identity relating `//`, `%`, and the divisor to see what the remainder must be.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
print(-9 // 4, -9 % 4)
#: -3 3
```

C and Java truncate integer division toward zero, so their integer
`-9 / 4` is `-2` and `-9 % 4` is `-1`. Python floors toward negative
infinity, so `-9 // 4` is `-3`. The identity
`a == (a // b) * b + a % b` then forces the remainder to `3`. The rule
is that the result of `%` takes the sign of the divisor. With a
positive divisor the remainder is nonnegative, which is why
`index % len(items)` wraps cleanly in either direction.

</details>
</details>
