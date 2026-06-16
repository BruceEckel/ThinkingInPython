# Classes

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

## Inheritance

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

## Properties

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

## String Representation

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

## Static and Class Methods

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
[Data Classes as Types](10_Data_Classes_as_Types.md) chapter shows a much shorter
path that writes the constructor and `__repr__` for you.


## Composing Methods by Import

You can compose classes using `import`. Here is a method that can be reused by
multiple classes:

```python
# utility.py


def f(self):
    print("utility.f()!!!")
```

Here we compose that method into a class:

```python
# compose.py

class Compose:
    from utility import f


Compose().f()
```
