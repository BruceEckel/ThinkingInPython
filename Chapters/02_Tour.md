# Tour

This chapter and the several that follow give a programmer's tour of Python:
syntax and the built-in numbers, strings, and `None` here, then containers,
control flow, functions, modules, classes, static typing, class attributes,
and object cleanup.
It assumes you have programming experience.
Find supplementary information in [the official language documentation](https://www.python.org/doc/).

## Scripting vs. Programming

Python exists to improve your productivity.
The language aims to aid you as much as possible.
It tries to hinder you as little as possible.
It does not impose arbitrary rules or force a particular set of features.

People often call Python a scripting language,
but scripting languages tend to be limiting,
especially in the scope of the problems that they solve.
Python is a programming language that also supports scripting.
It is marvelous for scripting, and you may replace all your batch files,
shell scripts, and simple programs with Python scripts.

## How to Read the Examples

The `#` denotes a comment that goes until the end of the line,
just like C++ and Java `//` comments.
[The Examples](01_Introduction.md#the-examples)
explains the filename first line and the `#:` output markers.

## Indentation and Blocks

Python is clean to write.
Your own code stays easy to read long after you've written it.
Indentation determines how statements group into blocks.
This script runs with `python if.py`:

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

A C/C++ `if` requires parentheses around the conditional.
Python needs no parentheses, although it won't complain if you use them.

The conditional clause ends with a colon.
A group of indented statements follows: the "then" part of the `if` statement.
The `print()` function sends its argument to standard output.
The next line assigns to a variable named `val`.
The subsequent statement is not indented, so it is no longer part of the `if`.

An indented block groups statements but does not create a scope.
Assigning `val` inside the `if` leaves it visible afterward,
unlike a variable declared inside braces in C++ or Java.
Functions, classes, and modules introduce new scopes;
an `if` or a `for` block does not.
Binding still follows execution: had `response` not been `"yes"`,
Python would not have bound `val`, and `print(val)` would raise a `NameError`.

Indenting can nest to any level.
Four spaces per level is the convention,
and mixing tabs and spaces inside one block is a `TabError`.
Unlike the brace-placement debates of C++ or Java,
the indentation is not a matter of taste: it is the structure.
Python code from any two authors therefore lines up the same way,
which is one of the main reasons for Python's consistent readability.

Python normally has only one statement per line,
so no terminating semicolon is necessary.
(You can put more than one statement on a line by separating them with semicolons.)

## Variables and References

A variable in Python is a name bound to an object, not a box that holds a value.
Assignment binds a name.
It does not copy.
You need not declare a variable's type,
and one name can bind to objects of different types over its life.
This is *dynamic typing*.
Python also has a full static type system layered on top,
which this book uses from [Static Typing](08_Static_Typing.md) onward.

```python
# references.py

x = 10  # x names an int
x = "ten"  # The same name now binds to a str
a = [1, 2, 3]
b = a  # b binds to the same list, not a copy
b.append(4)
print(a)  # The same object: a and b
#: [1, 2, 3, 4]
print(a is b)  # Identical objects
#: True
c = a[:]  # Copies the list, not its contents
print(a is c, a == c)  # Different object, equal value
#: False True
```

Use `==` to ask whether two objects have equal values.
Use `is` to ask whether two names refer to the same object.
Reserve `is` for `None` and other singletons.
`a[:]` is a *shallow* copy:
it duplicates the list but not the objects inside it,
so `a` and `c` would still share a nested list.

You can assign several names at once, so a swap needs no temporary:

```python
# multiple_assignment.py

a, b = 1, 2
a, b = b, a  # Swap without a temporary
print(a, b)
#: 2 1
first, *rest = [10, 20, 30, 40]
print(first, rest)
#: 10 [20, 30, 40]
```

`*rest` collects whatever remains.
[Containers](03_Containers.md#tuples-and-unpacking) covers the general form.

Numbers, strings, and tuples are *immutable*:
operations produce new objects rather than changing the original.
Lists, dictionaries, and sets are *mutable*.
Knowing which is which explains when a change is visible through another name,
as with `a` and `b` above.

## Numbers and Arithmetic

Integers have unlimited precision, so they cannot overflow.
Underscores group digits for readability:
`10_000_000` is the same literal as `10000000`.
Floating point is the usual IEEE double.
The operators are what you expect, with two worth noting:
`/` always produces a `float`, and `//` is floor division
(divide, then round down to a whole number; the result's type follows the operands, so `7.0 // 2` is `3.0`).
Floor division rounds toward negative infinity, not toward zero,
so `-7 // 2` is `-4` where C and Java give `-3`.
The remainder follows from that: `-7 % 2` is `1` in Python and `-1` in C.
The sign of `%` matches the divisor.

```python
# arithmetic.py

print(7 / 2)  # True division, always a float
#: 3.5
print(7 // 2)  # Floor division
#: 3
print(7 % 2)  # Remainder
#: 1
print(-7 // 2, -7 % 2)  # Floors, not truncates toward zero
#: -4 1
print(2 ** 10)  # Exponentiation
#: 1024
print(10 ** 30)  # A 31-digit int, no overflow
#: 1000000000000000000000000000000
print(abs(-5), round(3.14159, 2))
#: 5 3.14
total = 0
total += 5  # Augmented assignment, like other languages
print(total)
#: 5
scores = [90, 0, 71, 0, 55]
print(sum(s > 60 for s in scores))  # True counts as 1
#: 2
items = [1, 2]
alias = items
items += [3]  # In place, so alias sees it
print(alias)
#: [1, 2, 3]
```

Augmented assignment on a mutable object changes it in place,
so every other name for it sees the change.
`items = items + [3]` would instead build a new list and leave `alias` alone.
For an `int`, both forms rebind the name,
so `total += 5` above behaves the way `+=` does in any other language.

`round()` breaks a tie to the nearest even value,
so `round(0.5)` is `0` and `round(1.5)` is `2`,
rather than rounding half away from zero as C does.
An f-string's format spec rounds the same way.

Python has no `++` or `--`; use `+= 1` and `-= 1`.
Each arithmetic operator has an augmented-assignment form: `+=`, `-=`, `*=`,
`/=`, `//=`, `%=`, and `**=`.

A `bool` is a subtype of `int`, so `True` equals `1` and `False` equals `0`.
Summing a sequence of comparisons therefore counts how many were true.
The argument to `sum()` is a *generator expression*,
which hands over one value at a time instead of building a list first;
[Comprehensions](16_Comprehensions.md#generator-expressions) covers the form.

Integers also support the bitwise and shift operators,
each with a matching augmented form (`&=`, `|=`, `^=`, `<<=`, `>>=`).
Binary literals, which start with `0b`, make the bit patterns readable:

```python
# bitwise.py

print(bin(0b1100 & 0b1010))  # AND, bits set in both
#: 0b1000
print(bin(0b1100 | 0b1010))  # OR, bits set in either
#: 0b1110
print(bin(0b1100 ^ 0b1010))  # XOR, bits set in exactly one
#: 0b110
print(bin(~0b1100))  # NOT, inverts every bit
#: -0b1101
print(bin(1 << 4))  # Left shift, same as 1 * 2 ** 4
#: 0b10000
print(bin(0b110000 >> 2))  # Right shift, same as 48 // 2 ** 2
#: 0b1100

flags = 0
flags |= 0b0010  # Set bits with the augmented form
flags |= 0b1000
print(bin(flags))
#: 0b1010
```

The `bin()` function converts an integer to a binary string for display.
Because Python integers have no fixed width,
`~` has no fixed number of bits to flip.
It produces `-x - 1`,
the value that flipping every bit gives in two's complement,
and `bin()` prints that as a sign followed by a magnitude,
so `~0b1100` reads as `-0b1101` rather than a row of ones.

Python reserves one further operator, `@` (with `@=` to match),
for matrix multiplication.
The built-in numeric types do not implement it,
but array libraries such as NumPy do.
The same character in front of a `def` or a `class` means something else:
that is decorator syntax, covered in [Decorators](14_Decorators.md).

## Booleans, None, and Truthiness

`None` is Python's single "no value" object, like `null` elsewhere.
It is the default return value of a function that returns nothing.

You can test any object in a boolean context.
Numbers are false when zero, containers are false when empty,
and `None` is always false.
Everything else is true, unless an object's type says otherwise.
This is *truthiness*,
and it lets you write `if items:` instead of `if len(items) != 0:`.
A type says otherwise by defining `__bool__()`; without one,
Python falls back to `__len__()`, which is why an empty container is false.

```python
# truthiness.py

for value in [0, 1, "", "hi", [], [1], None]:
    print(repr(value), "->", bool(value))
#: 0 -> False
#: 1 -> True
#: '' -> False
#: 'hi' -> True
#: [] -> False
#: [1] -> True
#: None -> False

if not []:
    print("empty")  # An empty list is falsy
#: empty

name = "" or "default"  # 'or' returns the first truthy operand
print(name)
#: default
count = 0
print(count or 10)  # 0 is falsy, so the fallback wins
#: 10
```

`repr()` returns a value's unambiguous representation,
so the empty string shows as `''` and not as blank.

`and` and `or` short-circuit and return one of their operands,
not a coerced boolean.
`x or default` is a common way to supply a fallback.
It has a sharp edge.
It replaces every falsy `x`, not only a missing one,
so it throws away a legitimate `0` or `""`.
When zero or an empty string is a legal value, test for `None` instead:
`default if x is None else x`.
That is a conditional expression, covered in [Control Flow](04_Control_Flow.md).

## Strings

Single or double quotes create strings.
If you surround a string with double quotes,
you can embed single quotes and vice versa:

```python
# strings.py

print("That isn't a horse")
#: That isn't a horse
print('You are not a "Viking"')
#: You are not a "Viking"
print("""
You're just pounding two
coconut halves together.
""")
#:
#: You're just pounding two
#: coconut halves together.
#:
print('''
"Oh no!" He exclaimed.
"It's the blancmange!"
''')
#:
#: "Oh no!" He exclaimed.
#: "It's the blancmange!"
#:
print(r'c:\python\lib\utils')
#: c:\python\lib\utils
```

Python's name comes not from the snake but from the Monty Python comedy troupe,
of which the language creator Guido van Rossum is a fan.
Examples often include Python-esque references.

The triple-quote syntax quotes everything, including newlines.
That suits any block of literal text, such as an embedded template, a SQL query,
or a chunk of HTML, which you can write out in full without escaping line breaks.

In an ordinary string, a backslash starts an escape sequence, as in C and Java:
`\n` is a newline and `\t` is a tab.
The `r` right before a string means "raw."
Python takes backslashes literally, so you don't need to double them.
A raw string still cannot end with a backslash,
because the backslash escapes the closing quote even here.

### Common String Operations

Strings are immutable sequences with a large set of methods.
[Slicing](03_Containers.md#lists) also selects portions,
and `in` tests membership:

```python
# string_methods.py

s = "  Hello, World  "
print(s.strip())
#: Hello, World
print(s.strip().lower())
#: hello, world
print("World" in s)
#: True
print("a,b,c".split(","))
#: ['a', 'b', 'c']
print("-".join(["2024", "06", "15"]))
#: 2024-06-15
print("ababab".replace("a", "X"))
#: XbXbXb
print(s.strip()[0:5])
#: Hello
```

String methods return new strings rather than changing the original.

### f-Strings

Modern Python uses *f-strings*.
Prefix the string with `f` and put expressions in curly braces.
It is readable and fast:

```python
# fstrings.py

name = "Alice"
score = 91.5
print(f"{name} scored {score}")
#: Alice scored 91.5
print(f"{name} scored {score:.0f}%")
#: Alice scored 92%
print(f"{name!r} has {len(name)} letters")
#: 'Alice' has 5 letters
total = 7
print(f"{total = }")  # Useful for debugging
#: total = 7
print(f"|{name:>10}|{score:<8.1f}|")
#: |     Alice|91.5    |
```

The format spec after a colon controls width, precision, and alignment.
`>` right-aligns and `<` left-aligns within the given width.
A `!r` on the expression, as in `{name!r}`,
formats the value with `repr()` instead of `str()`.

Existing code also carries two older styles: C's `printf()` syntax,
as in `"val: %d" % val`, and the `str.format()` method,
as in `"val: {}".format(val)`.
Both still work, and both use the same format mini-language.
F-strings replaced them, so this book does not use them.

### t-Strings {#t-strings}

An f-string produces a finished `str`,
deciding how each value becomes text before anything else sees it.
A *t-string* produces a `Template` instead:
the literal pieces and the interpolated values, kept apart,
for a consumer to assemble.

The reason to care is safety.
A consumer that receives the parts separately knows which text came from the program and which came from a value,
so it can quote, escape,
or reject the values before they become part of the result.

The parts look like this:

```python
# tstrings.py
from string.templatelib import Interpolation, Template

name = "Alice"
score = 91.5
message: Template = t"{name} scored {score:.0f}%"
print(message.strings)
#: ('', ' scored ', '%')
print([piece.expression for piece in message.interpolations])
#: ['name', 'score']

def shout(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            parts.append(format(piece.value, piece.format_spec))
        else:
            parts.append(piece.upper())
    return "".join(parts)

print(shout(message))
#: Alice SCORED 92%
```

Iterating a `Template` produces the pieces in order,
each either a `str` the author typed or an `Interpolation` carrying a value.
An `Interpolation` also remembers the source text of the expression that produced it,
which `piece.expression` reports.
Iteration skips empty literal strings,
so the leading `''` in `message.strings` does not reach the loop.
A consumer cannot assume that literals and interpolations alternate.
`shout()` uppercases only the literal text, leaving the values alone,
which no amount of work on a finished f-string could do reliably.
Uppercasing is only a demonstration;
[Composite and Interpreter](34_Composite_and_Interpreter.md#a-template-is-a-tree)
builds a query from the parts that way.

## Naming Conventions

Use `snake_case` for variables, functions, methods, and file names:
lower case with words separated by underscores, as in `this_is_snake_case`.

If something represents a constant, use all uppercase letters,
as in `THIS_IS_A_CONSTANT`.

Class names are `CapWords` (Pascal cased), starting with a capital letter,
without underscores and capitalizing intermediate words.
For example: `ThisIsMyClass`.

A class may instead use `snake_case` when it serves primarily as a callable,
documented and used the way a function is.
The standard library does this for `contextlib.suppress` and `functools.partial`,
and for builtins like `property` and `staticmethod`.
Reserve it for classes that behave like a function to their users.
The default for a class is still `CapWords`.

[PEP 8](https://www.python.org/dev/peps/pep-0008/#naming-conventions)
covers style issues.
Tools such as ruff can apply these to your code automatically
(or at least point them out).

## Exercises

1.  In `references.py`, add a line after `c = a[:]` that appends `99` to `c`.
    Print `a` and `c` and confirm only `c` changed,
    then explain why `b.append(4)` earlier did change what `a` sees,
    but this does not.
2.  In `truthiness.py`, add an empty dictionary `{}` and a dictionary with one entry to the list of test values.
    Predict what `bool()` reports for each before running it,
    then check your prediction.
3.  In `fstrings.py`, add a line that formats `score` with two decimal places instead of zero,
    using `{score:.2f}` in place of `{score:.0f}%`,
    and a second line using the debug specifier, `f"{score = }"`.
4.  `arithmetic.py` and `bitwise.py` each define one variable,
    `total` and `flags`.
    Rename them to `totalSum` and `flagBits`,
    then to `TOTAL_SUM` and `FLAG_BITS`.
    Every version runs.
    Using [Naming Conventions](#naming-conventions),
    say what each form signals to a reader who did not write the code,
    and which of the three a linter would flag.
5.  In `tstrings.py`, write a second consumer, `quoted(template)`,
    that wraps every interpolated value in single quotes and leaves the literal text alone,
    then print `quoted(message)`.
    Explain why you cannot post-process an f-string the same way.
6.  Before running anything,
    write down what C or Java would print for `-9 / 4` and `-9 % 4` using integer math,
    then what Python prints for `-9 // 4` and `-9 % 4`.
    Run `print(-9 // 4, -9 % 4)` and check.
    State the rule that predicts the sign of the result of `%`.
