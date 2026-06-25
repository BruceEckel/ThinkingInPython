# Tour

This chapter and the several that follow give a programmer's tour of Python:
syntax and the scalar types here, then containers, control flow, functions,
modules, classes, and static typing in the chapters after it.
It assumes you have programming experience.
You can find supplementary information in [the official language documentation](https://www.python.org/doc/).

## Scripting vs. Programming

The goal of Python is improved productivity.
The language is designed to aid you as much as possible.
It tries to hinder you as little as possible.
It does not impose arbitrary rules or force a particular set of features.

Python is often referred to as a scripting language,
but scripting languages tend to be limiting,
especially in the scope of the problems that they solve.
Python is a programming language that also supports scripting.
It *is* marvelous for scripting,
and you may find yourself replacing all your batch files, shell scripts,
and simple programs with Python scripts.

Python is clean to write; you will find that it's quite easy to read your own code long after you've written it.
A major factor in code readability is that scoping in Python is determined by indentation.
Here is a script that runs with `python if.py`:

```python
# if.py

response = "yes"
if response == "yes":
    print("affirmative")
    val = 1
## affirmative
print("continuing...")
## continuing...
```

The '`#`' denotes a comment that goes until the end of the line,
just like C++ and Java '`//`' comments.
In this book, the first line of an example will be the name of the file containing that example.
That file can be found in the chapter's `Examples` subdirectory.
So the above example can be found in `Examples/02_Tour/if.py`.

The `##` comments are particular to this book: they show the console output for the example.
The book tooling validates that this output is correct.

In a C/C++ `if`, you are required to use parentheses around the conditional.
Parentheses are not necessary in Python, although it won't complain if you use them.

The conditional clause ends with a colon.
This indicates that what follows will be a group of indented statements,
which are the "then" part of the `if` statement.
The `print()` statement sends the result to standard output,
followed by an assignment to a variable named `val`.
The subsequent statement is not indented so it is no longer part of the `if`.
Indenting can nest to any level, just like curly braces in C++ or Java,
but unlike those languages there is no option (and no argument) about where the braces are placed;
the compiler forces everyone's code to be formatted the same way,
which is one of the main reasons for Python's consistent readability.

Python normally has only one statement per line (you can put more by separating them with semicolons),
thus no terminating semicolon is necessary.

## Variables and References

A variable in Python is a name bound to an object, not a box that holds a value.
Assignment binds a name; it does not copy.
You don't have to declare a variable's type,
and one name can bind to objects of different types over its life.
This is *dynamic typing*.

```python
# references.py

x = 10        # x names an int
x = "ten"     # The same name now binds to a str
a = [1, 2, 3]
b = a         # b binds to the same list, not a copy
b.append(4)
print(a)       # a and b are the same object
## [1, 2, 3, 4]
print(a is b)  # Identical objects
## True
c = a[:]       # A shallow copy
print(a is c, a == c)  # Different object, equal value
## False True
```

Use `==` to ask whether two objects have equal values.
Use `is` to ask whether two names refer to the *same* object.
Reserve `is` for `None` and other singletons.

You can assign several names at once,
which makes it easy to swap without a temporary:

```python
# multiple_assignment.py

a, b = 1, 2
a, b = b, a         # Swap, no temporary needed
print(a, b)
## 2 1
first, *rest = [10, 20, 30, 40]
print(first, rest)
## 10 [20, 30, 40]
```

Numbers, strings, and tuples are *immutable*, which means that
operations produce new objects rather than changing the original.
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
## 3.5
print(7 // 2)   # Floor division
## 3
print(7 % 2)    # Remainder
## 1
print(2 ** 10)  # Exponentiation
## 1024
print(10 ** 30) # A 31-digit int, no overflow
## 1000000000000000000000000000000
print(abs(-5), round(3.14159, 2))
## 5 3.14
total = 0
total += 5      # Augmented assignment, like other languages
print(total)
## 5
```

There is no `++` or `--`; use `+= 1` and `-= 1`.
Each arithmetic operator has an augmented-assignment form: `+=`, `-=`, `*=`,
`/=`, `//=`, `%=`, and `**=`.

A `bool` is a subtype of `int`, so `True` equals `1` and `False` equals `0`.
This can be useful for counting.

Integers also support the bitwise and shift operators,
each with a matching augmented form (`&=`, `|=`, `^=`, `<<=`, `>>=`):

```python
# bitwise.py
# Bitwise and shift operators on integers. Binary literals
# (starting with 0b) make the bit patterns easy to see.
print(0b1100 & 0b1010)  # AND, bits set in both
## 8
print(0b1100 | 0b1010)  # OR, bits set in either
## 14
print(0b1100 ^ 0b1010)  # XOR, bits set in exactly one
## 6
print(~0b1100)          # NOT, inverts every bit
## -13
print(1 << 4)           # left shift, same as 1 * 2 ** 4
## 16
print(64 >> 2)          # right shift, same as 64 // 2 ** 2
## 16

flags = 0
flags |= 0b0010         # Set bits with the augmented form
flags |= 0b1000
print(flags)
## 10
```

Python reserves one further operator, `@` (with `@=` to match),
for matrix multiplication.
The built-in numeric types do not implement it;
array libraries such as NumPy do.

## Booleans, None, and Truthiness

`None` is Python's single "no value" object, like `null` elsewhere.
It is the default return value of a function that returns nothing.

Any object can be tested in a boolean context.
Numbers are false when zero, containers are false when empty,
and `None` is always false.
Everything else is true.
This is *truthiness*,
and it lets you write `if items:` instead of `if len(items) != 0:`.

```python
# truthiness.py

for value in [0, 1, "", "hi", [], [1], None]:
    print(repr(value), "->", bool(value))
## 0 -> False
## 1 -> True
## '' -> False
## 'hi' -> True
## [] -> False
## [1] -> True
## None -> False

if not []:
    print("empty")        # An empty list is falsy
## empty

name = "" or "default"    # 'or' returns the first truthy operand
print(name)               # default
## default
```

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
"It's the blemange!"
''')
print(r'c:\python\lib\utils')
## That isn't a horse
## You are not a "Viking"
##
## You're just pounding two
## coconut halves together.
##
##
## "Oh no!" He exclaimed.
## "It's the blemange!"
##
## c:\python\lib\utils
```

Note that Python was not named after the snake,
but rather the Monty Python comedy troupe,
so examples often include Python-esque references.

The triple-quote syntax quotes everything, including newlines.
This makes it useful for any block of literal text,
such as an embedded template, a SQL query, or a chunk of HTML,
which you can write out in full without escaping line breaks.

The '`r`' right before a string means "raw,"
which takes backslashes literally so you don't have to put in an extra backslash in order to insert a literal backslash.

Python uses C's `printf()` string substitution syntax, but for any string at all.
Follow the string with a '`%`' and the values to substitute:

```python
# string_formatting.py

val = 47
print("The number is %d" % val)
## The number is 47
val2 = 63.4
s = "val: %d, val2: %f" % (val, val2)
print(s)
## val: 47, val2: 63.400000
```

As you can see in the second case,
more than one argument is grouped in parentheses as a tuple (covered in the [next chapter](03_Containers_and_Control_Flow.md#tuples-and-unpacking)).

All the formatting from `printf()` is available,
including control over the number of decimal places and alignment.

### f-Strings

The modern way to build strings is using *f-string*s:
prefix the string with `f` and put expressions in curly braces.
It is readable, fast, and preferred:

```python
# fstrings.py

name = "Alice"
score = 91.5
print(f"{name} scored {score}")
## Alice scored 91.5
print(f"{name} scored {score:.0f}%")
## Alice scored 92%
print(f"{name!r} has {len(name)} letters")
## 'Alice' has 5 letters
total = 7
print(f"{total = }")  # total = 7: useful for debugging
## total = 7
```

The format spec after a colon controls width, precision, and alignment,
the same mini-language the older formatting used.

### Common String Operations

Strings are immutable sequences.
You can use slicing and `in`,
and string methods return new strings rather than changing the original:

```python
# string_methods.py

s = "  Hello, World  "
print(s.strip())
## Hello, World
print(s.strip().lower())
## hello, world
print("World" in s)
## True
print("a,b,c".split(","))
## ['a', 'b', 'c']
print("-".join(["2024", "06", "15"]))
## 2024-06-15
print("ababab".replace("a", "X"))
## XbXbXb
print(s.strip()[0:5])
## Hello
```

## Functions

Functions are defined with `def`, a name, a parameter list, and a colon.
The indented block below is the body, the same indentation rule as `if`.
`return` sends a result back to the caller.
A function with no `return` yields `None`.

```python
# functions.py

def greet(name):
    return f"Hello, {name}"

def banner(text, width=20):  # width has a default value
    line = "*" * width
    return f"{line}\n{text}\n{line}"

print(greet("Alice"))         # Hello, Alice
## Hello, Alice
print(banner("Hi", width=4))  # pass an argument by name
## ****
## Hi
## ****
```

A parameter can have a default, which makes it optional at the call site.
You can also pass arguments by name, as with `width=4`, in any order.
The [Functions](04_Functions.md#default-and-keyword-arguments) chapter covers them in detail.

## Naming Conventions

The basic strategy for naming is to use `snake_case` for identifiers,
functions, and file names.
This means lower case with words separated by underscores,
as in `this_is_snake_case`.

If something represents a constant, use all uppercase letters,
as in `THIS_IS_A_CONSTANT`.

The one exception is class names, which are `CapWords` (pascal cased),
starting with a capital letter,
without underscores and capitalizing intermediate words.
For example: `ThisIsMyClass`.

[PEP 8](https://www.python.org/dev/peps/pep-0008/#naming-conventions) covers style issues.
These can be automatically applied to your code (or at least, pointed out) using tools such as ruff.

### File Names

The name must be a valid identifier: letters, digits, underscores, and cannot start with a digit.

**Modules** (`.py` files): short, all-lowercase, with underscores between words if that improves
readability. This is `snake_case`.

- Good: `result.py`, `cache_singleton.py`, `list_comprehension.py`
- Avoid: `Result.py` (CapWords is for classes), `cacheSingleton.py` (camelCase), `cache-singleton.py`
  (hyphens aren't importable)

**Packages** (directories with `__init__.py`): also short and all-lowercase, but underscores are
discouraged; prefer a single run-together word when you can.

- Good: `mypackage`, and underscores only when they genuinely help (`a_package`)

**Tests** follow pytest's discovery convention: `test_*.py` (or `*_test.py`). This book uses `test_*.py`,
  e.g. `test_result.py`.

Don't shadow standard-library modules. A file named `random.py`, `types.py`, or `weakref.py` can hide
the stdlib one and break imports.
