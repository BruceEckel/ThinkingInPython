Python for Programmers
======================

This book assumes you're an experienced programmer, and it's best if you
have learned Python through another book. For everyone else, this
chapter gives a programmer's introduction to the language.

This is not an introductory book. I am assuming that you have worked
your way through at least *Learning Python* (by Mark Lutz & David
Ascher; Oreilly, 1999) or an equivalent text before coming to this book.

This brief introduction is for the experienced programmer (which is what
you should be if you're reading this book). You can refer to the full
documentation at [www.Python.org](http://www.python.org/doc/).

In addition, I'll assume you have more than just a grasp of the syntax of
Python. You should have a good understanding of objects and what they're
about, including polymorphism.

On the other hand, by going through this book you're going to learn a *lot*
about object-oriented programming by seeing objects used in many different
situations. If your knowledge of objects is rudimentary, it will get much
stronger in the process of understanding the designs in this book.

Scripting vs. Programming
-------------------------

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
indentation---scoping in Python is determined by indentation. For example:

```python
# Py4Prog/if.py

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
braces are placed---the compiler forces everyone's code to be formatted the
same way, which is one of the main reasons for Python's consistent
readability.

Python normally has only one statement per line (you can put more by
separating them with semicolons), thus no terminating semicolon is necessary.
Even from the brief example above you can see that the language is designed to
be as simple as possible, and yet still very readable.

Built-In Containers
-------------------

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
# Py4Prog/list.py

list = [ 1, 3, 5, 7, 9, 11 ]
print(list)
list.append(13)
for x in list:
    print(x)
```

The first line creates a list. You can print the list and it will look exactly
as you put it in (in contrast, remember that I had to create a special
`Arrays2` class in *Thinking in Java* in order to print arrays in Java). Lists
are like Java containers---you can add new elements to them (here, `append()`
is used) and they will automatically resize themselves. The `for` statement
creates an iterator `x` which takes on each value in the list.

You can create a list of numbers with the `range()` function, so if you really
need to imitate C's `for`, you can.

Notice that there aren't any type declarations---the object names simply
appear, and Python infers their type by the way that you use them. It's as if
Python is designed so that you only need to press the keys that absolutely
must. You'll find after you've worked with Python for a short while that
you've been using up a lot of brain cycles parsing semicolons, curly braces,
and all sorts of other extra verbiage that was demanded by your non-Python
programming language but didn't actually describe what your program was
supposed to do.

Naming Conventions
-----------------

Although naming conventions are more detailed than this---you can find them in
[PEP 8](https://www.python.org/dev/peps/pep-0008/#naming-conventions)---the
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

**Note**: File names have no relationship to what they contain---you can name
them whatever makes sense to you.

Functions
---------

To create a function in Python, you use the `def` keyword, followed by the
function name and argument list, and a colon to begin the function body. Here
is the first example turned into a function:

```python
# Py4Prog/my_function.py

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

Notice there is no type information in the function signature---all it
specifies is the name of the function and the argument identifiers, but no
argument types or return types. Python is a *structurally-typed* language,
which means it puts the minimum possible requirements on typing. For example,
you could pass and return different types from the same function:

```python
# Py4Prog/different_returns.py

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
# Py4Prog/sum.py

def sum(arg1, arg2):
    return arg1 + arg2

print(sum(42, 47))
print(sum('spam ', "eggs"))
```

When the operator '`+`' is used with strings, it means concatenation (yes,
Python supports operator overloading, and it does a nice job of it).

Strings
-------

The above example also shows a little bit about Python string handling, which
is the best of any language I've seen. You can use single or double quotes to
represent strings, which is very nice because if you surround a string with
double quotes, you can embed single quotes and vice versa:

```python
# Py4Prog/strings.py

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
particularly useful for doing things like generating web pages (Python is an
especially good CGI language), since you can just triple-quote the entire page
that you want without any other editing.

The '`r`' right before a string means "raw," which takes the backslashes
literally so you don't have to put in an extra backslash in order to insert a
literal backslash.

Substitution in strings is exceptionally easy, since Python uses C's
`printf()` substitution syntax, but for any string at all. You simply follow
the string with a '`%`' and the values to substitute:

```python
# Py4Prog/string_formatting.py

val = 47
print("The number is %d" % val)
val2 = 63.4
s = "val: %d, val2: %f" % (val, val2)
print(s)
```

As you can see in the second case, if you have more than one argument
you surround them in parentheses (this forms a *tuple*, which is a list
that cannot be modified---you can also use regular lists for multiple
arguments, but tuples are typical).

All the formatting from `printf()` is available, including control
over the number of decimal places and alignment. Python also has very
sophisticated regular expressions.

Imports, Namespaces and Packages
--------------------------------

Each Python file is a *module* that you can use inside another Python file by
*importing* it. If the file is in the same directory, you can simply use an
`import` statement:

```python
# Py4Prog/module.py

def useful_function():
    return "Use this elsewhere!"
```

```python
# Py4Prog/use_module.py
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
# Py4Prog/import_module.py
import use_module
```

If you run `python import_module.py`, you should only see `'module' imported`
as the result.

If you want to bring a name into the current namespace, you can do so using
the `from` keyword:

```python
# Py4Prog/using_from.py
from module import useful_function

if __name__ == "__main__":
    print(useful_function())
```

You can change the namespace of a module during an import using the `as`
keyword:

```python
# Py4Prog/using_from.py
import module as m

if __name__ == "__main__":
    print(m.useful_function())
```

### Packages

As your programs get larger you'll want to further organize your code into
*packages*. A package is a directory---and its own namespace, which has the
name of that directory---that can contain multiple modules.

To make something a package, you put a special file named `__init__.py` in
that directory. Except in special cases, this file is empty---it is only there
to flag the directory as a package.^[People are often confused by the name
`__init__.py`. In hindsight, it might have been better to have named the file
`__package__.py`.]

To demonstrate, we'll create a directory called `a_package` and give it an
`__init__.py` containing nothing but a comment:

```python
# Py4Prog/a_package/__init__.py
```

Now we'll add two modules to the package:

```python
# Py4Prog/a_package/module1.py

def function1():
    return "function1 in module1 in a_package"
```

```python
# Py4Prog/a_package/module2.py

def function2():
    return "function2 in module2 in a_package"
```

To import a module from a package, you must qualify it with the package name:

```python
# Py4Prog/using_packages.py
import a_package.module1
import a_package.module2

print(a_package.module1.function1())
print(a_package.module2.function2())
```

You can also name the package with `from`:

```python
# Py4Prog/from_packages.py
from a_package import module1
from a_package import module2

print(module1.function1())
print(module2.function2())
```

Here you no longer need to qualify the module with the package name.

Finally, you can bring specific functions into the namespace by
naming both the package and the module:

```python
# Py4Prog/no_qualification.py
from a_package.module1 import function1
from a_package.module2 import function2

print(function1())
print(function2())
```

We can even put a second package underneath the first one:

```python
# Py4Prog/a_package/b_package/__init__.py
```

```python
# Py4Prog/a_package/b_package/module3.py

def function3():
    return "function3 in module3 in b_package"
```

To import `module3` we must specify both packages:

```python
# Py4Prog/two_levels.py
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
packages." [Virtual Environments] have their own chapter.

Classes
-------

Like most things in Python, class definitions use minimal syntax. You start
with the `class` keyword followed by the class name and a colon. Inside the
(indented) class body you use `def` to create methods. Here's a simple class:

```python
# Py4Prog/simple_class.py

class Simple:
    def __init__(self, str):
        print("Inside the Simple constructor")
        self.s = str
    # Two methods:
    def show(self):
        print(self.s)
    def showMsg(self, msg):
        print(msg + ':',
        self.show()) # Calling another method

if __name__ == "__main__":
    # Create an object:
    x = Simple("constructor argument")
    x.show()
    x.showMsg("A message")
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
object---*that* is done for you.

The first method, `__init__()`, defines the constructor (again, the double
underscores indicate a special name), which is automatically called when the
object is created, just like in C++ and Java. However, at the bottom of the
example you can see that the creation of an object looks just like a function
call using the class name. Python's spare syntax makes you realize that the
`new` keyword isn't really necessary in C++ or Java, either.

In C++ or Java you declare object level fields inside the class body but
outside of the methods. Something that's a little surprising at first is that
you do not declare them this way in Python. To create an object field, you
just name it---using `self`---inside one of the methods (usually in the
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
Python, the only reason you inherit is to inherit an implementation---to
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

You inherit a class (or classes---Python supports multiple inheritance)
by listing the name(s) of the class inside parentheses after the name of
the inheriting class. Note that the `Simple` class, which resides in
the file (and thus, module) named `simple_class` is brought into this
new name space using an `import` statement:

```python
# Py4Prog/simple2.py
from simple_class import Simple

class Simple2(Simple):
    def __init__(self, str):
        print("Inside Simple2 constructor")
        # You must explicitly call
        # the base-class constructor:
        Simple.__init__(self, str)
    def display(self):
        self.showMsg("Called from display()")
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
    x.showMsg("Inside main")
    def f(obj): obj.show() # One-line definition
    f(x)
    f(Different())
```

> Note: you don't have to explicitly call the base-class constructor if the
> argument list is the same. Show example.
>
> Note: (from a Reader) The note above is confusing. Did not understand. IMHO one still
>     needs to invoke the base-class constructor if the argument is the
>     same. Probably one needs to state that in case the base class
>     constructor functionality continues to be adequate for the derived
>     class, then a new constructor need not be declared for the derived
>     class at all.

`Simple2` is inherited from `Simple`, and in the constructor, the
base-class constructor is called. In `display()`, `showMsg()` can
be called as a method of `self`, but when calling the base-class
version of the method you are overriding, you must fully qualify the
name and pass `self` in as the first argument, as shown in the
base-class constructor call. This can also be seen in the overridden
version of `show()`.

In `__main__`, you will see (when you run the program) that the
base-class constructor is called. You can also see that the `showMsg(
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
automatically get the equivalent of templates---without having to learn
that particularly difficult syntax and semantics.

> (Reader) I am not sure if I agree with the remark about templates. One of the
>     big objective of templates has always been type safety along with
>     genericity. What python gives us is the genericity. IMHO the
>     analogy with template mechanism is not appropriate.

Useful Techniques
-----------------

-   You can turn a list into function arguments using `*`:

```python
def f(a,b,c): print a, b, c
    x = [1,2,3]
    f(*x)
    f(*(1,2,3))
```

-   You can compose classes using `import`. Here's a method that can be
    reused by multiple classes:

```python
# Py4Prog/utility.py

def f(self): print "utility.f()!!!"
```

Here's how you compose that method into a class:

```python
# Py4Prog/compose.py

class Compose:
     from utility import f

Compose().f()
```

-   Basic functional programming with `map()` etc.

Note: Suggest Further Topics for inclusion in the introductory chapter

Further Reading
---------------

> Although it is (alas) only for Python 2.7, I still find the [Python Quick
Reference](http://rgruet.free.fr/#QuickRef) to be incredibly useful.

> Python Programming FAQ: <http://www.python.org/doc/faq/programming/>

> Python idioms: <http://jaynes.colorado.edu/PythonIdioms.html>

> Python Tips, Tricks and Hacks: <http://www.siafoo.net/article/52>

> Building a Virtual Environment for Running Python 3:
> <http://pypi.python.org/pypi/virtualenv>

> Excellent Newsfeed Following Python Articles from Everywhere:
> <http://www.planetpython.org/>

Good description of the Python packaging system:
<http://nameless-sorrows.blogspot.com/2009/02/custom-namespacing-system-for-python.html>

How to package:
<http://www.brenelz.com/blog/2009/04/09/writing-a-package-in-python/>

Getters and setters in Python:
<http://eli.thegreenplace.net/2009/02/06/getters-and-setters-in-python/>

The 'with' statement (might require a separate chapter?):
<http://jessenoller.com/2009/02/03/get-with-the-program-as-contextmanager-completely-different/

For people who need more basics than this book has to offer, ShowMeDo
tutorials on Python:
<http://blog.showmedo.com/2009/04/09/python-tutorials-via-learning-paths/>

Importing properties into a class using the 'import' statement:
<http://www.artima.com/weblogs/viewpost.jsp?thread=246483>

Need to talk about abstract base classes (not necessarily here; perhaps
a "classes" chapter (which includes the previous note)
