# Tour: Solutions

## 1. Aliasing vs. slicing

> In `references.py`, add a line after `c = a[:]` that appends `99` to `c`.
> Print `a` and `c` and confirm that `c` changed and `a` still holds `[1, 2, 3, 4]`,
> then explain why `b.append(4)` earlier changed the list bound to `a`,
> but appending to `c` does not.

<details>
<summary>Where to look</summary>

[Variables and References](../../Chapters/02_Foundations--Tour.md#variables-and-references)
shows that assignment binds a name to the existing list instead of copying it.
A slice builds a new list object, so `a` and `c` name different lists.
Check which of `b` and `c` names the same list as `a` before you explain the difference.

<details>
<summary>Done when</summary>

your edited `references.py` prints `[1, 2, 3, 4] [1, 2, 3, 4, 99]` for `print(a, c)`,
and you can say which of `b` and `c` names the same list object as `a`,
and how `a is c` shows it.

<details>
<summary>Solution</summary>

If you write `c = a` instead of `c = a[:]`,
the program prints `[1, 2, 3, 4, 99] [1, 2, 3, 4, 99]`.
`c` is then a third name for the one list,
so appending to `c` changes the list `a` names, as `b.append(4)` did.
The solution keeps the slice.

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

`b.append(4)` changes `a` too, because `b` and `a` name the same list object.
`c = a[:]` makes a new list with the same elements,
so `c.append(99)` changes `c` and leaves `a` alone.
The identity test shows the difference:
`references.py` prints `True` for `a is b` and `False` for `a is c`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 2. Truthiness of empty and non-empty containers

> In `truthiness.py`, add an empty dictionary `{}` and a dictionary with one entry to the list of test values.
> Predict what `bool()` reports for each before running `truthiness.py`,
> then check your prediction.

<details>
<summary>Where to look</summary>

[Booleans, None, and Truthiness](../../Chapters/02_Foundations--Tour.md#booleans-none-and-truthiness)
lists which values `bool()` reports as false.
Add the two dictionaries to the loop's list and write your predictions down first.
Then ask whether the rule you see for lists and strings extends to a `dict`.

<details>
<summary>Done when</summary>

you wrote a prediction for both dictionaries before running,
the loop prints nine lines with your two dictionaries last,
and you can state one rule that predicts `bool()` for every container in the list.

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

The rule is the same for every container: falsy when empty, truthy otherwise.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. f-string precision and the debug specifier

> In `fstrings.py`, add a line that formats `score` with two decimal places instead of zero,
> using `{score:.2f}` in place of `{score:.0f}%`,
> and a second line using the debug specifier, `f"{score = }"`.

<details>
<summary>Where to look</summary>

[f-Strings](../../Chapters/02_Foundations--Tour.md#f-strings)
covers the format spec after the colon in a replacement field.
Change the digit after the `.` in `.0f` to set the precision.
A trailing `=` inside the braces makes the field print its source text before the value.

<details>
<summary>Done when</summary>

your first new line shows the score as `91.50`,
and your second prints `score = 91.5`.

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

`.2f` always shows two digits after the decimal point, a trailing zero included.
One `{score = }` field replaces a debugging `print("score", score)`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. What a name signals

> `augmented.py` defines `total` and `bitwise.py` defines `flags`.
> Rename them to `totalSum` and `flagBits`,
> then to `TOTAL_SUM` and `FLAG_BITS`.
> Every version runs.
> Using [Naming Conventions](../../Chapters/02_Foundations--Tour.md#naming-conventions),
> say what each form signals to a reader who did not write the code,
> and which of the three a linter reports.

<details>
<summary>Where to look</summary>

[Naming Conventions](../../Chapters/02_Foundations--Tour.md#naming-conventions)
says what each casing form tells a reader.
Rename the variables in both styles and run each version to confirm the interpreter accepts every form.
The book's `pyproject.toml` turns on ruff's naming rules,
so run `ruff check` on the camelCase file inside the book's repository and see which rule code ruff reports.

<details>
<summary>Done when</summary>

all three versions print `5 0b1010`,
`ruff check` in the book's repository reports `N816` on the camelCase file and passes the uppercase one,
and you can say what each form tells a reader about whether the value changes.

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

All three forms run, since Python accepts any valid identifier as a name.
The forms differ in what a reader infers from each.
`total` and `flags` say "an ordinary variable that changes,"
which describes both variables.
`TOTAL_SUM` and `FLAG_BITS` say "a constant,
the same for the life of the program,"
yet `exercise_4_constants.py` reassigns both, with `+=` and `|=`.
Python and the linter both accept the reassignment,
so the name misleads every reader who trusts it.
`totalSum` and `flagBits` describe the author rather than the value.
They say the author came from Java or JavaScript.

A linter flags the camelCase form.
Ruff's pep8-naming rules report `N816` for a mixed-case global.
Ruff leaves those rules off by default.
This book's `pyproject.toml` turns them on with the `N` in its `select` list.
The uppercase form passes the linter and still violates [Naming Conventions](../../Chapters/02_Foundations--Tour.md#naming-conventions),
which reserves uppercase for constants and CapWords for class names.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. A third `Template` consumer

> In `template_consumers.py`, write a third consumer, `quoted(template)`,
> that wraps every interpolated value in single quotes and leaves the literal text alone,
> then print `quoted(message)`.
> Explain why you cannot post-process an f-string the same way.

<details>
<summary>Where to look</summary>

[t-Strings](../../Chapters/02_Foundations--Tour.md#t-strings)
shows a `Template` as a sequence of literal strings and `Interpolation` objects.
Iterate over the template, test each piece with `isinstance()`,
and build the result from the pieces.
For the explanation,
consider what an f-string has done by the time you receive its result.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from string.templatelib import Interpolation, Template

def quoted(template: Template) -> str:
    ...
```

<details>
<summary>Done when</summary>

`print(quoted(message))` prints `'Alice' scored '92'%`,
and you can name the information `quoted()` needs that an f-string's finished `str` no longer records.

<details>
<summary>Solution</summary>

`quoted()` and the `message` it formats:

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

If you build each value with `str(piece.value)`,
the way the chapter's `safe()` does, the output reads `'Alice' scored '91.5'%`.
The template's `:.0f` stays behind in `piece.format_spec`,
because `str()` receives the value alone.
The solution passes the value and its spec to `format()`, as `shout()` does,
so `score` still prints as `'92'`.

**Tell values from literal text.**
`quoted()` reverses the roles of `shout()`'s two branches.
`shout()` changes the literal text and passes each value through,
while `quoted()` changes each value and passes the literal text through.
Iterating over a template yields a `str` for text the author typed and an `Interpolation` for a value the program supplied,
so a two-branch `if`, rather than a parser, decides what to do with each piece.

You cannot post-process an f-string this way,
because an f-string produces a finished `str`,
with each value merged into the text.
`f"{name} scored {score:.0f}%"` evaluates to the single string `Alice scored 92%`.
The evaluation discards the record that `Alice` came from a variable and ` scored ` came from the source.
A post-processor has only the characters,
so it must guess which spans to quote by matching them against the values.
The guess fails as soon as a literal matches a value.
With `name = "scored"`, the finished string reads `scored scored 92%`,
and either of the two words can be the value.

`Template` removes that guess,
because it keeps each value apart from the literal text.
Quoting is a harmless demonstration,
but the same reasoning covers escaping a value before it enters SQL or HTML,
where a wrong guess is a security hole rather than a typo.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Numbers and Arithmetic](../../Chapters/02_Foundations--Tour.md#numbers-and-arithmetic)
describes `//` and `%` on integers.
Work the C or Java answer by truncating toward zero,
then the Python answer by flooring.
Use the identity relating `//`, `%`,
and the divisor to see what the remainder must be.

<details>
<summary>Done when</summary>

your rule for the sign of `%` predicts what `print(-9 % -4, 9 % -4)` prints before you run it,
and your C or Java answers satisfy `a == (a / b) * b + a % b` with `/` truncating toward zero.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
print(-9 // 4, -9 % 4)
#: -3 3
```

C and Java truncate integer division toward zero,
so their integer `-9 / 4` is `-2` and `-9 % 4` is `-1`.
Python floors toward negative infinity, so `-9 // 4` is `-3`.
The identity `a == (a // b) * b + a % b` then forces the remainder to `3`.

The result of `%` takes the sign of the divisor.
With a positive divisor the remainder is zero or positive,
which is why `index % len(items)` wraps an index below zero or past the end to a valid index.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
