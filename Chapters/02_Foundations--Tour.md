# Tour

> You know a language,
> and Python differs from it in a few places that matter more than the syntax.

This chapter and the ones that follow give a programmer's tour of Python:
syntax and the built-in numbers, strings, and `None` here, then containers,
control flow, functions, modules, classes, static typing, class attributes,
and object cleanup.
The tour assumes you have programming experience.
Find supplementary information in [the official language documentation](https://www.python.org/doc/).

## Scripting vs. Programming

Python exists to improve your productivity.
The language aims to aid you as much as possible and to hinder you as little as possible.

People often call Python a scripting language,
but scripting languages tend to limit you,
especially in the range of problems they can solve.
Python is a programming language that also supports scripting.
It is marvelous for scripting.
You may replace all your batch files, shell scripts,
and simple programs with Python scripts.

## How to Read the Examples

The `#` starts a comment that runs to the end of the line,
like C++ and Java `//` comments.
[The Examples](01_Introduction.md#the-examples)
explains the filename comment on a listing's first line and the `#:` output markers.

## Indentation and Blocks

Python is clean to write.
Your code stays easy to read long after you've written it.
Part of that readability comes from indentation,
which determines how statements group into blocks.
Here, the script runs with `python if.py`:

```python
# if.py

response = "yes"
if response == "yes":
    print("affirmative")
    val = 1  # [1]
#: affirmative
print("continuing...")  # [2]
#: continuing...
print(val)
#: 1
```

A C/C++ `if` requires parentheses around the conditional.
Python makes them optional.

The conditional clause ends with a colon.
A group of indented statements follows: the "then" part of the `if` statement.
The `print()` function sends its arguments to standard output,
separated by spaces and followed by a newline.
The statement at `[2]` starts at the left margin again,
and that change in indentation ends the `if`.

An indented block groups statements inside the enclosing scope,
so the `val` assigned at `[1]` stays visible after the `if`.
In C++ or Java, a variable declared inside braces goes out of scope at the closing brace.
In Python, an `if` or a `for` block shares the scope around it.
New scopes come from functions, classes, modules, and comprehensions.

Python binds a name only when the assignment runs.

```python
# unbound_val.py

response = "no"
if response == "yes":
    val = 1
try:
    print(val)  # type: ignore
except NameError as e:
    print(e)
#: name 'val' is not defined
```

Indentation shows where the assignment sits, not whether it runs.

The type checker infers that `val = 1` cannot run and reports an error on `print(val)`.
The `# type: ignore` tells it the mistake is deliberate.
The [`try` and `except`](04_Foundations--Control_Flow.md#errors-and-exceptions)
catch the exception so the script can print the exception's message and finish.

Blocks can nest, each one indented further than the block that contains it.
Four spaces per level is the convention.
Mixing tabs and spaces inconsistently inside one block raises a `TabError`.

C++ and Java programmers debate where braces go.
In Python the indentation is the structure,
so the language settles the question.
Python code from any two authors therefore lines up the same way.
That sameness is one of the main reasons for Python's consistent readability.

A statement ends with its line.
C++ and Java end each one with a semicolon.
A semicolon's one job is to separate two statements that share a line.
An open parenthesis, bracket,
or brace continues the statement across lines until it closes.
You choose the indentation of those continued lines.
The longer calls in `tstrings.py` and `template_consumers.py` wrap that way.

## Variables and References

A variable in Python is a name bound to an object, not a box that holds a value.
Assignment binds a name.
It does not copy.
Python does not require you to declare a variable's type,
and one name can bind to objects of different types over its life.
That freedom is *dynamic typing*.

```python
# references.py

x = 10  # x names an int
print(type(x).__name__)
#: int
x = "ten"  # The same name now binds to a str
print(type(x).__name__)
#: str
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
nested = [[1], [2, 3]]
shallow = nested[:]
shallow[1].append(99)
print(nested)  # The inner list is shared
#: [[1], [2, 3, 99]]
```

Use `==` to ask whether two objects have equal values.
Use `is` to ask whether two names refer to the same object.
Reserve `is` for `None` and other singletons.

`a[:]` is a *shallow* copy.
It duplicates the outer list.
The copy shares the outer list's inner objects.
The standard library's `copy.deepcopy()` duplicates the inner objects as well as the outer list.

Numbers, strings, and tuples are *immutable*.
Operations on them produce new objects and leave the original as it was.
Lists, dictionaries, and sets are *mutable*.
Mutability decides whether a change made through one name is visible through another,
as the `4` appended through `b` is visible through `a` in `references.py`.

You can assign several names at once, so a swap takes one line:

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

[Containers](03_Foundations--Containers.md#tuples-and-unpacking)
covers the general form of `*rest`.

## Numbers and Arithmetic

Integers have unlimited precision, so they cannot overflow.
Underscores group digits for readability,
so `10_000_000` is the same literal as `10000000`.
A `float` is a 64-bit IEEE 754 double, the same as C's and Java's `double`.

`+`, `-`, and `*` work as in C and Java.
Division differs in two ways: `/` on integers always produces a `float`,
and `//` is floor division (divide, then round down to a whole number).
The result's type follows the operands, so `7.0 // 2` is `3.0`.
Floor division rounds toward negative infinity, not toward zero,
so `-7 // 2` is `-4` where C and Java give `-3`.
The remainder follows from that, so `-7 % 2` is `1` in Python and `-1` in C.
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
print(round(0.5), round(1.5), round(2.5))  # Ties go to even
#: 0 2 2
print(True + True, True == 1)  # A bool is an int
#: 2 True
```

`round()` breaks a tie to the nearest even value.
C's `round()` rounds half away from zero.
The format spec of an [f-string](#f-strings), later in this chapter,
rounds ties the way `round()` does.

A `bool` is a subtype of `int`, so `True` equals `1` and `False` equals `0`.

Python has no `++` or `--`.
Use `+= 1` and `-= 1`.
The prefix form parses and runs.
`++count` applies unary plus twice and leaves `count` at its old value.
The postfix `count++` is a syntax error.

Each arithmetic operator has an augmented-assignment form: `+=`, `-=`, `*=`,
`/=`, `//=`, `%=`, and `**=`.

```python
# augmented.py

total = 0
total += 5  # Augmented assignment, like other languages
print(total)
#: 5
items = [1, 2]
alias = items
items += [3]  # In place, so alias sees it
print(alias)
#: [1, 2, 3]
items = items + [4]  # A new list, alias keeps the old one
print(alias, items)
#: [1, 2, 3] [1, 2, 3, 4]
```

Augmented assignment on a mutable object changes it in place,
so every other name bound to that object refers to the changed object.
For a list, `+=` does what `extend()` does.
For an `int`, both forms rebind the name,
so `total += 5` behaves the way `+=` does in any other language.

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
# Right shift, same as 48 // 2 ** 2
print(bin(0b110000 >> 2))
#: 0b1100

flags = 0
flags |= 0b0010  # Set bits with the augmented form
flags |= 0b1000
print(bin(flags))
#: 0b1010
```

The `bin()` function converts an integer to a binary string for display.
Because a Python integer grows as wide as its value needs,
`~` has no set number of bits to flip.
`~x` produces `-x - 1`,
the value that flipping every bit gives in two's complement.
`bin()` prints that as a sign followed by a magnitude,
so `~0b1100` reads as `-0b1101` rather than a row of ones.

Python reserves one further operator, `@` (with `@=` to match),
for matrix multiplication.
The built-in numeric types do not implement it,
but array libraries such as NumPy do.
In front of a `def` or a `class`,
the same character marks a [decorator](14_Techniques--Decorators.md).

## Booleans, None, and Truthiness

`None` is Python's single "no value" object, like `null` elsewhere.
It is every function's default return value.

You can test any object in a boolean context.
Numbers are false when zero, containers are false when empty,
and `None` is always false.
Everything else is true, unless the object's type defines its own test.
That rule is *truthiness*,
and it lets you write `if items:` instead of `if len(items) != 0:`.

A type defines that test with `__bool__()`, a *dunder*:
a name with double underscores at each end.
Python reserves dunder names for the methods and attributes the interpreter itself calls and reads,
as an `if` calls `__bool__()`.
Without `__bool__()`, Python falls back to `__len__()`,
so an empty container is false.

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

class Bucket:
    def __init__(self, count: int) -> None:
        self.count = count

    def __len__(self) -> int:
        return self.count

print(bool(Bucket(0)), bool(Bucket(3)))
#: False True

items = []
if not items:
    print("empty")  # An empty list is falsy
#: empty
```

`repr()` returns a value's unambiguous representation,
so the empty string appears as a visible `''`.
`Bucket` defines no `__bool__()`, so `bool()` falls back to its `__len__()`.

`Bucket` is a small [class](07_Foundations--Classes.md).
Its `count: int` and `-> int` are [type hints](08_Foundations--Static_Types.md#type-hints).
They state the types for the reader and the type checker.
The code runs the same with or without them.

Python's logical operators are the words `and`, `or`, and `not`,
where C and Java write `&&`, `||`, and `!`.
The bitwise `&` and `|` from `bitwise.py` also accept `bool` values.
Unlike `and` and `or`, `&` and `|` bind more tightly than a comparison,
so `x > 0 & y > 0` means `x > (0 & y) > 0`,
which is `False` for any integers `x` and `y`.

`not` always produces a `bool`.
`and` and `or` short-circuit and return one of their operands,
not a coerced boolean:

```python
# or_fallback.py

# 'or' returns the first truthy operand
name = "" or "default"
print(name)
#: default
items = []
print(items and items[0])  # Stops at the falsy operand
#: []
count = 0
print(count or 10)  # 0 is falsy, so the fallback wins
#: 10
print(10 if count is None else count)  # Keeps the 0
#: 0
```

`and` stops at its first falsy operand and returns it,
so Python skips `items[0]` on the empty list.
When every operand is truthy, `and` returns the last one,
so the same expression on a nonempty list yields `items[0]`.

`x or default` is a common way to supply a fallback,
but it replaces every falsy `x`.
A legitimate `0` or `""` gets the fallback the same as a missing value does.
When zero or an empty string is a legal value, test for `None` instead:
`default if x is None else x`.
That is a [conditional expression](04_Foundations--Control_Flow.md#conditionals).

## Strings

### String Literals

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

A triple-quoted string can span lines, and it keeps every newline it contains.
That suits any block of literal text, such as an embedded template, a SQL query,
or a chunk of HTML.
You write the text out in full, line breaks and all.

The string also holds the newline right after the opening quotes and the one before the closing quotes.
So each triple-quoted output in `strings.py` begins and ends with an empty `#:` line.

In an ordinary string, a backslash starts an escape sequence, as in C and Java.
`\n` is a newline and `\t` is a tab.
The `r` right before a string means "raw."
Python takes each backslash in a raw string literally, as a single character.
Without the `r`, the `\u` in the last literal of `strings.py` starts a Unicode escape,
which requires four hex digits.
The `t` after it falls outside the hex digits `0`-`9` and `a`-`f`,
so the literal is a syntax error.
A raw string has one limit: it cannot end with a single backslash,
because a backslash in a raw string still makes the quote after it part of the string's text.

### Common String Operations

Strings are immutable sequences with a large set of methods.
[Slicing](03_Foundations--Containers.md#indexing-and-slicing)
selects a range of characters, and `in` tests for a substring:

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
print(repr(s))
#: '  Hello, World  '
print("test_setup".lstrip("test_"))
#: up
print("test_setup".removeprefix("test_"))
#: setup
print("notes.txt".removesuffix(".txt"))
#: notes
```

String methods return new values and leave the original string intact.
After three calls on `s`, `repr(s)` still shows its surrounding spaces,
and the quotes that `repr()` adds make those spaces visible.
An optional third argument to `replace()` limits how many occurrences it replaces.

`strip()` and its one-sided forms `lstrip()` and `rstrip()` take an optional argument,
but that argument is a set of characters, not a prefix or suffix.
`"test_setup".lstrip("test_")` removes every leading `t`, `e`, `s`, and `_`,
leaving `"up"`.
To remove one exact piece from an end, use `removeprefix()` or `removesuffix()`.

`+` joins two strings and leaves any conversion to you:

```python
# concatenate.py

total = 7
try:
    print("total: " + total)  # type: ignore
except TypeError as e:
    print(e)
#: can only concatenate str (not "int") to str
print("total: " + str(total))
#: total: 7
```

Java and JavaScript turn the `7` into text and join it.
Python requires two strings, so you write the conversion,
either with `str()` or inside an f-string.

### f-Strings

Modern Python uses *f-strings*.
Prefix the string with `f` and put expressions in curly braces.
Each expression sits where its value appears in the result.
Python compiles an f-string into dedicated instructions that format each value and join the pieces:

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
print(f"{name = }")  # Useful for debugging
#: name = 'Alice'
print(f"|{name:>10}|{score:<8.1f}|")
#: |     Alice|91.5    |
```

The format spec after a colon controls width, precision, and alignment.
`>` right-aligns and `<` left-aligns within the given width.
A comma or an underscore in the spec groups the digits by thousands,
so `f"{1234567:,}"` produces `1,234,567`.
Since Python 3.14, a separator after the precision groups the fractional digits as well,
so `f"{3.14159265:.6_f}"` produces `3.141_593`.
A `!r` on the expression, as in `{name!r}`,
formats the value with `repr()` instead of `str()`.
An `=` after the expression, as in `{name = }`, is the *debug specifier*.
It prints the expression's text, the `=` with any spaces you put around it,
and then the value.
By default the value appears as its `repr()`,
so the output shows `'Alice'` in quotes.
Use `=` to label values in your exploring and debugging code.

Since Python 3.12 ([PEP 701](https://peps.python.org/pep-0701/)),
the expression inside the braces can reuse the string's own quote character,
as in `f"{d["key"]}"`, hold a backslash, and span several lines.
Older code avoids all three because earlier versions rejected them.

Existing code also uses two older styles: the `%` operator,
as in `"val: %d" % val`, and the `str.format()` method,
as in `"val: {}".format(val)`.
Both still work.
`str.format()` shares the f-string's format mini-language,
while the `%` form has its own, inherited from C's `printf()`.
F-strings replaced them.

### t-Strings {#t-strings}

An f-string produces a finished `str`,
converting each value to text before any other code receives the `str`.
A *t-string* produces a `Template`.
The `Template` keeps the literal pieces and the interpolated values apart for a consumer to assemble.
Python 3.14 added t-strings ([PEP 750](https://peps.python.org/pep-0750/)).

T-strings exist for safety.
A consumer receives the literal text and the values as separate pieces,
so it can quote, escape,
or reject the values before they become part of the result.

```python
# tstrings.py
from string.templatelib import Template

name = "Alice"
score = 91.5
message: Template = t"{name} scored {score:.0f}%"
print(message.strings)
#: ('', ' scored ', '%')
for piece in message.interpolations:
    print(piece.expression, piece.value,
          repr(piece.format_spec))
#: name Alice ''
#: score 91.5 '.0f'
```

A `Template` stores its two kinds of piece separately.
`message.strings` holds the literal text around and between the values,
so it has one entry more than `message.interpolations`.
Because `message` opens with a value,
`message.strings` opens with an empty string, which prints as `''`.
`message.interpolations` holds one `Interpolation` per value.
Each `Interpolation` keeps the value,
the source text of the expression that produced it, and its format spec.

Iterating over a `Template` produces the pieces in order,
each either a `str` the author typed or an `Interpolation`.
Iteration skips empty literal strings,
so a loop over `message` starts with the `Interpolation` for `name`.
Because of that skipping,
a consumer cannot assume that literals and interpolations alternate.
Iterating over `t"{first}{last}"`, with two interpolations side by side,
produces two `Interpolation`s in a row.

Two consumers, `shout()` and `safe()`, each walk a `Template` piece by piece.

```python
# template_consumers.py
from string.templatelib import Interpolation, Template

name = "Alice"
score = 91.5
message: Template = t"{name} scored {score:.0f}%"

def shout(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            parts.append(
                format(piece.value, piece.format_spec))
        else:
            parts.append(piece.upper())
    return "".join(parts)

print(shout(message))
#: Alice SCORED 92%

def safe(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            value = str(piece.value)
            if "'" in value:
                raise ValueError(
                    f"unsafe value: {value!r}")
            parts.append(value)
        else:
            parts.append(piece)
    return "".join(parts)

print(safe(t"Hello, {name}"))
#: Hello, Alice
trouble = "Bob'; rm -rf /"
try:
    safe(t"Hello, {trouble}")
except ValueError as e:
    print(e)
#: unsafe value: "Bob'; rm -rf /"
```

`shout()` turns each value into text with the built-in `format()` and the format spec stored in the `Interpolation`,
so `score` still prints as `92`.
A finished f-string is a single `str` in which the values have merged into the literal text,
so code that processes it afterward must guess which characters came from a value.

`safe()` uses the same separation to check each value.
`trouble` holds a single quote,
so `safe(t"Hello, {trouble}")` raises a `ValueError` before any result exists.
An f-string finishes assembling the result, quote and all,
before any code can inspect the values.

Uppercasing and rejecting are small demonstrations.
[*Composite* and *Interpreter*](34_Patterns--Composite_and_Interpreter.md#a-template-is-a-tree)
builds a SQL query from a `Template`'s pieces,
writing a `?` in place of each value and collecting the values in a separate list.

Keep using f-strings for ordinary output.
Use a t-string only when a consumer must inspect, escape,
or reject the interpolated values before they become part of the result,
the way `safe()` does above.

## Naming Conventions

Use `snake_case` for variables, functions, methods, and file names:
lower case with words separated by underscores, as in `this_is_snake_case`.

For a constant, use all uppercase letters, as in `THIS_IS_A_CONSTANT`.

Class names are `CapWords` (Pascal cased).
Every word, including the first, begins with a capital letter,
and the words run together.
For example: `ThisIsMyClass`.

When users call a class the way they call a function,
that class may use `snake_case` instead,
so its name reads as the action the call performs.
The standard library names `contextlib.suppress`, `contextlib.redirect_stdout`,
and `functools.partial` that way.
Name every other class `CapWords`.

[PEP 8](https://peps.python.org/pep-0008/#naming-conventions)
gives the full naming rules and the conventions for layout, whitespace,
and imports.
Tools such as ruff report violations and fix many of them automatically.

## Exercises

Try each exercise before opening its [solution](../Solutions/02_Foundations--Tour/).

1.  In `references.py`, add a line after `c = a[:]` that appends `99` to `c`.
    Print `a` and `c` and confirm that `c` changed and `a` still holds `[1, 2, 3, 4]`,
    then explain why `b.append(4)` earlier changed the list bound to `a`,
    but appending to `c` does not.
2.  In `truthiness.py`, add an empty dictionary `{}` and a dictionary with one entry to the list of test values.
    Predict what `bool()` reports for each before running `truthiness.py`,
    then check your prediction.
3.  In `fstrings.py`, add a line that formats `score` with two decimal places instead of zero,
    using `{score:.2f}` in place of `{score:.0f}%`,
    and a second line using the debug specifier, `f"{score = }"`.
4.  `augmented.py` defines `total` and `bitwise.py` defines `flags`.
    Rename them to `totalSum` and `flagBits`,
    then to `TOTAL_SUM` and `FLAG_BITS`.
    Every version runs.
    Using [Naming Conventions](#naming-conventions),
    say what each form signals to a reader who did not write the code,
    and which of the three a linter reports.
5.  In `template_consumers.py`, write a third consumer, `quoted(template)`,
    that wraps every interpolated value in single quotes and leaves the literal text alone,
    then print `quoted(message)`.
    Explain why you cannot post-process an f-string the same way.
6.  Before running anything,
    write down what C or Java prints for `-9 / 4` and `-9 % 4` using integer math,
    then what Python prints for `-9 // 4` and `-9 % 4`.
    Run `print(-9 // 4, -9 % 4)` and check.
    State the rule that predicts the sign of the result of `%`.
