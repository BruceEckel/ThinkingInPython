# Metaprogramming: Solutions

## 1. Tracking leaves through two more generations

> In `init_subclass.py`, add a class `Yellow(Color)` and then `Gold(Yellow)`.
> Predict `Color.registry` after each new class, then confirm.

<details>
<summary>Where to look</summary>

[Self-Registration of Subclasses](../../Chapters/17_Techniques--Metaprogramming.md#self-registration-of-subclasses)
shows `__init_subclass__()` running once for every new subclass.
Trace what `__init_subclass__()` adds and what it removes for `Yellow`,
then for `Gold`.
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
<summary>Done when</summary>

your edited `init_subclass.py` prints the sorted registry after `Yellow` and again after `Gold`,
and both lists match the predictions you wrote down first.
The two lists are the same length,
and you can say why adding `Gold` changes the registry's contents and not its size.

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

**Register a new leaf.**
The registry holds no `Color`,
so subtracting `Yellow`'s one base leaves the set as it was.
`Yellow` stays until Python creates a subclass of it.

**Drop a base that gains a child.**
Creating `PhthaloBlue` removes `Blue` the same way `Gold` removes `Yellow`.
`__init_subclass__()` runs for every new subclass,
so each new generation adds itself and prunes its parent.
The `Color` class stays as written.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A third `Field` descriptor

> In `set_name.py`, add a third `Field()` attribute, `z`, to `Point`,
> set `p.z = 9`, and confirm `p.__dict__` now also holds `_z`.

<details>
<summary>Where to look</summary>

[A Descriptor That Learns Its Name](../../Chapters/17_Techniques--Metaprogramming.md#a-descriptor-that-learns-its-name)
shows `__set_name__()` receiving the attribute name when Python creates the class.
`__set_name__()` runs once per descriptor instance,
so a third attribute needs a third `Field()` and no new code.
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
<summary>Done when</summary>

after `p.z = 9`, printing `p.__dict__` shows `'_z': 9` beside the `_x` and `_y` entries,
and the `Field` class reads the same as in `set_name.py`.

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

`z = Field()` leaves the `Field` class as it was,
because `__set_name__()` runs once per descriptor, at class-creation time.
Python calls `__set_name__()` separately for `x`, `y`, and `z`,
passing each descriptor its own attribute name.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. A third independent singleton class

> In `singleton.py`, add a third class `CSingleton(metaclass=Singleton)` and confirm `c1 = CSingleton(); c2 = CSingleton(); c1 is c2` is `True`,
> while `c1 is a` (comparing across the different singleton classes)
> is `False`.

<details>
<summary>Where to look</summary>

[Intercepting Instance Creation](../../Chapters/17_Techniques--Metaprogramming.md#intercepting-instance-creation)
shows a metaclass `__call__()` that caches one instance per class.
The cache is a dictionary keyed by the class,
so each class that uses the metaclass gets its own entry.
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
class BSingleton(metaclass=Singleton):
    pass
class CSingleton(metaclass=Singleton):
    pass
```

<details>
<summary>Done when</summary>

your edited `singleton.py` prints `True` for `c1 is c2` and `False` for `c1 is a`,
and its trace shows `building CSingleton` once,
followed by `reusing CSingleton` on the second call.

<details>
<summary>Solution</summary>

The usual form in a metaclass is `super().__call__(*args, **kwargs)`.
If you write it, the script still prints `True` and `False`,
but `ty` reports `invalid-super-argument`.
Under the annotation `cls: type[T]`,
the type checker treats `cls` as some class `T`, not as a `Singleton`,
so it rejects `cls` as the second argument of `super()`.
The solution calls `type.__call__(cls, *args, **kwargs)` and keeps the `type[T]` annotation that types `CSingleton()` as a `CSingleton`.

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
class BSingleton(metaclass=Singleton):
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

**Type the result as the calling class.**
The `__call__[T]` signature is the one from the chapter,
and this solution keeps it rather than simplifying to `-> Any`.
The signature declares the return type as the class `cls` names,
so `CSingleton()` type-checks as a `CSingleton`.
The type checker then catches a misspelled attribute on the result.

The `cls: type[T]` annotation also decides how the body reaches the cache.
`ty` sees `cls` as some class `T`,
so it would report `unresolved-attribute` for `cls._instances`.
The body reads the cache through the class name, `Singleton._instances`,
instead.

**Keep one instance per class.**
`Singleton._instances` is a dictionary keyed by the class,
so each class using the `Singleton` metaclass gets its own entry.
`ASingleton` is a separate key in that dictionary,
so its instance is a separate object.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Making a Class Final](../../Chapters/17_Techniques--Metaprogramming.md#making-a-class-final)
shows `__init_subclass__()` refusing a subclass at runtime.
Python passes the keyword arguments in a class header to `__init_subclass__()`,
so give that method a `final` parameter with a default.
Record each final class in a set on the base,
and check `cls.__mro__` when Python creates a new subclass.

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
<summary>Done when</summary>

`class B(A, final=True):` builds,
a subclass of `B` fails with `[TypeError] B is final; you cannot subclass it`,
and a sibling of `B` written with no keyword in its header accepts a subclass of its own,
for which `issubclass()` against `A` prints `True`.

<details>
<summary>Solution</summary>

If you declare `final` without a default,
`class B(A, final=True):` still builds,
but `class Open(A):` fails with `TypeError: A.__init_subclass__() missing 1 required positional argument: 'final'`.
The solution gives `final` the default `False`,
so `class Open(A):` gets `final=False` from the default.

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

**Accept the header keyword.**
Python passes the keywords in a class header to `__init_subclass__()`,
so creating `B` calls `A.__init_subclass__()` with `final=True` from the header `class B(A, final=True):`.

**Pass the other keywords up.**
The remaining `**kwargs` go on to `super().__init_subclass__()`,
which turns a misspelled keyword into a `TypeError` instead of a silent no-op.

**Refuse any descendant of a final class.**
The chapter's `final_runtime.py` hard-codes the refusal into `B`'s own `__init_subclass__()`.
This version moves the decision into a set that `A` owns.

`A.__init_subclass__()` refuses the first subclass of a final class as Python creates that subclass,
so the hierarchy below a final class stays empty.
A check of the direct bases in `cls.__bases__` would therefore refuse every descendant as well as the first subclass.
The `__mro__` walk stays because it states the rule as written,
"no final class anywhere above," in one line.

**Confirm a sibling stays open.**
`Open` and `Sub` show that the rest of the hierarchy still subclasses freely.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[The Core Functions](../../Chapters/17_Techniques--Metaprogramming.md#the-core-functions)
lists the `inspect` calls for signatures and docstrings.
Call `inspect.signature()` and `inspect.getdoc()` on the function,
and print the function's `__name__`.
Since `getdoc()` returns `None` for a missing docstring,
supply the fallback text with `or`.

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
<summary>Done when</summary>

`describe(greet)` prints `greet (name: str, loud: bool = False) -> str` and then `Return a greeting.`,
and `describe(lambda x: x * 2)` prints `<lambda> (x)` and then `(no docstring)` in place of `None`.

<details>
<summary>Solution</summary>

If you print `doc` without the `or` fallback, `greet` still shows its docstring,
but the lambda's second line reads `None`,
since `inspect.getdoc()` returns `None` for a callable with no docstring.
The type checker accepts that version, because `print()` takes any object.
The solution writes `doc or "(no docstring)"`,
which replaces a missing docstring with the message.

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

Every `lambda` carries the name `"<lambda>"`,
so `func.__name__` works the same way on a `def` function and on a `lambda`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. The static diagnostic beside the runtime `TypeError`

> Delete the `# type: ignore` comment from `metaclass_layout_conflict.py` and run `ty` over the file.
> Compare the `instance-layout-conflict` diagnostic it reports with the `TypeError` the program prints.
> The static report and the runtime failure describe the same collision.

<details>
<summary>Where to look</summary>

[Multiple Inheritance and Metaclasses](../../Chapters/17_Techniques--Metaprogramming.md#multiple-inheritance-and-metaclasses)
introduces the instance layout conflict in `metaclass_layout_conflict.py`.
Remove the `# type: ignore` comment and run `uv run ty check` on the file.
Read both the summary line and the `info` block of the diagnostic,
and compare them with the message the `TypeError` carries.

<details>
<summary>Done when</summary>

`uv run ty check` on your edited `metaclass_layout_conflict.py` reports `instance-layout-conflict` with bases `type` and `dict`,
and you can name two facts the diagnostic states that the runtime `[TypeError] multiple bases have instance lay-out conflict` leaves out.

<details>
<summary>Solution</summary>

Removing the `# type: ignore` from `metaclass_layout_conflict.py` exposes the class header to the type checker,
inside the listing's `with expected(TypeError):` block:

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

Running the same file prints `[TypeError] multiple bases have instance lay-out conflict`.

The diagnostic and the exception describe one collision.
`ty`'s summary line states the consequence,
"Class will raise `TypeError` at runtime."
The diagnostic's `info` block states the rule behind the collision.
`type` and `dict` are both implemented in C, each with its own instance layout,
so no single object can be both.
CPython discovers that conflict while executing the `class` statement and reports it as the terse "instance lay-out conflict."
`ty` reports the same conflict from the class header alone,
before anything runs, and marks both bases to show which pair conflicts.

The runtime message tells you something collided.
The static diagnostic tells you which two bases collided and why,
at the moment you type the header rather than the moment Python first imports the module.

The chapter's `metaclass_layout_conflict.py` still carries the `# type: ignore`,
because that listing exists to show the `TypeError`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. Building a `float` subclass with `type()`

> Using `type()` directly, build a class `Celsius` with a base of `float`,
> an attribute `unit = "C"`,
> and a method `describe(self)` returning `f"{self} degrees {self.unit}"`.
> Confirm `Celsius(21.5).describe()` works and that `type(Celsius)` is `type`.

<details>
<summary>Where to look</summary>

[Generating Classes with `type()`](../../Chapters/17_Techniques--Metaprogramming.md#generating-classes-with-type)
shows the three-argument form of `type()`: a name, a tuple of bases,
and a namespace dictionary.
Define `describe()` as an ordinary function,
then put it in the dictionary beside `unit`.
Because a function is a descriptor,
the lookup on an instance binds it as a method.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from typing import Any

def describe(self: Any) -> str:
    ...
```

<details>
<summary>Done when</summary>

your file contains no `class` statement,
`Celsius(21.5).describe()` returns `21.5 degrees C`,
and `type(Celsius) is type` prints `True`.

<details>
<summary>Solution</summary>

If you write the bases as `(float)`, without the trailing comma,
the parentheses group an expression that evaluates to the class `float`,
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

**Define the method as a function.**
`describe()` is a module-level function,
defined before `type()` creates the class that carries `unit`.
With no class to name as the type of `self`, the annotation uses `Any`,
which lets the type checker accept `self.unit`.

**Assemble the class from data.**
The three arguments are the name, the bases, and the namespace,
the same three a `class` statement assembles for you.
A module-level function becomes a method once it sits in that namespace dict.
Because a function is a descriptor,
the attribute lookup binds it to the instance.

**Confirm the metaclass.**
`type(Celsius)` is `type` because this listing calls `type()` as a constructor rather than subclassing it.
`Celsius` gets the default metaclass, the same one a `class` statement uses.

**Inherit the base's arithmetic.**
Because `float.__add__()` builds its result from `float`,
the sum `c + 0.5` is a `float` rather than a `Celsius`.
A numeric subclass therefore usually overrides every operator whose result should keep the subclass's type.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. Moving `bases += (Tag,)` into `__init__()`

> In `new_vs_init.py`,
> move the `bases += (Tag,)` line from `__new__()` into `__init__()` and predict the outcome before running it.
> Explain the result in terms of when the class object comes into existence.

<details>
<summary>Where to look</summary>

[`__init__()` versus `__new__()` in a Metaclass](../../Chapters/17_Techniques--Metaprogramming.md#init__-versus-__new__-in-a-metaclass)
contrasts what each method can still change.
Ask whether the class object exists yet when the metaclass `__init__()` begins.
Then consider what `bases += (Tag,)` does to a parameter,
and print `Demo.__bases__` to check your prediction.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        # Rebinds a local name, nothing else
        ...

class Demo(metaclass=Meta):
    pass
```

<details>
<summary>Done when</summary>

your edited `new_vs_init.py` runs with no exception and prints `has Tag base: False`,
the outcome matches the prediction you wrote first,
and you can say what exists by the time the metaclass `__init__()` starts.

<details>
<summary>Solution</summary>

The prediction: `Demo` builds cleanly,
and `Demo.__bases__` holds `object` alone, so `Tag` stays out.

```python
# exercise_8.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        # Rebinds a local name, nothing else
        bases += (Tag,)
        super().__init__(name, bases, namespace)

class Demo(metaclass=Meta):
    pass

print(Demo.__bases__)
#: (<class 'object'>,)
print(Tag in Demo.__bases__)
#: False
```

By the time `__init__()` runs, the class object is complete.
`type.__new__()` builds it first, from the bases in the class header,
and computes its `__mro__` from those bases.
The `bases` parameter of `__init__()` holds the same tuple `__new__()` received.
A tuple is immutable,
so `bases += (Tag,)` builds a new tuple and rebinds the local name `bases` to it.
Passing the longer tuple on to `type.__init__()` leaves the class as it was too,
since `type.__init__()` checks its arguments and then ignores them.

`new_vs_init.py` shows the same limit for the namespace.
Its `__init__()` writes an `added_in_init` key into `namespace`.
`hasattr()` then reports `False` for that attribute on the class.
`__new__()` must make every decision that goes through the arguments: the name,
the bases, and the namespace from which `type` builds the class.
`__init__()` receives the completed class object and can change it in place,
which is why `setattr(cls, ...)` still works there.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[The Injection Risk](../../Chapters/17_Techniques--Metaprogramming.md#the-injection-risk)
explains why `exec()` on text built from a caller's string is dangerous.
`make_class()` inserts the name into the source twice,
so build a payload that stays valid Python at both places.
Open a triple-quoted string in the payload's last line so the text up to the second insertion becomes string content,
and catch the `KeyError` the final lookup raises.

<details>
<summary>The shape</summary>

```python
# The shape of ch17_exec_injection.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

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
<summary>Done when</summary>

with the check removed,
your payload makes `commander.py` print the injected statement's output,
with no `SyntaxError`, before the final lookup fails with a `KeyError`.
With the check restored,
the same payload raises a `ValueError` starting `Unknown command:` and the injected output disappears.

<details>
<summary>Solution</summary>

If you end the payload after `print("injected code ran")` and leave out the triple-quoted line,
the script stops at once with a `SyntaxError`, `unterminated string literal`.
The second splice puts a newline inside the `super().__init__("...")` literal.
`exec()` compiles the whole spliced source before running any of it,
so the `SyntaxError` arrives before the injected `print()` can run.
The solution's payload ends with `Y = """  #`,
which opens a string that the second splice's `"""` closes,
so the spliced source compiles.

```python
# ch17_exec_injection.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

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
        namespace: dict[str, object] = {"Command": Command}
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

**End the class block.**
The payload's `pass` fills the body of a class `X`,
and the dedented `print("injected code ran")` after it sits at module level,
so it runs inside `exec()`.
A name that reaches `make_class()` unchecked becomes source code,
and source code can do anything the program can do.

**Close the second splice's string.**
The payload must compile at both splice points,
because `make_class()` splices `class_name` in twice.
The first splice supplies the attack lines.
The second puts them inside the `super().__init__("...")` string literal,
where a bare newline is a `SyntaxError` before anything runs.
So the payload's last line opens a triple-quoted string, `Y = """`.
That string runs to the `"""` in the second splice,
so the template text between the two splices becomes string content.
The trailing `#` then comments out the `")` left over after the string closes.
The spliced source compiles,
and the injected `print()` runs once the class body finishes.

**Catch the failed lookup.**
The `KeyError` afterward is a side effect of the payload, not a defense.
`namespace[class_name]` looks for a class named after the whole payload,
while the spliced source defines a class named `X`.
The injected statement runs before that lookup,
so the lookup fails too late to stop it.

Restoring the `if class_name not in cls.KNOWN_COMMANDS` check rejects the payload before `make_class()` builds the string,
so the injected code stops at the check, before `exec()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. Keeping the first definition instead of raising an exception

> Change `prepare_namespace.py`'s `NoDuplicates` so that instead of raising an exception,
> it keeps the first definition of a duplicated name and discards the later one.
> Give the two `on_open` bodies different `print()` calls so you can tell them apart,
> then confirm that `Handlers().on_open()` runs the first one.
> Explain why no class decorator could achieve the same thing.

<details>
<summary>Where to look</summary>

[When You Still Need a Metaclass](../../Chapters/17_Techniques--Metaprogramming.md#when-you-still-need-a-metaclass)
shows `__prepare__()` supplying the mapping into which a class body writes.
Subclass `dict` and override `__setitem__()` so it discards a repeated key.
For the explanation,
consider which class-creation steps run before the body and which run after it.

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
<summary>Done when</summary>

the `Handlers` class statement completes with no exception,
`Handlers().on_open()` prints the first body's message,
and you can name the class-creation step that runs before the class body and say why no class decorator can stand in for it.

<details>
<summary>Solution</summary>

If you leave `@classmethod` off `__prepare__()`,
Python's call fills `cls` with the class name and `name` with the bases.
The `class Handlers` statement then fails with `TypeError: First.__prepare__() missing 1 required positional argument: 'bases'`,
a message that blames a missing `bases` argument rather than the missing decorator.
Python calls `__prepare__()` on the metaclass before any class object exists,
so the solution keeps the decorator,
as [When You Still Need a Metaclass](../../Chapters/17_Techniques--Metaprogramming.md#when-you-still-need-a-metaclass)
requires.

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

**Discard a repeated name.**
`NoDuplicates` raises an exception on a repeated key.
`KeepFirst.__setitem__()` returns early.
Python still builds the second `on_open` function and passes it to `__setitem__()`,
where the early return discards it.

No class decorator can keep the first definition,
and neither can `__init_subclass__()` or `__set_name__()`.
All three receive the class after its body has finished executing.
By then the body has run `on_open = <second function>` as an ordinary assignment into the namespace mapping.
That assignment drops the last reference to the first function,
so Python frees the first function before any of the three runs.
Among the class-creation steps,
`__prepare__()` alone supplies the mapping that receives the assignments one at a time,
as the body makes them.
That is why the chapter says `__prepare__()` has no simpler substitute.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
