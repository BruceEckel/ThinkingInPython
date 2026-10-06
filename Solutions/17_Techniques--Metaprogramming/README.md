# Metaprogramming: Solutions

## 1. Tracking leaves through two more generations

> In `init_subclass.py`, add a class `Yellow(Color)` and then `Gold(Yellow)`.
> Predict `Color.registry` after each new class, then confirm.

<details>
<summary>Where to look</summary>

[Self-Registration of Subclasses](../../Chapters/17_Techniques--Metaprogramming.md#self-registration-of-subclasses) shows `__init_subclass__()` running once for every new subclass.
Trace what `__init_subclass__()` adds and what it removes for `Yellow`, then for `Gold`.
Write your predicted sets down before you run the listing.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import ClassVar

class Color:
    registry: ClassVar[set[type[Color]]] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        ...

class Blue(Color):
    pass
class Red(Color):
    pass
class Green(Color):
    pass
class PhthaloBlue(Blue):
    pass
class CeruleanBlue(Blue):
    pass

class Yellow(Color):
    pass

class Gold(Yellow):
    pass
```

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from typing import ClassVar

class Color:
    registry: ClassVar[set[type[Color]]] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Color.registry.add(cls)
        Color.registry -= set(cls.__bases__)

class Blue(Color):
    pass
class Red(Color):
    pass
class Green(Color):
    pass
class PhthaloBlue(Blue):
    pass
class CeruleanBlue(Blue):
    pass

class Yellow(Color):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Green', 'PhthaloBlue', 'Red', 'Yellow']

class Gold(Yellow):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Gold', 'Green', 'PhthaloBlue', 'Red']
```

**Register a new leaf.** Creating `Yellow` adds it to the registry and
removes its only base, `Color`, which is not in the registry, so that
removal changes nothing. `Yellow` stays until a subclass of its own
arrives.

**Drop a base that gains a child.** Creating `Gold` adds it and removes its base, `Yellow`, the
same pruning `PhthaloBlue` and `CeruleanBlue` do to `Blue` earlier.
`__init_subclass__()` runs for every new subclass, so each new
generation adds itself and prunes its parent automatically, with no
edit to `Color`.

</details>
</details>
</details>

## 2. A third `Field` descriptor

> In `set_name.py`, add a third `Field()` attribute, `z`, to `Point`,
> set `p.z = 9`, and confirm `p.__dict__` now also holds `_z`.

<details>
<summary>Where to look</summary>

[A Descriptor That Learns Its Name](../../Chapters/17_Techniques--Metaprogramming.md#a-descriptor-that-learns-its-name) shows `__set_name__()` receiving the attribute name when Python creates the class.
`__set_name__()` runs once per descriptor instance, so a third attribute needs a third `Field()` and no new code.
Compare `p.__dict__` with the attribute names on `Point`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        ...

    def __get__(self, obj: Any,
                owner: type | None = None) -> Any:
        ...

    def __set__(self, obj: Any, value: Any) -> None:
        ...

class Point:
    x = Field()
    y = Field()
    z = Field()
```

<details>
<summary>Solution</summary>

```python
# exercise_2.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage = "_" + name

    def __get__(self, obj: Any,
                owner: type | None = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.storage)

    def __set__(self, obj: Any, value: Any) -> None:
        setattr(obj, self.storage, value)

class Point:
    x = Field()
    y = Field()
    z = Field()

p = Point()
p.x = 3
p.y = 4
p.z = 9
print(p.x, p.y, p.z)
#: 3 4 9
print(p.__dict__)
#: {'_x': 3, '_y': 4, '_z': 9}
```

`z = Field()` leaves the `Field` class as it was.
`__set_name__()` runs once per descriptor, at class-creation time.
Python calls it separately for each of `x`, `y`, and `z`, passing each
one its own attribute name, so `z`'s `Field` instance learns the name
`"z"` and stores under `"_z"`, independently of the other two.

</details>
</details>
</details>

## 3. A third independent singleton class

> In `singleton.py`, add a third class `CSingleton(metaclass=Singleton)` and confirm `c1 = CSingleton(); c2 = CSingleton(); c1 is c2` is `True`,
> while `c1 is a` (comparing across the different singleton classes)
> is `False`.

<details>
<summary>Where to look</summary>

[Intercepting Instance Creation](../../Chapters/17_Techniques--Metaprogramming.md#intercepting-instance-creation) shows a metaclass `__call__()` that caches one instance per class.
The cache is a dictionary keyed by the class, so each class that uses the metaclass gets its own entry.
Add `CSingleton` with the same `metaclass=` argument and compare identities with `is`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import Any, ClassVar

class Singleton(type):
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__[T](
            cls: type[T], *args: Any, **kwargs: Any) -> T:
        ...

class ASingleton(metaclass=Singleton):
    pass
class CSingleton(metaclass=Singleton):
    pass
```

<details>
<summary>Solution</summary>

If you write `super().__call__(*args, **kwargs)`, the usual form in a
metaclass, the script still prints `True` and `False`, but `ty`
reports `invalid-super-argument`. The annotation `cls: type[T]` hides
the fact that `cls` is a `Singleton`, so the type checker cannot
accept `cls` as the second argument of `super()`. The solution calls
`type.__call__(cls, *args, **kwargs)` and keeps the `type[T]`
annotation that types `CSingleton()` as a `CSingleton`.

```python
# exercise_3.py
from typing import Any, ClassVar

class Singleton(type):
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__[T](
            cls: type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in Singleton._instances:
            Singleton._instances[cls] = type.__call__(
                cls, *args, **kwargs)
        return Singleton._instances[cls]

class ASingleton(metaclass=Singleton):
    pass
class CSingleton(metaclass=Singleton):
    pass

a = ASingleton()
c1 = CSingleton()
c2 = CSingleton()
print(c1 is c2)
#: True
print(c1 is a)
#: False
```

**Type the result as the calling class.** The `__call__[T]` signature is the chapter's, and this solution keeps it
rather than simplifying to `-> Any`. It ties the return type to
`cls`, so `CSingleton()` type-checks as a `CSingleton`, and the type
checker still flags a misspelled attribute on the result. Two details follow from
that annotation. `cls: type[T]` hides the fact that `cls` is a
`Singleton`, so the body writes `type.__call__(cls, ...)`, where
`ty` rejects a zero-argument `super()`. For the same reason
the body reads the cache through the class name,
`Singleton._instances`, rather than through `cls`.

**Keep one instance per class.** `Singleton._instances` is a dictionary keyed by the class, so
each class using the `Singleton` metaclass gets its own independent
slot: `ASingleton`'s single instance, `BSingleton`'s single instance
(omitted here, but present in the book), and now `CSingleton`'s.
Calling `CSingleton()` twice returns the same object both times.
`ASingleton` occupies its own key in that dictionary, so its instance
is a separate object.

</details>
</details>
</details>

## 4. Declaring finality with a keyword in the class header

> Extend `final_runtime.py` so a class declares itself final with a keyword in its header,
> `class B(A, final=True):`,
> using the `**kwargs` that `__init_subclass__()` receives.
> Confirm that a non-final sibling of `B` still subclasses freely.

<details>
<summary>Where to look</summary>

[Making a Class Final](../../Chapters/17_Techniques--Metaprogramming.md#making-a-class-final) shows `__init_subclass__()` refusing a subclass at runtime.
Python passes the keyword arguments in a class header to `__init_subclass__()`, so give that method a `final` parameter with a default.
Record each final class in a set on the base, and check `cls.__mro__` when a new subclass appears.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from typing import ClassVar
from exceptions import expected

class A:
    _final: ClassVar[set[type]] = set()

    def __init_subclass__(cls, final: bool = False,
                          **kwargs: object) -> None:
        ...

class B(A, final=True):
    pass

class Open(A):  # A sibling that says nothing
    pass

class Sub(Open):
    pass
```

<details>
<summary>Solution</summary>

If you declare `final` without a default,
`class B(A, final=True):` still builds,
but `class Open(A):` fails with
`TypeError: A.__init_subclass__() missing 1 required positional argument: 'final'`.
The solution gives `final` the default `False`,
so a subclass that is not final can leave the keyword out of its header.

```python
# exercise_4.py
from typing import ClassVar
from exceptions import expected

class A:
    _final: ClassVar[set[type]] = set()

    def __init_subclass__(cls, final: bool = False,
                          **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        for base in cls.__mro__[1:]:
            if base in A._final:
                raise TypeError(
                    f"{base.__name__} is final;"
                    " you cannot subclass it")
        if final:
            A._final.add(cls)

class B(A, final=True):
    pass

class Open(A):  # A sibling that says nothing
    pass

class Sub(Open):
    pass
print(issubclass(Sub, A))
#: True

with expected(TypeError):
    class C(B):
        pass
#: [TypeError] B is final; you cannot subclass it
```

**Accept the header keyword.** The keywords in a class header travel to
`__init_subclass__()`, so `final=True` in `class B(A, final=True):`
arrives as a parameter of the method Python calls when it creates `B`.
Declaring `final` with a default, `final: bool = False`, lets every
other subclass omit it.

**Pass the other keywords up.** The
remaining `**kwargs` go on to `super().__init_subclass__()`, which
turns a misspelled keyword into a `TypeError` instead of a silent
no-op.

**Refuse any descendant of a final class.** The chapter's
`final_runtime.py` hard-codes the refusal into `B`'s own
`__init_subclass__()`. This version moves the decision into a set that
`A` owns, and `A.__init_subclass__()` walks `cls.__mro__` to ask whether
any ancestor declared itself final. A check of the direct bases in
`cls.__bases__` would also refuse every descendant.
`A.__init_subclass__()` refuses the first subclass of a final class as
Python creates that subclass, so no deeper descendant exists. The walk
stays because it states the rule as written, "no final class anywhere
above," in one line.

**Confirm a sibling stays open.** `Open` and `Sub` show that the
rest of the hierarchy still subclasses freely. `A.__init_subclass__()`
raises a `TypeError` only for a class whose `__mro__` holds one of the
classes in `A._final`.

</details>
</details>
</details>

## 5. A small `inspect`-based `describe()` helper

> Using `inspect_tour.py` as a model,
> write a function `describe(func)` that prints a function's name,
> its `inspect.signature()`, and its docstring
> (or `"(no docstring)"` if `inspect.getdoc()` returns `None`),
> then call it on `greet` and on a lambda.

<details>
<summary>Where to look</summary>

[The Core Functions](../../Chapters/17_Techniques--Metaprogramming.md#the-core-functions) lists the `inspect` calls for signatures and docstrings.
Call `inspect.signature()` and `inspect.getdoc()` on the function, and print the function's `__name__`.
Since `getdoc()` returns `None` for a missing docstring, supply the fallback text with `or`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
import inspect
from types import FunctionType

def greet(name: str, loud: bool = False) -> str:
    "Return a greeting."
    ...

def describe(func: FunctionType) -> None:
    ...
```

<details>
<summary>Solution</summary>

If you print `doc` without the `or` fallback, `greet` still shows its
docstring, but the lambda's second line reads `None`, since
`inspect.getdoc()` returns `None` for a callable with no docstring.
The type checker accepts that version, because `print()` takes any
object. The solution writes `doc or "(no docstring)"`, which replaces
a missing docstring with the message.

```python
# exercise_5.py
import inspect
from types import FunctionType

def greet(name: str, loud: bool = False) -> str:
    "Return a greeting."
    text = f"Hello, {name}"
    return text.upper() if loud else text

def describe(func: FunctionType) -> None:
    doc = inspect.getdoc(func)
    sig = inspect.signature(func)
    print(func.__name__, sig)
    print(" ", doc or "(no docstring)")

describe(greet)
#: greet (name: str, loud: bool = False) -> str
#:   Return a greeting.
describe(lambda x: x * 2)
#: <lambda> (x)
#:   (no docstring)
```

`inspect.getdoc()` returns `None` when a callable has no docstring, so
`doc or "(no docstring)"` supplies a fallback message instead of
printing `None`. A `lambda` always has a name, `"<lambda>"`, so
`func.__name__` works uniformly on both a `def`-based function and a
`lambda`, with no special case needed to tell them apart.

</details>
</details>
</details>

## 6. The static diagnostic beside the runtime `TypeError`

> Delete the `# type: ignore` comment from `metaclass_layout_conflict.py` and run `ty` over the file.
> Compare the `instance-layout-conflict` diagnostic it reports with the `TypeError` the program prints.
> The static report and the runtime failure describe the same collision.

<details>
<summary>Where to look</summary>

[Multiple Inheritance and Metaclasses](../../Chapters/17_Techniques--Metaprogramming.md#multiple-inheritance-and-metaclasses) introduces the instance layout conflict in `metaclass_layout_conflict.py`.
Remove the `# type: ignore` comment and run `uv run ty check` on the file.
Read both the summary line and the `info` block of the diagnostic, and compare them with the message the `TypeError` carries.

<details>
<summary>Solution</summary>

Removing the `# type: ignore` from `metaclass_layout_conflict.py` leaves
the class header unsuppressed, inside the listing's
`with expected(TypeError):` block:

```python
with expected(TypeError):
    class Singleton(type, dict[type, Any]):
        pass
```

`uv run ty check metaclass_layout_conflict.py` then reports:

```text
error[instance-layout-conflict]: Class will raise `TypeError` at runtime
due to incompatible bases
 --> metaclass_layout_conflict.py:6:11
  |
6 |     class Singleton(type, dict[type, Any]):
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Bases `type` and `dict`
  |           cannot be combined in multiple inheritance
info: Two classes cannot coexist in a class's MRO if their instances
have incompatible memory layouts
 --> metaclass_layout_conflict.py:6:21
  |
6 |     class Singleton(type, dict[type, Any]):
  |                     ----  --------------- `dict` instances have a
  |                     |                     distinct memory layout
  |                     |                     because of the way `dict`
  |                     |                     is implemented in a C
  |                     |                     extension
  |                     `type` instances have a distinct memory layout
  |                     because of the way `type` is implemented in a C
  |                     extension
```

Running the same file prints
`[TypeError] multiple bases have instance lay-out conflict`.

The diagnostic and the exception describe one collision. `ty`'s summary
line names the consequence, "Class will raise `TypeError` at runtime."
Its `info` block explains the rule the interpreter enforces without
explaining: `type` and `dict` are both implemented in C, each with its
own instance layout, so no single object can be both. CPython discovers
that conflict while executing the `class` statement and reports it as
the terse "instance lay-out conflict." `ty` reaches the same conclusion
from the class header alone, before anything runs, and points at both
bases to say which pair is at fault.

The runtime message tells you something collided. The static one tells
you which two bases collided and why, at the moment you type the
header rather than the moment Python first imports the module. The
chapter's `metaclass_layout_conflict.py` carries the `# type: ignore`
because that listing exists to show the `TypeError`.

</details>
</details>

## 7. Building a `float` subclass with `type()`

> Using `type()` directly, build a class `Celsius` with a base of `float`,
> an attribute `unit = "C"`,
> and a method `describe(self)` returning `f"{self} degrees {self.unit}"`.
> Confirm `Celsius(21.5).describe()` works and that `type(Celsius)` is `type`.

<details>
<summary>Where to look</summary>

[Generating Classes with `type()`](../../Chapters/17_Techniques--Metaprogramming.md#generating-classes-with-type) shows the three-argument form of `type()`: a name, a tuple of bases, and a namespace dictionary.
Define `describe()` as an ordinary function, then put it in the dictionary beside `unit`.
Because a function is a descriptor, the lookup on an instance binds it as a method.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from typing import Any

def describe(self: Any) -> str:
    ...
```

<details>
<summary>Solution</summary>

If you write the bases as `(float)`, without the trailing comma,
the parentheses group an expression and build no tuple,
so `type()` raises a `TypeError`:
`type.__new__() argument 2 must be tuple, not type`.
The solution writes `(float,)`, a one-element tuple,
which the three-argument form requires for its bases.

```python
# exercise_7.py
from typing import Any

def describe(self: Any) -> str:
    return f"{self} degrees {self.unit}"

Celsius = type("Celsius", (float,),
               {"unit": "C", "describe": describe})

c = Celsius(21.5)
print(c.describe())
#: 21.5 degrees C
print(type(Celsius) is type)
#: True
print(c + 0.5, isinstance(c, float))
#: 22.0 True
```

**Define the method as a function.** `describe()` annotates `self` as
`Any` because the type checker cannot know that this loose function
ends up on a class carrying a `unit` attribute.

**Assemble the class from data.** The three arguments are the name,
the bases, and the namespace, the same three a `class` statement
assembles for you. A function defined at module level becomes a method
when you put it in that namespace dict. It needs no decoration, because
a function is a descriptor. The attribute lookup binds it to the
instance.

**Confirm the metaclass.** `type(Celsius)` is `type` because this listing calls `type()` as a
constructor rather than subclassing it. Nothing here involves a
metaclass of your own.

**Inherit the base's arithmetic.** `Celsius` inherits `float`'s
arithmetic, so `c + 0.5` works. Because `float.__add__()` builds its
result from `float`, the sum is a `float` rather than a `Celsius`. That
is why a numeric subclass usually overrides every operator whose result
should keep the subclass's type.

</details>
</details>
</details>

## 8. Moving `bases += (Tag,)` into `__init__()`

> In `new_vs_init.py`,
> move the `bases += (Tag,)` line from `__new__()` into `__init__()` and predict the outcome before running it.
> Explain the result in terms of when the class object comes into existence.

<details>
<summary>Where to look</summary>

[`__init__()` versus `__new__()` in a Metaclass](../../Chapters/17_Techniques--Metaprogramming.md#init__-versus-__new__-in-a-metaclass) contrasts what each method can still change.
Ask whether the class object exists yet when the metaclass `__init__()` begins.
Then consider what `bases += (Tag,)` does to a parameter, and print `Demo.__bases__` to check your prediction.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        # Rebinds a local name, nothing else
        ...

class Demo(metaclass=Meta):
    pass
```

<details>
<summary>Solution</summary>

The prediction: the move changes nothing. `Tag` stays out of
`Demo.__bases__`, and Python raises no error.

```python
# exercise_8.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        # Rebinds a local name, nothing else
        bases += (Tag,)
        super().__init__(name, bases, nmspc)

class Demo(metaclass=Meta):
    pass

print(Demo.__bases__)
#: (<class 'object'>,)
print(Tag in Demo.__bases__)
#: False
```

By the time `__init__()` runs, the class object is complete. `type`
built it inside `__new__()`, using the bases the class header supplied
there, and laid out its `__mro__` from them. The `bases` parameter of
`__init__()` reports the tuple `__new__()` used rather than choosing a
new one, so `bases += (Tag,)` rebinds a local name, and `Demo.__bases__`
stays the same. Passing the longer tuple on to `type.__init__()` changes
nothing either, since `type.__init__()` checks its arguments and then
ignores them.

`new_vs_init.py` makes the same point from the other side, with its
`added_in_init` key. `__new__()` must make every decision about what
the class is: its name, its bases, and the namespace from which `type`
builds it. `__init__()` receives the completed class object and can change
it in place, which is why `setattr(cls, ...)` still works there.

</details>
</details>
</details>

## 9. Removing the `KNOWN_COMMANDS` check

> `commander.py` validates `class_name` against `KNOWN_COMMANDS` before splicing it into source text.
> Remove that check, call `Command.make_class()` with a name containing a newline and a second statement,
> and confirm that the injected statement runs.
> `make_class()` splices the name in twice,
> the second time inside a string literal,
> so a bare newline ends the payload as an unterminated string.
> The payload's last line must close or swallow that second splice.
> Restore the check.

<details>
<summary>Where to look</summary>

[The Injection Risk](../../Chapters/17_Techniques--Metaprogramming.md#the-injection-risk) explains why `exec()` on text built from a caller's string is dangerous.
`make_class()` inserts the name into the source twice, so build a payload that stays valid Python at both places.
Open a triple-quoted string in the payload's last line so it absorbs the second insertion, and catch the `KeyError` the final lookup raises.

<details>
<summary>The shape</summary>

```python
# The shape of ch17_exec_injection.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

@dataclass
class Command:
    label: str

    def run(self) -> str:
        ...

    @classmethod
    def make_class(
        cls, class_name: str
    ) -> Callable[[], Command]:
        # The KNOWN_COMMANDS check has been removed:
        ...
```

<details>
<summary>Solution</summary>

If you end the payload after `print("injected code ran")
` and leave
out the triple-quoted line, the script prints nothing and stops with a
`SyntaxError`, "unterminated string literal". `exec()` compiles the
whole spliced source before running any of it, and the second splice
puts a newline inside the `super().__init__("...")` literal, so the
injected `print()` does not run. The solution's payload ends with
`Y = """  #`, which opens a string that swallows the second splice,
so the spliced source compiles.

```python
# ch17_exec_injection.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

@dataclass
class Command:
    label: str

    def run(self) -> str:
        return f"Running {self.label}"

    @classmethod
    def make_class(
        cls, class_name: str
    ) -> Callable[[], Command]:
        # The KNOWN_COMMANDS check has been removed:
        klass = f"""
class {class_name}(Command):
    def __init__(self) -> None:
        super().__init__("{class_name}")
"""
        namespace: dict[str, Any] = {"Command": Command}
        exec(klass, namespace)
        return cast(Callable[[], Command],
                    namespace[class_name])

attack = (
    'X(Command):\n'
    '    pass\n'
    'print("injected code ran")\n'
    'Y = """  #'
)
try:
    Command.make_class(attack)
except KeyError:
    print("lookup failed, after the injection ran")
#: injected code ran
#: lookup failed, after the injection ran
```

**Break out of the class block.** `print("injected code ran")` sits outside every class body. It runs at
module level inside `exec()`, and that is the danger. A name that
reaches `make_class()` unchecked becomes source code, and source code
can do anything the program can do.

**Absorb the second splice.** The payload needs a little care, because `make_class()` splices
`class_name` in twice. The first splice supplies the attack lines. The
second puts them inside the `super().__init__("...")` string literal, where
a bare newline is a `SyntaxError` before anything runs. So the
payload's last line opens a triple-quoted string, `Y = """`. That
string swallows the second splice, and the trailing `#` comments out
the `")` left over after the string closes. The spliced source
compiles, and the
injected `print()` runs at module level inside `exec()`, after the
class body has finished.

**Catch the failed lookup.** The `KeyError` afterward is incidental damage, not protection.
`namespace[class_name]` looks for a class named after the whole
payload, which the spliced source does not define. The injected
statement ran before that lookup, so failing the lookup rescues nothing.
Restoring the `if class_name not in cls.KNOWN_COMMANDS` check closes
the hole at the only point that works: before `make_class()` builds
the string.

</details>
</details>
</details>

## 10. Keeping the first definition instead of raising an exception

> Change `prepare_namespace.py`'s `NoDuplicates` so that instead of raising an exception,
> it keeps the *first* definition of a duplicated name and discards the later one.
> Give the two `on_open` bodies different `print()` calls so you can tell them apart,
> then confirm that `Handlers().on_open()` runs the first one.
> Explain why no class decorator could achieve the same thing.

<details>
<summary>Where to look</summary>

[When You Still Need a Metaclass](../../Chapters/17_Techniques--Metaprogramming.md#when-you-still-need-a-metaclass) shows `__prepare__()` supplying the mapping into which a class body writes.
Subclass `dict` and override `__setitem__()` so it discards a repeated key.
For the explanation, consider which class-creation steps run before the body and which run after it.

<details>
<summary>The shape</summary>

```python
# The shape of ch17_keep_first.py
from typing import Any

class KeepFirst(dict[str, Any]):
    def __setitem__(self, key: str, value: Any) -> None:
        ...

class First(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> KeepFirst:
        ...

class Handlers(metaclass=First):
    def on_open(self) -> None:
        ...
    def on_open(self) -> None:  # noqa: F811
        ...
```

<details>
<summary>Solution</summary>

If you leave `@classmethod` off `__prepare__()`,
Python's call fills `self` with the class name and `name` with the bases.
The `class Handlers` statement then fails with
`TypeError: First.__prepare__() missing 1 required positional argument: 'bases'`,
a message that says nothing about the missing decorator.
Python calls `__prepare__()` on the metaclass before any class object exists,
so the solution keeps the decorator, as [When You Still Need a Metaclass](../../Chapters/17_Techniques--Metaprogramming.md#when-you-still-need-a-metaclass) requires.

```python
# ch17_keep_first.py
from typing import Any

class KeepFirst(dict[str, Any]):
    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            return  # Discard the later definition
        super().__setitem__(key, value)

class First(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> KeepFirst:
        return KeepFirst()

class Handlers(metaclass=First):
    def on_open(self) -> None:
        print("first on_open")
    def on_open(self) -> None:  # noqa: F811
        print("second on_open")

Handlers().on_open()
#: first on_open
```

**Discard a repeated name.** `NoDuplicates` raises an exception on a repeated key. `KeepFirst`
returns instead, so Python builds the second `on_open` function, hands
it to `__setitem__()`, and the mapping discards it. The name still
refers to the first function when the body finishes, as
`Handlers().on_open()` proves.

No class decorator can keep the first definition, and neither can
`__init_subclass__()` or `__set_name__()`. All three receive the class
after its body has finished executing, and by then the body has run
`on_open = <second function>` as an ordinary assignment into the
namespace mapping. The first function has no name pointing at it and no
reference anywhere, so none of the three has anything to restore. Among
the class-creation steps, `__prepare__()` alone sees the assignments one
at a time, as the body makes them, and that is why the chapter calls it
the one with no simpler substitute.

</details>
</details>
</details>
