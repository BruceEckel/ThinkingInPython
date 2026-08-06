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
