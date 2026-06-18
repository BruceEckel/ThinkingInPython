# A Python Tour

This chapter and the several that follow give a programmer's tour of Python:
syntax and the scalar types here, then containers, control flow, functions,
modules, classes, and static typing in the chapters after it.
It assumes you have programmed before and have worked through an introductory Python text such as *Learning Python* by Mark Lutz.
For the full language reference, see
<https://docs.python.org/3/>.

## Scripting vs. Programming

Python is often referred to as a scripting language,
but scripting languages tend to be limiting,
especially in the scope of the problems that they solve.
Python, on the other hand,
is a programming language that also supports scripting.
It *is* marvelous for scripting,
and you may find yourself replacing all your batch files, shell scripts,
and simple programs with Python scripts.

The goal of Python is improved productivity.
This productivity comes in many ways,
but the language is designed to aid you as much as possible,
while hindering you as little as possible with arbitrary rules or any requirement that you use a particular set of features.

Python is very clean to write and you will find that it's quite easy to read your own code long after you've written it.
A major factor in code readability is that scoping in Python is determined by indentation.
For example:

```python
# if.py

response = "yes"
if response == "yes":
    print("affirmative")
    val = 1
print("continuing...")
```

The '`#`' denotes a comment that goes until the end of the line,
just like C++ and Java '`//`' comments.

But in a C `if`, you would be required to use parentheses around the conditional,
whereas they are not necessary in Python (it won't complain if you use them anyway).

The conditional clause ends with a colon,
and this indicates that what follows will be a group of indented statements,
which are the "then" part of the `if` statement.
In this case, there is a `print` statement which sends the result to standard output,
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
You never declare a variable's type,
and one name can bind to objects of different types over its life.
This is *dynamic typing*.

```python
# references.py

x = 10        # x names an int
x = "ten"     # the same name now binds to a str
a = [1, 2, 3]
b = a         # b binds to the same list, not a copy
b.append(4)
print(a)       # [1, 2, 3, 4]: a and b are the same object
print(a is b)  # True: identical objects
c = a[:]       # a shallow copy
print(a is c, a == c)  # False True: different object, equal value
```

Use `==` to ask whether two objects have equal values.
Use `is` to ask whether two names refer to the *same* object.
Reserve `is` for `None` and other singletons.

You can assign several names at once,
which makes it easy to swap without a temporary:

```python
# multiple_assignment.py

a, b = 1, 2
a, b = b, a         # swap, no temporary needed
print(a, b)         # 2 1
first, *rest = [10, 20, 30, 40]
print(first, rest)  # 10 [20, 30, 40]
```

Numbers, strings, and tuples are *immutable*:
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

print(7 / 2)    # 3.5: true division, always a float
print(7 // 2)   # 3: floor division
print(7 % 2)    # 1: remainder
print(2 ** 10)  # 1024: exponentiation
print(10 ** 30) # a 31-digit int, no overflow
print(abs(-5), round(3.14159, 2))  # 5 3.14
total = 0
total += 5      # augmented assignment, like other languages
print(total)
```

There is no `++` or `--`; use `+= 1` and `-= 1`.
Each arithmetic operator has an augmented-assignment form: `+=`, `-=`, `*=`,
`/=`, `//=`, `%=`, and `**=`.
A `bool` is a subtype of `int`, so `True` equals `1` and `False` equals `0`,
which is occasionally handy for counting.

Integers also support the bitwise and shift operators,
each with a matching augmented form (`&=`, `|=`, `^=`, `<<=`, `>>=`):

```python
# bitwise.py
# Bitwise and shift operators on integers. Binary literals (0b...)
# make the bit patterns easy to see.
print(0b1100 & 0b1010)  # 8: AND, bits set in both
print(0b1100 | 0b1010)  # 14: OR, bits set in either
print(0b1100 ^ 0b1010)  # 6: XOR, bits set in exactly one
print(~0b1100)          # -13: NOT, inverts every bit
print(1 << 4)           # 16: left shift, same as 1 * 2 ** 4
print(64 >> 2)          # 16: right shift, same as 64 // 2 ** 2

flags = 0
flags |= 0b0010         # set bits with the augmented form
flags |= 0b1000
print(flags)            # 10
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

if not []:
    print("empty")        # an empty list is falsy

name = "" or "default"    # 'or' returns the first truthy operand
print(name)               # default
```

`and` and `or` short-circuit and return one of their operands,
not a coerced boolean.
`x or default` is a common way to supply a fallback.

## Strings

You can use single or double quotes to represent strings,
which is very nice because if you surround a string with double quotes,
you can embed single quotes and vice versa:

```python
# strings.py

print("That isn't a horse")
print('You are not a "Viking"')
print("""You're just pounding two
coconut halves together.""")
print('''"Oh no!" He exclaimed.
"It's the blemange!"''')
print(r'c:\python\lib\utils')
```

Note that Python was not named after the snake,
but rather the Monty Python comedy troupe,
and so examples are virtually required to include Python-esque references.

The triple-quote syntax quotes everything, including newlines.
This makes it useful for any block of literal text,
such as an embedded template, a SQL query, or a chunk of HTML,
which you can write out in full without escaping line breaks.

The '`r`' right before a string means "raw,"
which takes the backslashes literally so you don't have to put in an extra backslash in order to insert a literal backslash.

Substitution in strings is exceptionally easy,
since Python uses C's `printf()` substitution syntax, but for any string at all.
You simply follow the string with a '`%`' and the values to substitute:

```python
# string_formatting.py

val = 47
print("The number is %d" % val)
val2 = 63.4
s = "val: %d, val2: %f" % (val, val2)
print(s)
```

As you can see in the second case,
more than one argument is grouped in parentheses as a tuple (covered in the [next chapter](03_Containers_and_Control_Flow.md)).

All the formatting from `printf()` is available,
including control over the number of decimal places and alignment.

### f-Strings

The `%` syntax above still works,
but the modern way to build strings is the *f-string*:
prefix the string with `f` and put expressions in braces.
It is readable, fast, and preferred:

```python
# fstrings.py

name = "Alice"
score = 91.5
print(f"{name} scored {score}")             # Alice scored 91.5
print(f"{name} scored {score:.0f}%")        # Alice scored 92%
print(f"{name!r} has {len(name)} letters")  # 'Alice' has 5 letters
total = 7
print(f"{total = }")  # total = 7: handy when debugging
```

The format spec after a colon controls width, precision, and alignment,
the same mini-language the older formatting used.

### Common String Operations

Strings are immutable sequences, so slicing and `in` work on them,
and the methods return new strings rather than changing the original:

```python
# string_methods.py

s = "  Hello, World  "
print(s.strip())              # 'Hello, World'
print(s.strip().lower())      # 'hello, world'
print("World" in s)           # True
print("a,b,c".split(","))     # ['a', 'b', 'c']
print("-".join(["2024", "06", "15"]))  # '2024-06-15'
print("ababab".replace("a", "X"))      # 'XbXbXb'
print(s.strip()[0:5])         # 'Hello': slicing
```

## Naming Conventions

Although naming conventions are more detailed than this (you can find them in [PEP 8](https://www.python.org/dev/peps/pep-0008/#naming-conventions)),
the basic strategy for naming is to use "snake-case" for identifiers,
functions and file names.
This means lower case with words separated by underscores,
as in `this_is_snake_case`.

If something represents a constant, you use all uppercase letters,
as in `THIS_IS_A_CONSTANT`.

The one exception is class names, which are "pascal-cased,"
starting with a capital letter,
without underscores and capitalizing intermediate words.
For example: `ThisIsMyClass`.

[PEP 8](https://www.python.org/dev/peps/pep-0008/) covers all manner of style issues.
These can be automatically applied to your code (or at least, pointed out) using tools such as [AutoPEP8](https://pypi.python.org/pypi/autopep8) or [YAPF](https://github.com/google/yapf).

**Note**: File names have no relationship to what they contain:
you can name them whatever makes sense to you.
