# Tour: Solutions

## 1. Aliasing vs. slicing

```python
# exercise_1.py
a = [1, 2, 3]
b = a           # b is another name for the same list
b.append(4)
c = a[:]        # A shallow copy: a new list, same values
c.append(99)
print(a, c)
#: [1, 2, 3, 4] [1, 2, 3, 4, 99]
```

`b.append(4)` changes `a` too, because `b` and `a` name the same list
object. `c = a[:]` makes a new list with the same elements, so
`c.append(99)` only changes `c`. Slicing copies; assignment does not.

## 2. Truthiness of empty and non-empty containers

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

## 3. f-string precision and the debug specifier

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
expression's source text and its value, which is why it is useful for
quick debugging prints: no need to write `print("score", score)`
separately.

## 4. What a name signals

The camelCase versions of `total` and `flags`:

```python
# exercise_4.py
totalSum = 0  # noqa: N816 (deliberately non-idiomatic; see below)
totalSum += 5  # noqa: N816
flagBits = 0b0010  # noqa: N816
flagBits |= 0b1000  # noqa: N816
print(totalSum, bin(flagBits))
#: 5 0b1010
```

And the all-uppercase versions:

```python
# exercise_4_constants.py
TOTAL_SUM = 5
FLAG_BITS = 0b1010
print(TOTAL_SUM, bin(FLAG_BITS))
#: 5 0b1010
```

All three forms run, since Python does not enforce a naming convention
at the language level. What differs is what a reader infers.
`total_sum` and `flag_bits` say "an ordinary variable that changes,"
which is what both of these are. `TOTAL_SUM` and `FLAG_BITS` say "a
constant, fixed for the life of the program," so using that form for a
running total misleads anyone who later tries to reuse the name.
`totalSum` and `flagBits` say nothing about the value; they only say the
author came from Java or JavaScript.

Only the camelCase form breaks
[Naming Conventions](../Chapters/02_Tour.md#naming-conventions), and it
is the only one a linter objects to: ruff's PEP 8 checks report `N816`
for a mixed-case global. The uppercase form is legal style, merely a
false claim about the value. CapWords stays reserved for class names.

## 5. A second `Template` consumer

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

`quoted()` is `shout()` with the two branches swapped over: the
`Interpolation` branch is the one that changes something, and the
literal branch passes its text through. The `isinstance()` test is the
whole mechanism. Each piece arrives already labelled as text the author
typed or as a value the program supplied, so deciding what to do with
each is a two-line `if` rather than a parsing problem.

An f-string cannot be post-processed this way because the label is gone
by the time you have one. `f"{name} scored {score:.0f}%"` evaluates to
the single string `Alice scored 92%`, and nothing in that string records
that `Alice` came from a variable and ` scored ` came from the source.
A post-processor has only the characters, so it would have to guess
which spans to quote by matching them against the values, and the guess
fails as soon as a literal happens to look like a value: with
`name = "scored"`, the finished string reads `scored scored 92%` and no
rule can tell the first word from the second.

That is the argument for `Template` in one example. Quoting is a
harmless demonstration, but the same reasoning covers escaping a value
before it enters SQL or HTML, which is the case where guessing wrong is
a security hole rather than a typo.

## 6. Negative floor division and modulo

```python
# exercise_6.py
print(-9 // 4, -9 % 4)
#: -3 3
```

C and Java truncate integer division toward zero, so their integer
`-9 / 4` is `-2` and `-9 % 4` is `-1`. Python floors toward negative
infinity, so `-9 // 4` is `-3`, and the identity
`a == (a // b) * b + a % b` then forces the remainder to `3`. The
rule: the result of `%` takes the sign of the divisor. With a
positive divisor the remainder is nonnegative, which is why
`index % len(items)` wraps cleanly in either direction.
