# Python for Programmers

This book assumes you're an experienced programmer, and it's best if you
have learned Python through another book. For everyone else, this
chapter gives a programmer's introduction to the language.

This is not an introductory book. I assume you have worked through at least one
introductory text, such as *Learning Python* by Mark Lutz, or an equivalent,
before coming to this book.

This brief introduction is for the experienced programmer. You can refer to the
full documentation at <https://docs.python.org/3/>.

In addition, I'll assume you have more than just a grasp of the syntax of
Python. You should have a good understanding of objects and what they're
about, including polymorphism.

On the other hand, by going through this book you're going to learn a *lot*
about object-oriented programming by seeing objects used in many different
situations. If your knowledge of objects is rudimentary, it will get much
stronger in the process of understanding the designs in this book.

## Scripting vs. Programming

Python is often referred to as a scripting language, but scripting languages
tend to be limiting, especially in the scope of the problems that they solve.
Python, on the other hand, is a programming language that also supports
scripting. It *is* marvelous for scripting, and you may find yourself
replacing all your batch files, shell scripts, and simple programs with Python
scripts. But it is far more than a scripting language.

The goal of Python is improved productivity. This productivity comes in many
ways, but the language is designed to aid you as much as possible, while
hindering you as little as possible with arbitrary rules or any requirement
that you use a particular set of features. Python is practical; Python
language design decisions were based on providing the maximum benefits to the
programmer.

Python is very clean to write and especially to read. You will find that it's
quite easy to read your own code long after you've written it, and also to
read other people's code. This is accomplished partially through clean, to-
the-point syntax, but a major factor in code readability is
indentation: scoping in Python is determined by indentation. For example:

```python
# if.py

response = "yes"
if response == "yes":
    print("affirmative")
    val = 1
print("continuing...")
```

The '`\#`' denotes a comment that goes until the end of the line, just like
C++ and Java '`//`' comments.

First notice that the basic syntax of Python is C-ish as you can see in the
`if` statement. But in a C `if`, you would be required to use parentheses
around the conditional, whereas they are not necessary in Python (it won't
complain if you use them anyway).

The conditional clause ends with a colon, and this indicates that what follows
will be a group of indented statements, which are the "then" part of the `if`
statement. In this case, there is a "print" statement which sends the result
to standard output, followed by an assignment to a variable named `val`. The
subsequent statement is not indented so it is no longer part of the `if`.
Indenting can nest to any level, just like curly braces in C++ or Java, but
unlike those languages there is no option (and no argument) about where the
braces are placed; the compiler forces everyone's code to be formatted the
same way, which is one of the main reasons for Python's consistent
readability.

Python normally has only one statement per line (you can put more by
separating them with semicolons), thus no terminating semicolon is necessary.
Even from the brief example above you can see that the language is designed to
be as simple as possible, and yet still very readable.

## Variables and References

A variable in Python is a name bound to an object, not a box that holds a value.
Assignment binds a name; it does not copy. You never declare a variable's type,
and one name can bind to objects of different types over its life. This is
*dynamic typing*.

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

Use `==` to ask whether two objects have equal values. Use `is` to ask whether
two names refer to the *same* object. Reserve `is` for `None` and other
singletons.

You can assign several names at once, which makes swapping a one-liner with no
temporary:

```python
# multiple_assignment.py

a, b = 1, 2
a, b = b, a         # swap, no temporary needed
print(a, b)         # 2 1
first, *rest = [10, 20, 30, 40]
print(first, rest)  # 10 [20, 30, 40]
```

Numbers, strings, and tuples are *immutable*: operations produce new objects
rather than changing the original. Lists, dictionaries, and sets are *mutable*.
Knowing which is which explains when a change is visible through another name, as
with `a` and `b` above.

## Numbers and Arithmetic

Integers have unlimited precision, so they never overflow. Floating point is the
usual IEEE double. The operators are what you expect, with two worth noting: `/`
always produces a float, and `//` is floor division.

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

There is no `++` or `--`; use `+= 1`. A `bool` is a subtype of `int`, so `True`
equals `1` and `False` equals `0`, which is occasionally handy for counting.

## Booleans, None, and Truthiness

`None` is Python's single "no value" object, like `null` elsewhere. It is the
default return value of a function that returns nothing.

Any object can be tested in a boolean context. Numbers are false when zero,
containers are false when empty, and `None` is always false. Everything else is
true. This is *truthiness*, and it lets you write `if items:` instead of
`if len(items) != 0:`.

```python
# truthiness.py

for value in [0, 1, "", "hi", [], [1], None]:
    print(repr(value), "->", bool(value))

items = []
if not items:
    print("empty")        # an empty list is falsy

name = "" or "default"    # 'or' returns the first truthy operand
print(name)               # default
```

`and` and `or` short-circuit and return one of their operands, not a coerced
boolean. `x or default` is a common way to supply a fallback.

## Built-In Containers

With languages like C++ and Java, containers are add-on libraries and not
integral to the language. In Python, the essential nature of containers for
programming is acknowledged by building them into the core of the language:
both lists and associative arrays (a.k.a. maps, dictionaries, hash tables) are
fundamental data types. This adds much to the elegance of the language.

In addition, the `for` statement automatically iterates through lists rather
than just counting through a sequence of numbers. This makes a lot of sense
when you think about it, since you're almost always using a `for` loop to step
through an array or a container. Python formalizes this by automatically
making `for` use an iterator that works through a sequence. Here's an example:

```python
# list.py

list = [ 1, 3, 5, 7, 9, 11 ]
print(list)
list.append(13)
for x in list:
    print(x)
```

The first line creates a list. You can print the list and it will look exactly
as you put it in (in contrast, remember that I had to create a special
`Arrays2` class in *Thinking in Java* in order to print arrays in Java). Lists
are like Java containers: you can add new elements to them (here, `append()`
is used) and they will automatically resize themselves. The `for` statement
creates an iterator `x` which takes on each value in the list.

You can create a list of numbers with the `range()` function, so if you really
need to imitate C's `for`, you can.

Notice that there aren't any type declarations: the object names simply
appear, and Python infers their type by the way that you use them. It's as if
Python is designed so that you only need to press the keys that absolutely
must. You'll find after you've worked with Python for a short while that
you've been using up a lot of brain cycles parsing semicolons, curly braces,
and all sorts of other extra verbiage that was demanded by your non-Python
programming language but didn't actually describe what your program was
supposed to do.

### Lists and Slicing

A list holds an ordered, mutable sequence of any objects. Indexing starts at
zero, and negative indices count from the end. A *slice* `[start:stop:step]`
copies a subrange, with `stop` excluded:

```python
# slicing.py

xs = [10, 20, 30, 40, 50]
print(xs[0], xs[-1])  # 10 50: first and last
print(xs[1:3])        # [20, 30]: the stop index is excluded
print(xs[:2])         # [10, 20]: from the start
print(xs[2:])         # [30, 40, 50]: to the end
print(xs[::2])        # [10, 30, 50]: every second item
print(xs[::-1])       # [50, 40, 30, 20, 10]: reversed
xs.append(60)
xs.insert(0, 5)
print(len(xs), 30 in xs)  # 7 True
```

Slicing works on any sequence, including strings and tuples.

### Tuples and Unpacking

A tuple is an immutable sequence. The comma makes the tuple, not the
parentheses. Tuples are the natural way to return several values from a function
and to group values for unpacking:

```python
# tuples.py

point = (3, 4)
x, y = point        # unpacking
print(x, y)         # 3 4
single = (42,)      # a one-element tuple needs the trailing comma
print(len(single))  # 1

def min_max(values):
    return min(values), max(values)  # returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)    # 1 9
```

### Dictionaries

A dictionary maps keys to values, with fast lookup. Keys must be immutable.

```python
# dictionaries.py

ages = {"Alice": 30, "Bob": 25}
print(ages["Alice"])       # 30
ages["Carol"] = 41         # add or update
print("Bob" in ages)       # True: membership tests the keys
print(ages.get("Dan", 0))  # 0: a default when the key is missing
for name, age in ages.items():
    print(name, age)
```

Reach for `dict.get()` to avoid a `KeyError` when a key might be absent.

### Sets

A set is an unordered collection of unique items, with fast membership tests and
the usual set algebra:

```python
# sets.py

a = {1, 2, 3, 3}  # duplicates collapse
b = {3, 4, 5}
print(a)          # {1, 2, 3}
print(a & b)      # {3}: intersection
print(a | b)      # {1, 2, 3, 4, 5}: union
print(a - b)      # {1, 2}: difference
print(2 in a)     # True
```

## Control Flow

You already saw `if`. Add `elif` for chained tests, and note that Python's
comparison operators chain the way they do in mathematics:

```python
# control_flow.py

def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"

print(classify(-3), classify(0), classify(7))

x = 5
print(0 < x < 10)  # True: chained comparison
grade = "pass" if x >= 3 else "fail"  # conditional expression
print(grade)
```

A `while` loop runs until its condition is false. `break` leaves the loop and
`continue` skips to the next iteration:

```python
# while_loop.py

n = 27
steps = 0
while n != 1:  # the Collatz sequence
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    steps += 1
print(steps, "steps")
```

For iteration, `for` walks any sequence directly. Use `range()` for counting,
`enumerate()` when you also need the index, and `zip()` to walk two sequences
together:

```python
# looping.py

for i in range(3):  # 0, 1, 2
    print(i, end=" ")
print()
names = ["Alice", "Bob", "Carol"]
for index, name in enumerate(names):
    print(index, name)
scores = [88, 91, 79]
for name, score in zip(names, scores):
    print(name, score)
```

### Pattern Matching

The `match` statement compares a value against structural patterns. It is more
than a C `switch`: a pattern can destructure a value and bind its parts. (The
`f"..."` strings below are *f-strings*, covered under Strings.)

```python
# match_command.py

def run(command):
    match command.split():
        case ["go", direction]:
            return f"moving {direction}"
        case ["quit"]:
            return "goodbye"
        case _:
            return "unknown command"

print(run("go north"))
print(run("quit"))
print(run("dance"))
```

## Errors and Exceptions

Python signals an error by *raising* an exception, which propagates up until a
`try`/`except` handles it. Catch specific exception types, not everything:

```python
# exceptions.py

def parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None

print(parse_int("42"))    # 42
print(parse_int("oops"))  # None

def checked_divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b

try:
    checked_divide(1, 0)
except ValueError as e:
    print("caught:", e)
finally:
    print("finally always runs")
```

An `except` clause names the exception type. An optional `else` runs when no
exception was raised, and `finally` always runs, which makes it the place for
cleanup. Python's culture leans on "easier to ask forgiveness than permission":
try the operation and handle the exception, rather than checking every
precondition first.

## Context Managers

A `with` block guarantees that setup and cleanup happen as a pair, even if the
body raises. Opening a file is the canonical case: the file is closed on the way
out, no matter what:

```python
# context_manager.py
import os
import tempfile

path = os.path.join(tempfile.gettempdir(), "demo.txt")
with open(path, "w") as f:
    f.write("one\ntwo\n")  # f.close() happens automatically

with open(path) as f:
    for line in f:
        print(line.strip())
os.remove(path)
```

This is the explicit-finalizer approach mentioned under Cleanup. Anything that
acquires a resource (a file, a lock, a network connection) can be a context
manager.

## Comprehensions

A *comprehension* builds a list, dictionary, or set from another sequence in one
expression, replacing a loop that builds up a result:

```python
# comprehensions_intro.py

squares = [n * n for n in range(5)]           # list comprehension
print(squares)                                # [0, 1, 4, 9, 16]
evens = [n for n in range(10) if n % 2 == 0]  # with a filter
print(evens)                                  # [0, 2, 4, 6, 8]
lengths = {w: len(w) for w in ["a", "bb"]}    # dict comprehension
print(lengths)                                # {'a': 1, 'bb': 2}
```

This is such a core idiom that it has its own chapter,
[Comprehensions](07_Comprehensions.md), which also covers generator expressions
and the functional tools `map()` and `filter()`.

## Naming Conventions

Although naming conventions are more detailed than this (you can find them in
[PEP 8](https://www.python.org/dev/peps/pep-0008/#naming-conventions)), the
basic strategy for naming is to use "snake-case" for identifiers, functions
and file names. This means lower case with words separated by underscores, as
in `this_is_snake_case`.

If something represents a constant, you use all uppercase letters, as in
`THIS_IS_A_CONSTANT`.

The one exception is class names, which are "pascal-cased," starting with a
capital letter, without underscores and capitalizing intermediate words. For
example: `ThisIsMyClass`.

[PEP 8]([PEP 8](https://www.python.org/dev/peps/pep-0008/) covers all manner
of style issues. These can be automatically applied to your code (or at least,
pointed out) using tools such as
[AutoPEP8](https://pypi.python.org/pypi/autopep8) or
[YAPF](https://github.com/google/yapf).

**Note**: File names have no relationship to what they contain: you can name
them whatever makes sense to you.

## Functions

To create a function in Python, you use the `def` keyword, followed by the
function name and argument list, and a colon to begin the function body. Here
is the first example turned into a function:

```python
# my_function.py

def my_function(response):
    val = 0
    if response == "yes":
        print("affirmative")
        val = 1
    print("continuing...")
    return val

print(my_function("no"))
print(my_function("yes"))
```

Notice there is no type information in the function signature: all it
specifies is the name of the function and the argument identifiers, but no
argument types or return types. Python is a *structurally-typed* language,
which means it puts the minimum possible requirements on typing. For example,
you could pass and return different types from the same function:

```python
# different_returns.py

def different_returns(arg):
    if arg == 1:
        return "one"
    if arg == "one":
        return True

print(different_returns(1))
print(different_returns("one"))
```

The only constraints on an object that is passed into the function are that
the function can apply its operations to that object, but other than that, it
doesn't care. Here, the same function applies the '`+`' operator to integers
and strings:

```python
# sum.py

def sum(arg1, arg2):
    return arg1 + arg2

print(sum(42, 47))
print(sum('spam ', "eggs"))
```

When the operator '`+`' is used with strings, it means concatenation (yes,
Python supports operator overloading, and it does a nice job of it).

### Default and Keyword Arguments

Parameters can have defaults, and callers can pass arguments by name in any
order. Keyword arguments make a call self-documenting:

```python
# default_args.py

def connect(host, port=5432, timeout=30):
    return f"{host}:{port} (timeout {timeout}s)"

print(connect("db.example.com"))                 # uses both defaults
print(connect("db.example.com", timeout=5))      # skip to a keyword
print(connect(port=80, host="web.example.com"))  # any order by name
```

A default value is evaluated once, when the function is defined, not on each
call. A *mutable* default is therefore shared across calls, a classic trap:

```python
# mutable_default.py

def bad_append(item, target=[]):  # the same list every call
    target.append(item)
    return target

print(bad_append(1))  # [1]
print(bad_append(2))  # [1, 2]: surprise, the default kept the 1

def good_append(item, target=None):
    if target is None:
        target = []               # a fresh list each call
    target.append(item)
    return target

print(good_append(1))  # [1]
print(good_append(2))  # [2]
```

### Variable Argument Lists

A `*args` parameter collects extra positional arguments into a tuple, and
`**kwargs` collects extra keyword arguments into a dictionary:

```python
# var_args.py

def report(label, *values, **options):
    print(label, values, options)

report("nums", 1, 2, 3)                       # nums (1, 2, 3) {}
report("point", 3, 4, color="red", size=10)   # extras land in options
```

The same `*` and `**` *unpack* a sequence or dictionary back into arguments at a
call site, the mirror image of collecting them.

### Lambdas

A `lambda` is a small anonymous function written as a single expression. It is
handy for passing behavior to functions like `sorted()`:

```python
# lambdas.py

words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=lambda w: len(w)))  # sort by length
square = lambda n: n * n                     # usually prefer def
print(square(9))                             # 81
```

## Strings

The above example also shows a little bit about Python string handling, which
is the best of any language I've seen. You can use single or double quotes to
represent strings, which is very nice because if you surround a string with
double quotes, you can embed single quotes and vice versa:

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

Note that Python was not named after the snake, but rather the Monty Python
comedy troupe, and so examples are virtually required to include Python-esque
references.

The triple-quote syntax quotes everything, including newlines. This makes it
useful for any block of literal text, such as an embedded template, a SQL query,
or a chunk of HTML, which you can write out in full without escaping line breaks.

The '`r`' right before a string means "raw," which takes the backslashes
literally so you don't have to put in an extra backslash in order to insert a
literal backslash.

Substitution in strings is exceptionally easy, since Python uses C's
`printf()` substitution syntax, but for any string at all. You simply follow
the string with a '`%`' and the values to substitute:

```python
# string_formatting.py

val = 47
print("The number is %d" % val)
val2 = 63.4
s = "val: %d, val2: %f" % (val, val2)
print(s)
```

As you can see in the second case, if you have more than one argument
you surround them in parentheses (this forms a *tuple*, which is a list
that cannot be modified; you can also use regular lists for multiple
arguments, but tuples are typical).

All the formatting from `printf()` is available, including control
over the number of decimal places and alignment. Python also has very
sophisticated regular expressions.

### f-Strings

The `%` syntax above still works, but the modern way to build strings is the
*f-string*: prefix the string with `f` and put expressions in braces. It is
readable and fast, and it is what you should reach for:

```python
# fstrings.py

name = "Alice"
score = 91.5
print(f"{name} scored {score}")             # Alice scored 91.5
print(f"{name} scored {score:.0f}%")        # Alice scored 92%
print(f"{name!r} has {len(name)} letters")  # 'Alice' has 5 letters
total = 7
print(f"{total = }")                         # total = 7: handy when debugging
```

The format spec after a colon controls width, precision, and alignment, the same
mini-language the older formatting used.

### Common String Operations

Strings are immutable sequences, so slicing and `in` work on them, and the
methods return new strings rather than changing the original:

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

## Imports, Namespaces and Packages

Each Python file is a *module* that you can use inside another Python file by
*importing* it. If the file is in the same directory, you can simply use an
`import` statement:

```python
# module.py

def useful_function():
    return "Use this elsewhere!"
```

```python
# use_module.py
import module

print("'module' imported")

if __name__ == "__main__":
    print(module.useful_function())
```

When you import a module, it creates a *namespace* within the importing file.
This automatically prevents name clashes between the names in the imported
module and the local names. To call `useful_function()`, you must *qualify* it
with the name of the module: `module.useful_function()`.

The code at the end of the file starts with an `if` clause which checks to see
if something called `__name__` is equivalent to `__main__`. In Python, any
identifier that begins and ends with double underscores is special in some
way. The reason for the `if` is that any file can also be used as a library
module within another program (modules are described shortly). In that case,
you just want the classes defined, but you don't want the code at the bottom
of the file to be executed. This particular `if` statement is only true when
you are running this file directly. That is, `__name__` is `__main__` when you
use the command line:

```
python use_module.py
```

However, if this file is imported as a module into another program, `__name__`
will not be `__main__`, so the `__main__` code is not executed:

```python
# import_module.py
```

If you run `python import_module.py`, you should only see `'module' imported`
as the result.

If you want to bring a name into the current namespace, you can do so using
the `from` keyword:

```python
# using_from.py
from module import useful_function

if __name__ == "__main__":
    print(useful_function())
```

You can change the namespace of a module during an import using the `as`
keyword:

```python
# using_as.py
import module as m

if __name__ == "__main__":
    print(m.useful_function())
```

### Packages

As your programs get larger you'll want to further organize your code into
*packages*. A package is a directory (and its own namespace, which has the
name of that directory) that can contain multiple modules.

To make something a package, you put a special file named `__init__.py` in
that directory. Except in special cases, this file is empty; it is only there
to flag the directory as a package.^[People are often confused by the name
`__init__.py`. In hindsight, it might have been better to have named the file
`__package__.py`.]

To demonstrate, we'll create a directory called `a_package` and give it an
`__init__.py` containing nothing but a comment:

```python
# a_package/__init__.py
```

Now we'll add two modules to the package:

```python
# a_package/module1.py

def function1():
    return "function1 in module1 in a_package"
```

```python
# a_package/module2.py

def function2():
    return "function2 in module2 in a_package"
```

To import a module from a package, you must qualify it with the package name:

```python
# using_packages.py
import a_package.module1
import a_package.module2

print(a_package.module1.function1())
print(a_package.module2.function2())
```

You can also name the package with `from`:

```python
# from_packages.py
from a_package import module1, module2

print(module1.function1())
print(module2.function2())
```

Here you no longer need to qualify the module with the package name.

Finally, you can bring specific functions into the namespace by
naming both the package and the module:

```python
# no_qualification.py
from a_package.module1 import function1
from a_package.module2 import function2

print(function1())
print(function2())
```

We can even put a second package underneath the first one:

```python
# a_package/b_package/__init__.py
```

```python
# a_package/b_package/module3.py

def function3():
    return "function3 in module3 in b_package"
```

To import `module3` we must specify both packages:

```python
# two_levels.py
from a_package.b_package import module3

print(module3.function3())
```

This example is primarily useful to show you the consistency of the package
model. You will rarely do anything like this, probably only with an especially
complex project.

### `PYTHONPATH`

What if your module or package isn't placed in the same directory as the Python file
that's doing the importing? The original (and now semi-deprecated) solution to this
was to set an environment variable called `PYTHONPATH` which tells Python where to
look for modules and packages. `PYTHONPATH` can take multiple paths, and Python will
keep searching through those paths until it finds your module or package (or doesn't,
and reports an error).

`PYTHONPATH` still works, but has been effectively superseded by the *virtual
environment*, which solves much more than just "where are the modules and
packages."

## Classes

Like most things in Python, class definitions use minimal syntax. You start
with the `class` keyword followed by the class name and a colon. Inside the
(indented) class body you use `def` to create methods. Here's a simple class:

```python
# simple_class.py

class Simple:
    def __init__(self, str):
        print("Inside the Simple constructor")
        self.s = str
    # Two methods:
    def show(self):
        print(self.s)
    def show_msg(self, msg):
        print(msg + ':',
        self.show()) # Calling another method

if __name__ == "__main__":
    # Create an object:
    x = Simple("constructor argument")
    x.show()
    x.show_msg("A message")
```

Both methods have `self` as their first argument. C++ and Java both have a
hidden first argument in their class methods, which points to the object that
the method was called for and can be accessed using the keyword `this`. Python
methods also use a reference to the current object, but when you are
*defining* a method you must explicitly specify the reference as the first
argument. Traditionally, the reference is called `self` but you could use any
identifier you want (if you do not use `self` you will probably confuse a lot
of people, however). To refer to fields in the object or other methods in the
object, you must use `self` in the expression. However, when you call a method
for an object as in `x.show()`, you do not hand it the reference to the
object; *that* is done for you.

The first method, `__init__()`, defines the constructor (again, the double
underscores indicate a special name), which is automatically called when the
object is created, just like in C++ and Java. However, at the bottom of the
example you can see that the creation of an object looks just like a function
call using the class name. Python's spare syntax makes you realize that the
`new` keyword isn't really necessary in C++ or Java, either.

In C++ or Java you declare object level fields inside the class body but
outside of the methods. Something that's a little surprising at first is that
you do not declare them this way in Python. To create an object field, you
just name it, using `self`, inside one of the methods (usually in the
constructor, but not always), and space is created when that method is run.
This seems a little strange coming from C++ or Java where you must decide
ahead of time how much space your object is going to occupy, but it turns out
to be a very flexible way to program. If you declare fields using the C++/Java
style, they implicitly become class level fields (similar to the static fields
in C++/Java)

### Inheritance

Because Python is dynamically typed, it doesn't really care about
interfaces -all it cares about is applying operations to objects (in
fact, Java's `interface` keyword would be wasted in Python). This
means that inheritance in Python is different from inheritance in C++ or
Java, where you often inherit simply to establish a common interface. In
Python, the only reason you inherit is to inherit an implementation, to
re-use the code in the base class.

To inherit from a class, you must tell Python to bring that class into your
new file. Python controls its name spaces as aggressively as Java does, and in
a similar fashion (albeit with Python's penchant for simplicity). Every time
you create a file, you implicitly create a module (which is like a package in
Java) with the same name as that file. Thus, no `package` keyword is needed in
Python. When you want to use a module, you just say `import` and give the name
of the module. Python searches the PYTHONPATH in the same way that Java
searches the CLASSPATH (but for some reason, Python doesn't have the same
kinds of pitfalls as Java does) and reads in the file. To refer to any of the
functions or classes within a module, you give the module name, a period, and
the function or class name. If you don't want the trouble of qualifying the
name, you can say

```python
from module import name(s)
```

Where "name(s)" can be a list of names separated by commas.

You inherit a class (or classes, since Python supports multiple inheritance)
by listing the name(s) of the class inside parentheses after the name of
the inheriting class. Note that the `Simple` class, which resides in
the file (and thus, module) named `simple_class` is brought into this
new name space using an `import` statement:

```python
# simple2.py
from simple_class import Simple


class Simple2(Simple):
    def __init__(self, str):
        print("Inside Simple2 constructor")
        # You must explicitly call
        # the base-class constructor:
        Simple.__init__(self, str)
    def display(self):
        self.show_msg("Called from display()")
    # Overriding a base-class method
    def show(self):
        print("Overridden show() method")
        # Calling a base-class method from inside
        # the overridden method:
        Simple.show(self)

class Different:
    def show(self):
        print("Not derived from Simple")

if __name__ == "__main__":
    x = Simple2("Simple2 constructor argument")
    x.display()
    x.show()
    x.show_msg("Inside main")
    def f(obj): obj.show() # One-line definition
    f(x)
    f(Different())
```

`Simple2` is inherited from `Simple`, and in the constructor, the
base-class constructor is called. In `display()`, `show_msg()` can
be called as a method of `self`, but when calling the base-class
version of the method you are overriding, you must fully qualify the
name and pass `self` in as the first argument, as shown in the
base-class constructor call. This can also be seen in the overridden
version of `show()`.

In `__main__`, you will see (when you run the program) that the
base-class constructor is called. You can also see that the `show_msg(
)` method is available in the derived class, just as you would expect
with inheritance.

The class `Different` also has a method named `show()`, but this
class is not derived from `Simple`. The `f()` method defined in
`__main__` demonstrates weak typing: all it cares about is that
`show()` can be applied to `obj`, and it doesn't have any other
type requirements. You can see that `f()` can be applied equally to
an object of a class derived from `Simple` and one that isn't, without
discrimination. If you're a C++ programmer, you should see that the
objective of the C++ `template` feature is exactly this: to provide
weak typing in a strongly-typed language. Thus, in Python you
automatically get the equivalent of templates, without having to learn
that particularly difficult syntax and semantics.

### Properties

In Java or C++ you often write getters and setters up front, in case you later
need logic behind a field. Python lets you expose a plain attribute and convert
it to a computed one later, without changing the calling code, using
`@property`:

```python
# properties.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # a plain attribute

    @property
    def area(self):           # used like an attribute, not a call
        return 3.14159 * self.radius ** 2

c = Circle(10)
print(c.radius)  # 10
print(c.area)    # 314.159: no parentheses, it is a property
```

Because the change is invisible at the call site, you do not write getters and
setters in advance. Add a property only when you actually need the logic.

### String Representation

Two special methods control how an object prints. `__str__` is the readable form
for users, and `__repr__` is the unambiguous form for developers, shown in the
REPL and inside containers:

```python
# representation.py

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(p)       # Point(3, 4): falls back to __repr__
print([p, p])  # [Point(3, 4), Point(3, 4)]
```

Define `__repr__` on classes you debug. Methods named with double underscores are
*special methods*, and they hook your class into the language's operators and
built-in functions.

### Static and Class Methods

A method that ignores `self` can be a `@staticmethod`. One that needs the class
rather than an instance can be a `@classmethod`, which receives the class as its
first argument, conventionally `cls`:

```python
# class_methods.py

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, f):    # an alternative constructor
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def is_freezing(celsius):        # needs no self or cls
        return celsius <= 0

t = Temperature.from_fahrenheit(212)
print(round(t.celsius))             # 100
print(Temperature.is_freezing(-4))  # True
```

For classes that are mostly a bundle of typed data, the
[Data Classes as Types](04_Data_Classes_as_Types.md) chapter shows a much shorter
path that writes the constructor and `__repr__` for you.

## Initialization and Cleanup

A constructor sets up an object, and you saw `__init__()` do that above. Two
parts of an object's lifetime surprise programmers coming from C++ or Java: how
class-level attributes behave, and how and when objects are cleaned up.

### Class Attributes Are Not Default Values

A field declared in the class body, outside any method, is a *class attribute*. It
is easy to misread one as a per-object default value. It is not. There is one
shared variable for the whole class, and an instance variable of the same name
*shadows* it. This trips up programmers coming from C++ or Java, where storage for
such a field is allocated per object before the constructor runs.

Simple use looks exactly like a default value, which is the trap:

```python
# class_attribute_confusion.py
# A class attribute looks like a per-object default, but it is one
# shared value, and an instance variable of the same name shadows it.
class Stars:
    rating = 5  # One value, shared by the whole class.


a = Stars()
b = Stars()
print(a.rating, b.rating)  # 5 5: both read the class attribute
a.rating = 1  # Assigning makes an instance variable on a.
print(a.rating, b.rating)  # 1 5: a shadows it, b sees the class
Stars.rating = 9  # Now change the shared class attribute.
print(a.rating, b.rating)  # 1 9: a keeps its own, b follows
```

The reason is that an instance and its class each have their own attribute
dictionary. Reading an attribute checks the instance first, then falls back to
the class. Assigning always writes to the instance, creating the variable there
the first time:

```python
# inside_objects.py
# An instance and its class each have their own attribute dictionary.
# Reading falls back to the class; assigning writes to the instance.
class A:
    x = 100  # class attribute


a = A()
print(vars(A)["x"])  # 100: the attribute lives in the class dict
print(vars(a))  # {}: the instance has no attributes yet
a.x = 1
print(vars(a))  # {'x': 1}: assignment created it on the instance
```

So a class attribute behaves like a default only until someone assigns to the
instance. Changing the class attribute then reaches into every object that has
not shadowed it yet. That produces bugs that surface far from their cause.

For real per-object defaults, write a constructor with default arguments, or use
a `@dataclass`, which turns the class-attribute syntax into exactly that. Each
object then gets its own storage:

```python
# real_defaults.py
# For per-object defaults, write a constructor, or use a @dataclass,
# which turns the class-attribute syntax into exactly that.
from dataclasses import dataclass


class A:
    def __init__(self, x: int = 100) -> None:
        self.x = x  # an instance variable, one per object


@dataclass
class B:
    x: int = 100  # a constructor default, not a shared value


if __name__ == "__main__":
    a = A()
    a.x = -1
    print(a.x, A().x)  # -1 100: a's change does not leak
    print(B().x, B(7).x)  # 100 7
```

The [Data Classes as Types](04_Data_Classes_as_Types.md) chapter builds on this:
a `@dataclass` reads the class-attribute declarations as a template and generates
a constructor from them.

### Cleanup

Python manages memory for you, so most objects need no explicit cleanup. When an
object owns an outside resource (a file, a socket, a lock), you still have to
release it. Python calls an object's `__del__()` method when it collects the
object, which looks like the place for that work:

```python
# cleanup.py
class Counter:
    count: int = 0   # Number of objects of this class

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, 'created')
        Counter.count += 1

    def __del__(self) -> None:
        print(self.name, 'deleted')
        Counter.count -= 1
        if Counter.count == 0:
            print('Last Counter object deleted')
        else:
            print(Counter.count, 'Counter objects remaining')


x = Counter("First")
del x
```

This runs, but leaning on `__del__()` is fragile. Its timing is not guaranteed,
and at interpreter shutdown the globals it refers to may already be gone. The
Python documentation warns:

> Warning: Due to the precarious circumstances under which __del__()
> methods are invoked, exceptions that occur during their execution are
> ignored, and a warning is printed to sys.stderr instead. Also, when
> __del__() is invoked in response to a module being deleted (e.g.,
> when execution of the program is done), *other globals referenced by
> the __del__() method may already have been deleted*. For this
> reason, __del__() methods should do the absolute minimum needed to
> maintain external invariants.

The explicit `del x` above forces collection while `Counter` is still intact.
Without it the cleanup fires during shutdown, when `Counter` may already be gone.
So `__del__()` should do the minimum, and you should not depend on it. Two
approaches are sturdier.

First, an explicit finalizer such as the `close()` that file objects provide,
called from a `with` block so it runs even when an error interrupts the code.

Second, a weak reference, which tracks an object without keeping it alive. Here a
`WeakValueDictionary` counts live instances, using `id(self)` as each object's
key:

```python
# weak_value.py
from weakref import WeakValueDictionary


class Counter:
    _instances: WeakValueDictionary[int, Counter] = (
        WeakValueDictionary())

    @property
    def count(self) -> int:
        return len(self._instances)

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self
        print(name, 'created')

    def __del__(self) -> None:
        print(self.name, 'deleted')
        if self.count == 0:
            print('Last Counter object deleted')
        else:
            print(self.count, 'Counter objects remaining')


x = Counter("First")
```

The count now falls on its own as objects are collected, with no explicit `del`
required.

## Static Type Checking

The functions earlier in this chapter declare no types. C++ and Java make you
declare the type of everything, and they check those types before the program
runs. Python checks types at run time, only when an operation is actually
attempted, and so far this chapter has leaned on that freedom.

On a small program you do not miss the declarations. On a large one you start to.
A type error that a compiler would have caught now waits until the code runs, and
sometimes that means it waits until a bug report. Python's answer keeps the
freedom and adds the safety net back on your terms. You annotate code with *type
hints*, and a separate tool reads them and tells you, before you run anything,
where the types do not line up. The hints are optional and the checking is a
separate step, so you opt in as much as it pays off and no more.

### Type Hints

A hint annotates a parameter, a return value, or a variable. You write a colon
for parameters and variables, and an arrow for the return type:

```python
# typed_basics.py
# Hints annotate parameters, returns, and variables. They do not
# change how the code runs; they let a checker and an editor reason
# about it.


def repeat(text: str, times: int) -> str:
    return text * times


total: int = 0
for word in ["a", "bb", "ccc"]:
    total += len(word)

print(repeat("ab", 3))
print(total)
```

The container and optional types read the way you say them: `list[int]`,
`dict[str, float]`, `tuple[int, ...]`, and `str | None` for "a string or
nothing." There is almost no new vocabulary to learn for everyday code.

### Gradual Typing

You do not have to annotate everything, or anything. Add hints one function at a
time, and the unannotated code keeps working. The checker treats whatever it
cannot see as the type `Any`, which is compatible with everything, so typed and
untyped code live together. This is *gradual typing*. Start untyped, then add
hints where they earn their keep: the public interfaces, the tricky data, the
code other people depend on. Throwaway scripts you leave bare. When a value
really is dynamic, `Any` is an honest way to say so.

### The Checker: ty

The hints do nothing on their own. You need a tool to read them. This book uses
[`ty`](https://github.com/astral-sh/ty), Astral's fast checker. You point it at
your code:

    ty check

It complains where the hints and the code disagree, and stays quiet when they
agree. Every runnable example in this book is checked this way, and the build
runs `ty` on every change, so the code you read here checks as well as runs.

### Catching Mistakes

The whole point is to hear about a mistake before it ships. Look at this:

```python
def area(width: int, height: int) -> int:
    return width * height

area("3", 4)   # ty: argument of type "str" is not assignable to "int"
```

At run time `area("3", 4)` does not even raise. It returns `"3333"`, because
`"3" * 4` is perfectly good string repetition. The bug would surface much later,
somewhere that expected a number, far from the line that caused it. The checker
points at the call right away.

### Structural Typing with Protocols

This feature fits the way Python already works. Some statically typed languages
make you declare, up front, that a class "is a" `Drawable` by inheriting from it.
That fights duck typing, where what matters is whether an object *has* the methods
you call, not what it inherits from.

A *Protocol* types duck typing directly. You describe a shape, and any object
with that shape satisfies it, with no inheritance:

```python
# protocols.py
# A Protocol types duck typing: any object with the right shape
# qualifies, without inheriting from a base class.
from typing import Protocol


class Drawable(Protocol):
    def draw(self) -> str: ...


class Circle:
    def draw(self) -> str:
        return "circle"


class Square:
    def draw(self) -> str:
        return "square"


def render(shape: Drawable) -> str:   # accepts anything with draw()
    return shape.draw()


print(render(Circle()))
print(render(Square()))
```

`Circle` and `Square` never mention `Drawable`, and both are accepted, because
each has a `draw()` of the right shape. Hand `render()` an object with no
`draw()` and `ty` rejects it. You keep the flexibility of duck typing and gain
the early warning of static types.

### The Hints Are Not Enforced at Run Time

Keep one thing straight: the hints do not change what the program does. Python
stores them and otherwise ignores them. A wrong type that slips past the checker
behaves exactly as it would have with no hints at all. Checking is a separate
step you run, like the tests. If you need a guarantee at run time, you still
write `isinstance`, or reach for a library built to validate data. The hints are
for the tools and for the reader. The run-time behavior is unchanged.

## Useful Techniques

-   You can turn a list into function arguments using `*`:

```python
# unpacking.py
# Turn a sequence into positional arguments with *.
def f(a: int, b: int, c: int) -> None:
    print(a, b, c)


x = [1, 2, 3]
f(*x)
f(*(1, 2, 3))
```

-   You can compose classes using `import`. Here's a method that can be
    reused by multiple classes:

```python
# utility.py


def f(self):
    print("utility.f()!!!")
```

Here's how you compose that method into a class:

```python
# compose.py

class Compose:
    from utility import f


Compose().f()
```

## Notes

Open points and rougher material gathered while writing, kept for a later pass:

- **Base-class constructors.** Be rigorous about calling base-class initializers
  as the first step of your `__init__()` method. Call them with `super()` so that
  changes to the class hierarchy do not break the chain.
- **`__new__()` vs. `__init__()`.** `__init__()` initializes an already-created
  object; `__new__()` creates it. The distinction matters for immutable types and
  some metaprogramming. Expand this with an example.
- **Static fields as a shared singleton.** A modifiable class attribute is shared
  by every instance until one assigns to it. A pattern sometimes seen is lazily
  creating a per-object value on first use, `if not self.something: self.something
  = []`, though normally you would just initialize it in the constructor.
- **Cleanup of locals.** Setting a global to `None` drops a reference. What
  governs `__del__` timing for local variables, and whether assigning `None`
  triggers `__del__` versus Python collecting the object first, deserves a worked
  example.
- **Garbage-collection order.** When `__del__` runs at interpreter shutdown, the
  order in which objects are collected is not deterministic, so an object's
  `__del__` may find other globals already gone.

## Further Reading

- The official Python tutorial: <https://docs.python.org/3/tutorial/>
- The Python Programming FAQ:
  <https://docs.python.org/3/faq/programming.html>
- Planet Python, an aggregator of Python articles from around the web:
  <https://planetpython.org/>
