# Tour

This chapter and the several that follow give a programmer's tour of Python:
syntax and the scalar types here, then containers, control flow, functions,
modules, classes, and static typing in the chapters after it.
It assumes you have programming experience.
You can find supplementary information in [the official language documentation](https://www.python.org/doc/).

## Scripting vs. Programming

The goal of Python is improved productivity.
The language aims to aid you as much as possible.
It tries to hinder you as little as possible.
It does not impose arbitrary rules or force a particular set of features.

People often call Python a scripting language,
but scripting languages tend to be limiting,
especially in the scope of the problems that they solve.
Python is a programming language that also supports scripting.
It is marvelous for scripting,
and you may find yourself replacing all your batch files, shell scripts,
and simple programs with Python scripts.

Python is clean to write.
You will find it easy to read your own code long after you've written it.
A major factor in code readability is that indentation determines scoping in Python.
Here is a script that runs with `python if.py`:

```python
# if.py

response = "yes"
if response == "yes":
    print("affirmative")
    val = 1
#: affirmative
print("continuing...")
#: continuing...
```

The '`#`' denotes a comment that goes until the end of the line,
just like C++ and Java '`//`' comments.
In this book, the first line of an example will be the name of the file containing that example.
That file lives in the chapter's `Examples` subdirectory,
so the above example is `Examples/02_Tour/if.py`.

The `#:` comments are particular to this book.
They show the console output for the example.
The book tooling validates that this output is correct.

A C/C++ `if` requires parentheses around the conditional.
Parentheses are not necessary in Python,
although it won't complain if you use them.

The conditional clause ends with a colon.
This indicates that what follows will be a group of indented statements,
which are the "then" part of the `if` statement.
The `print()` statement sends the result to standard output.
The next line assigns to a variable named `val`.
The subsequent statement is not indented so it is no longer part of the `if`.
Indenting can nest to any level.
Unlike the brace-placement debates of C++ or Java,
there are no options with Python formatting.
The language forces everyone to indent code the same way,
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

```python
# references.py

x = 10        # x names an int
x = "ten"     # The same name now binds to a str
a = [1, 2, 3]
b = a         # b binds to the same list, not a copy
b.append(4)
print(a)       # The same object: a and b
#: [1, 2, 3, 4]
print(a is b)  # Identical objects
#: True
c = a[:]       # A shallow copy
print(a is c, a == c)  # Different object, equal value
#: False True
```

Use `==` to ask whether two objects have equal values.
Use `is` to ask whether two names refer to the same object.
Reserve `is` for `None` and other singletons.

You can assign several names at once,
which makes it easy to swap without a temporary:

```python
# multiple_assignment.py

a, b = 1, 2
a, b = b, a         # Swap, no temporary needed
print(a, b)
#: 2 1
first, *rest = [10, 20, 30, 40]
print(first, rest)
#: 10 [20, 30, 40]
```

Numbers, strings, and tuples are *immutable*,
which means that operations produce new objects rather than changing the original.
Lists, dictionaries, and sets are *mutable*.
Knowing which is which explains when a change is visible through another name,
as with `a` and `b` above.

## Numbers and Arithmetic

Integers have unlimited precision, so they never overflow.
Floating point is the usual IEEE double.
The operators are what you expect, with two worth noting:
`/` always produces a `float`, and `//` is floor division.

```python
# numbers.py

print(7 / 2)    # True division, always a float
#: 3.5
print(7 // 2)   # Floor division
#: 3
print(7 % 2)    # Remainder
#: 1
print(2 ** 10)  # Exponentiation
#: 1024
print(10 ** 30) # A 31-digit int, no overflow
#: 1000000000000000000000000000000
print(abs(-5), round(3.14159, 2))
#: 5 3.14
total = 0
total += 5      # Augmented assignment, like other languages
print(total)
#: 5
```

Python has no `++` or `--`; use `+= 1` and `-= 1`.
Each arithmetic operator has an augmented-assignment form: `+=`, `-=`, `*=`,
`/=`, `//=`, `%=`, and `**=`.

A `bool` is a subtype of `int`, so `True` equals `1` and `False` equals `0`.
This can be useful for counting.

Integers also support the bitwise and shift operators,
each with a matching augmented form (`&=`, `|=`, `^=`, `<<=`, `>>=`):

```python
# bitwise.py
# Binary literals (starting with 0b) make the bit patterns readable
print(bin(0b1100 & 0b1010))  # AND, bits set in both
#: 0b1000
print(bin(0b1100 | 0b1010))  # OR, bits set in either
#: 0b1110
print(bin(0b1100 ^ 0b1010))  # XOR, bits set in exactly one
#: 0b110
print(bin(~0b1100))          # NOT, inverts every bit
#: -0b1101
print(bin(1 << 4))           # Left shift, same as 1 * 2 ** 4
#: 0b10000
print(bin(64 >> 2))          # Right shift, same as 64 // 2 ** 2
#: 0b10000

flags = 0
flags |= 0b0010         # Set bits with the augmented form
flags |= 0b1000
print(bin(flags))
#: 0b1010
```

The `bin()` function converts an integer to a binary string for display.

Python reserves one further operator, `@` (with `@=` to match),
for matrix multiplication.
The built-in numeric types do not implement it but array libraries such as NumPy do.

## Booleans, None, and Truthiness

`None` is Python's single "no value" object, like `null` elsewhere.
It is the default return value of a function that returns nothing.

You can test any object in a boolean context.
Numbers are false when zero, containers are false when empty,
and `None` is always false.
Everything else is true.
This is *truthiness*,
and it allows `if items:` instead of `if len(items) != 0:`.

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
    print("empty")        # An empty list is falsy
#: empty

name = "" or "default"    # 'or' returns the first truthy operand
print(name)               # default
#: default
```

`repr()` returns a value's unambiguous representation,
so the empty string shows as `''` and not as blank.

`and` and `or` short-circuit and return one of their operands,
not a coerced boolean.
`x or default` is a common way to supply a fallback.

## Strings

Single or double quotes create strings.
If you surround a string with double quotes,
you can embed single quotes and vice versa:

```python
# strings.py

print("That isn't a horse")
print('You are not a "Viking"')
print("""
You're just pounding two
coconut halves together.
""")
print('''
"Oh no!" He exclaimed.
"It's the blancmange!"
''')
print(r'c:\python\lib\utils')
#: That isn't a horse
#: You are not a "Viking"
#:
#: You're just pounding two
#: coconut halves together.
#:
#:
#: "Oh no!" He exclaimed.
#: "It's the blancmange!"
#:
#: c:\python\lib\utils
```

Python's name comes not from the snake but from the Monty Python comedy troupe,
of which the language creator Guido van Rossum is a fan.
Examples often include Python-esque references.

The triple-quote syntax quotes everything, including newlines.
This makes it useful for any block of literal text,
such as an embedded template, a SQL query, or a chunk of HTML,
which you can write out in full without escaping line breaks.

The '`r`' right before a string means "raw."
Python takes backslashes literally, so you don't need to double them.

### f-Strings

Modern Python uses *f-strings*.
Prefix the string with `f` and put expressions in curly braces.
It is readable, fast, and preferred:

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
```

The format spec after a colon controls width, precision, and alignment.

You will also see two older styles in existing code: C's `printf()` syntax,
as in `"val: %d" % val`, and the `str.format()` method,
as in `"val: {}".format(val)`.
Both still work, and both use the same format mini-language.
F-strings replaced them, so this book does not use them.

### Common String Operations

Strings are immutable sequences.
You can use slicing to select portions and `in` to test membership:

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

## Naming Conventions

The basic strategy for naming is to use `snake_case` for identifiers, functions,
and file names.
This means lower case with words separated by underscores,
as in `this_is_snake_case`.

If something represents a constant, use all uppercase letters,
as in `THIS_IS_A_CONSTANT`.

The one exception is class names, which are `CapWords` (Pascal cased),
starting with a capital letter,
without underscores and capitalizing intermediate words.
For example: `ThisIsMyClass`.

A class may instead use `snake_case` when it is documented and used primarily as a callable,
the way a function is.
The standard library does this for `contextlib.suppress` and `contextlib.contextmanager`,
and for builtins like `property` and `staticmethod`.
Reserve it for classes that behave like a function to their users.
The default for a class is still `CapWords`.

[PEP 8](https://www.python.org/dev/peps/pep-0008/#naming-conventions) covers style issues.
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
3.  In `fstrings.py`, add a line that formats `score` with two decimal places instead of zero
    (change `{score:.0f}%` to show `{score:.2f}`),
    and a second line using the debug specifier, `f"{score = }"`.
4.  Rename every identifier in `numbers.py` to camelCase
    (`totalSum` instead of `total`, and so on), then explain,
    using [Naming Conventions](#naming-conventions),
    which renames break the convention and which merely look unfamiliar.
