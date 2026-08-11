# Modules and Packages

Each Python file is a *module* you can `import` into another Python file.
If the file is in the same directory,
you can use an unqualified `import` statement:

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
#: 'module' imported
#: Use this elsewhere!
```

Importing a module makes its *namespace* reachable in the importing file,
under the module's name.
This automatically prevents name clashes between the imported module's names and the local ones.
To call `useful_function()`, you must *qualify* it with the name of the module:
`module.useful_function()`.

The code at the end of `use_module.py` starts with an `if` clause that checks whether the standard variable `__name__` is equal to the string `"__main__"`.
In Python, any identifier that begins and ends with double underscores
(commonly called a "dunder") is special in some way.
Dunder methods, for example,
connect your class to the language's operators and built-in functions
(see [Classes](07_Classes.md)).

The reason for the `if` is that you can also use any file as a library module within another program.
In that case, you want only its definitions,
but you don't want the code at the bottom of the file to run.
This particular `if` condition is true only when you are running this file directly.
That is, `__name__` is `"__main__"` when you use the command line:

```
python use_module.py
```

However, if another program imports `use_module.py` as a module,
`__name__` is not `"__main__"`, so its `"__main__"` code does not run.
Here is such a program, which only imports `use_module`:

```python
# import_module.py
import use_module
#: 'module' imported
```

Importing `use_module` runs its top-level code, including the `print()`,
but not its `"__main__"` block.
It runs that code once, however many times the program imports it:

```python
# import_once.py
import sys
import use_module
import use_module as second

#: 'module' imported
print(use_module is second)
#: True
print(sys.modules["use_module"] is use_module)
#: True
```

`use_module`'s body runs once even though two `import` statements name it.
The first `import` stored the finished module object in `sys.modules`,
a dict keyed by dotted module name.
Every later `import` of that name, from any file in the program,
finds it there and binds the same object instead of re-running the file,
which is why `use_module` and `second` are one object.
A consequence: a running program does not notice an edit to a module it has imported.
Restart it, or call `importlib.reload(use_module)`,
which re-runs the body into the existing module object.
Reloading leaves every name bound by a `from ... import` pointing at the old objects,
so restarting is the reliable choice.

To bring a name into the current namespace, use the `from` keyword:

```python
# using_from.py
from module import useful_function

if __name__ == "__main__":
    print(useful_function())
#: Use this elsewhere!
```

`from` copies the name's current value into this file rather than linking to it.
Rebinding the name in the module afterward does not reach the copy:

```python
# app_settings.py

debug: bool = False

def show() -> None:
    print(f"app_settings.debug is {debug}")
```

```python
# from_snapshot.py
import app_settings
from app_settings import debug

app_settings.debug = True
print(debug, app_settings.debug)
#: False True
app_settings.show()
#: app_settings.debug is True
```

`app_settings.debug` is now `True`,
and `show()` sees the new value because it looks the name up in its own module every time it runs.
The local `debug` is a separate binding made once, at import,
so it still holds `False`.
Import the module and write `app_settings.debug` when the value can change;
use `from ... import` for things that don't get rebound,
such as functions and classes.

You can rename a module's namespace during an import using the `as` keyword:

```python
# using_as.py
import module as m

if __name__ == "__main__":
    print(m.useful_function())
#: Use this elsewhere!
```

A module's namespace is an ordinary dict you can read and write.
`globals()` returns it as a mutable `dict`,
the same dict Python already searches when it looks up a top-level name.
It is also the dict behind the dotted name:
`use_module.__dict__` from outside is the same object `globals()` returns inside `use_module`,
which is why `module.useful_function()` and a top-level lookup inside `module.py` find the same function.
Assigning into that dict has the same effect as writing the assignment directly:

```python
# globals_demo.py
x = 10
print(globals()["x"])
#: 10

globals()["y"] = 42
print(y)  # type: ignore  # noqa: F821
#: 42
```

The two directives on the `print(y)` line silence the type checker and the linter,
neither of which can see a name that appears only as a dict key.
That is the cost of creating names this way, and a reason to keep it rare.
Assigning into `globals()` matters whenever code needs to define a module-level name that isn't known until runtime,
such as a class built dynamically and registered under a computed name
(see [Metaprogramming](17_Metaprogramming.md)).

## Packages

As your programs get larger, you'll further organize your code into *packages*.
A package is a directory that contains multiple modules,
and it forms its own namespace with the name of that directory.

To make something a package,
you put a special file named `__init__.py` in that directory.
`__init__.py` runs once, before any module inside the package loads.
It is often empty, and then it only flags the directory as a package.^[The name `__init__.py` often confuses people. In hindsight, it might have been better to have named the file `__package__.py`.]
When it isn't, it usually re-exports the package's public names,
so that `from a_package import function1` works and callers never learn which submodule `function1` lives in.
You can still import a directory without `__init__.py` as a *namespace package*,
but an explicit `__init__.py` makes the package's identity and boundary clear,
so this book uses one by default.

To explore this, create a directory called `a_package` whose `__init__.py` announces itself,
so the markers below show when it runs:

```python
# a_package/__init__.py

print("initializing a_package")
```

Now add two modules to the package:

```python
# a_package/module1.py

print("importing module1 in a_package")

def function1():
    return "function1 in module1 in a_package"
```

```python
# a_package/module2.py

print("importing module2 in a_package")

def function2():
    return "function2 in module2 in a_package"
```

To import a module from a package, you must qualify it with the package name:

```python
# using_packages.py
import a_package.module1
import a_package.module2

#: initializing a_package
#: importing module1 in a_package
#: importing module2 in a_package
print("a_package" in dir(), "module1" in dir())
#: True False
print(a_package.module1.function1())
#: function1 in module1 in a_package
print(a_package.module2.function2())
#: function2 in module2 in a_package
```

`import a_package.module1` binds only the name `a_package` in this file.
Loading `module1` also sets it as an attribute of the package,
which is why `a_package.module1.function1()` resolves,
and why the shorter `module1.function1()` fails here but works in `from_packages.py` below,
where `from` binds `module1` directly.

Importing the package alone does not import what is inside it:

```python
# package_only.py
import a_package

#: initializing a_package
print(hasattr(a_package, "module1"))
#: False
```

No submodule loads, and no message prints beyond the package's own.
`a_package.module1.function1()` here would raise `AttributeError: module 'a_package' has no attribute 'module1'`.
The submodule becomes an attribute of the package only when something imports it by name.

You can also name the package with `from`:

```python
# from_packages.py
from a_package import module1, module2

#: initializing a_package
#: importing module1 in a_package
#: importing module2 in a_package
print(module1.function1())
#: function1 in module1 in a_package
print(module2.function2())
#: function2 in module2 in a_package
```

Here you no longer need to qualify the module with the package name.

You can bring specific functions into the namespace by naming both the package and the module:

```python
# no_qualification.py
from a_package.module1 import function1
from a_package.module2 import function2

#: initializing a_package
#: importing module1 in a_package
#: importing module2 in a_package
print(function1())
#: function1 in module1 in a_package
print(function2())
#: function2 in module2 in a_package
```

This listing, `from_packages.py`,
and `using_packages.py` print the same loading messages:
`from` does not load less.
The whole module runs either way;
the statement decides only which names this file binds.

You can put a second package underneath the first one:

```python
# a_package/b_package/__init__.py

print("initializing b_package")
```

```python
# a_package/b_package/module3.py

print("importing module3 in b_package")

def function3():
    return "function3 in module3 in b_package"
```

To import `module3` you must specify both packages:

```python
# two_levels.py
from a_package.b_package import module3

#: initializing a_package
#: initializing b_package
#: importing module3 in b_package
print(module3.function3())
#: function3 in module3 in b_package
```

### Imports Within a Package

The listings above import into a package from outside it.
A package's own modules also import each other,
and there the leading dot of a *relative import* means "the package containing this module":

```python
# a_package/module4.py
from .module1 import function1

def function4():
    return f"function4 calls {function1()}"
```

```python
# use_module4.py
from a_package.module4 import function4

#: initializing a_package
#: importing module1 in a_package
print(function4())
#: function4 calls function1 in module1 in a_package
```

`module4` finds its sibling without naming `a_package`,
so renaming the package breaks nothing inside it.
Two dots (`..module1`) reach the parent package,
which is how `b_package/module3.py` would import from `a_package`.
The absolute form `from a_package.module1 import function1` works from inside the package too,
and is the better choice when the import crosses a package boundary.
Keep relative imports for a package's own submodules.

A relative import needs a package context,
which a file run as a script does not have.
Running `python a_package/module4.py` raises `ImportError: attempted relative import with no known parent package`.
Run it as `python -m a_package.module4` instead.

Two modules in a package can end up importing each other.
Python places the first one to load in `sys.modules` before its body finishes,
so a `from` import in the second finds a partially initialized module and fails with `ImportError: cannot import name ... (most likely due to a circular import)`.
A cycle is a design signal:
move the shared piece into a third module both can import.
When the cycle exists only in annotations,
an `if TYPE_CHECKING:` import breaks it,
because annotations are not evaluated at import time
(see [Simulation](38_Simulation.md#a-robot-in-a-maze)).

## What a Module Exports

Every name at a module's top level is importable,
because Python has no `private` keyword.
A module states its boundary by convention and by one optional list.

A leading underscore marks a name as internal.
It is a signal to a reader rather than a barrier.
`accounting._Engine` still resolves,
and `from accounting import _Engine` still works.
The underscore changes one mechanical thing:
`from accounting import *` skips every name that begins with one.

`__all__` states the export list explicitly.
You assign it at module level as a list of strings naming the public names,
and `from module import *` imports those and no others, underscore or not.
An `__all__` also documents the intended surface in one readable place,
which a scattering of underscores does not,
and it is what documentation tools read when they ask what a module offers.

```python
# exporting.py

__all__ = ["public", "helper"]

def public():
    return "public"

def helper():
    return "helper"

def _internal():
    return "internal"

def undeclared():
    return "undeclared"
```

```python
# star_import.py
from exporting import *  # noqa: F403

print(sorted(n for n in dir() if not n.startswith("__")))
#: ['helper', 'public']
```

Without `__all__`, the star import would bind `public`, `helper`,
and `undeclared`: everything not underscored.
With it, only the listed names arrive, and `_internal` is skipped either way.

Neither mechanism stops `module._name`.
Both say which names a caller should use,
which is enough to treat a module as a façade over its internals
([Changing the Interface](29_Changing_the_Interface.md))
or as a shared single instance
([Singleton](24_Singleton.md#a-module-is-already-a-singleton)).

## File Names

To be the target of an `import` statement,
a module's file name must be a valid Python identifier and not a keyword.
`import my-mod` cannot parse.
(`importlib.import_module("my-mod")` still loads it, which is how plugin loaders reach oddly named files, but that is not a name you should choose.)

**Modules** (`.py` files): short, all-lowercase,
with underscores between words if that improves readability.
This is `snake_case`.

- Good: `result.py`, `cache_singleton.py`, `list_comprehension.py`
- Avoid: `Result.py` (CapWords is for classes), `cacheSingleton.py` (camelCase),
  `cache-singleton.py` (hyphens aren't importable)

**Packages** (directories with `__init__.py`): also short and all-lowercase,
but convention discourages underscores.
Prefer a single run-together word when you can.

- Good: `mypackage`, and underscores only when they genuinely help (`a_package`)

**Tests** follow pytest's discovery convention: `test_*.py` (or `*_test.py`).
This book uses `test_*.py`, e.g. `test_result.py`.

Don't shadow standard-library modules.
A file named `random.py`, `types.py`,
or `weakref.py` can hide the stdlib one and break imports,
because Python searches the directory of the script you ran before the standard library
(see [`PYTHONPATH`](#pythonpath) below).
Give a shared module a distinctive name for the same reason:
the first `config.py` imported anywhere in the process is the one every later `import config` gets.

## `PYTHONPATH`

Python searches `sys.path`, a list of directories it builds at startup.
`print(sys.path)` shows it.
Its first entry is the directory of the script you ran
(the current directory when you use `-m` or the REPL),
which is why `use_module.py` could `import module` with no setup;
the entries from `PYTHONPATH` come next,
and installed packages sit further down.
Running with `-P` drops that first entry,
so a local `random.py` can no longer shadow the standard library.

What if your module or package isn't in the same directory as the Python file doing the importing?
The original solution was the `PYTHONPATH` environment variable,
which tells Python where to look for modules and packages.
`PYTHONPATH` takes multiple paths,
and Python keeps searching through those paths until it finds your module or package
(or doesn't, and reports an error).

`PYTHONPATH` still works,
but the modern practice is to install your package into the environment you are using,
which puts it on the search path without any environment variable.
Concretely, with `uv` (this book's tool of choice), that means `uv sync`,
or `uv pip install -e .` for an editable install.
The package resolves by name from anywhere,
and edits to its source take effect immediately, without reinstalling.

## Lazy Imports

Every `import` so far runs the target module's top-level code immediately,
which is why importing `a_package.module1` earlier printed its message as it loaded.
For a large program that imports many modules but uses only some of them on any given run,
that eager work slows startup.

Python 3.15 ([PEP 810](https://peps.python.org/pep-0810/))
adds the `lazy` soft keyword.
A `lazy import` defers loading the module until the first time you use the imported name,
so a run pays only for the modules it uses,
while all imports stay at the top of the file:

```python
# lazy_imports.py
lazy import json
lazy from pathlib import Path

print(json.dumps({"a": 1}))
#: {"a": 1}
print(Path("report/data.txt").suffix)
#: .txt
```

A `lazy import` looks like an ordinary one, with `lazy` in front,
and once loaded the names behave like eagerly imported ones.
`json` and `pathlib` load at the `json.dumps` and `Path(...)` calls,
which this listing cannot show, since the output is the same either way.

Before 3.15, deferring a costly import meant moving it inside the function that needed it.
That works, but it hides the dependency:
nothing at the top of the file mentions the module,
tools that read imports miss it,
and the `import` statement re-runs its `sys.modules` lookup on every call.
`lazy import` keeps the declaration at the top where a reader and a tool can see it,
and pays the loading cost once, at first use.
You can watch the deferral by importing a module whose body prints when it runs:

```python
# noisy.py

print("noisy module loaded")

def announce():
    print("noisy.announce() called")
```

```python
# lazy_noisy.py
lazy import noisy

print("before first use")
#: before first use
noisy.announce()
#: noisy module loaded
#: noisy.announce() called
print("after first use")
#: after first use
```

Nothing loads at the `lazy import` line.
The body of `noisy` runs at `noisy.announce()`, the first access,
which is why `noisy module loaded` prints after `before first use`.
If a lazily imported module is missing or broken,
the error surfaces at that first use rather than at the import line.
`sys.lazy_modules` holds the names that are currently deferred,
so you can check what a run actually put off without instrumenting the modules.

`lazy` works with both `import` and `from ... import`, but only at module scope.
Using it inside a function, a class body, or a `try` block is a `SyntaxError`,
and Python likewise rejects `lazy from module import *` and a `lazy from __future__` import.
To change the setting for a whole run without editing source,
run with `-X lazy_imports=MODE` or set `PYTHON_LAZY_IMPORTS=MODE`.
Both accept one of two values.
`normal`, the default, defers only the imports you marked `lazy`.
`all` defers every module-level import the keyword could have marked,
so the imports it cannot mark, such as one inside a `try` block, stay eager.
The PEP also describes a third value, `none`, a global off switch;
CPython removed it before the 3.15 release.

Don't make an import lazy when you import a module for what its body does rather than for a name it defines.
A module that registers a plugin class
([Factory](27_Factory.md#the-pythonic-factory-a-dictionary)), installs a codec,
or fills a table does that work as it loads,
and a lazily imported name nobody touches never loads.
The failure is silent: no error, just a table with a row missing.
That is also why `all` is an experiment to run rather than a setting to leave on,
since it defers ordinary `import` statements too,
including the ones whose only purpose is to run the module.

## Exercises

1.  Add a third module, `a_package/module5.py`,
    with its own `function5()` that prints a message when the module loads.
    Import it three different ways, one each using `import a_package.module5`,
    `from a_package import module5`,
    and `from a_package.module5 import function5`,
    and confirm the loading message prints only once no matter how many of the three you use together.
2.  Add `a_package/b_package/module6.py` with a `function6()` that calls `function5()` from `module5`.
    Import and call `function6()` from a script outside `a_package`,
    then rename `b_package` to `bPackage` (and rename it back afterward)
    and explain, from the naming rules above,
    why that name is a poor choice even though the import still works.
3.  Write a small module `noisy2.py` whose top-level body prints a message,
    similar to `noisy.py` above.
    In a new script, `lazy import` both `noisy` and `noisy2`,
    then use `noisy2` before `noisy`.
    Confirm the two loading messages print in the order you used the modules,
    not the order you wrote the `lazy import` lines.
4.  Rename `module.py` to `Module.py` and change `use_module.py` to `import Module`.
    Run it.
    Then change the import back to `import module`,
    leaving the file named `Module.py`, and run it again.
    Predict the result before you run it, then explain what you see,
    given that Windows and macOS open `module.py` and `Module.py` as the same file.
    Look up `PYTHONCASEOK` to confirm your explanation.
5.  Change `a_package/module4.py` to the absolute import `from a_package.module1 import function1` and confirm `use_module4.py` still works.
    Then run `python a_package/module4.py` directly,
    both before and after the change.
    Both fail, with different errors: explain each,
    and say why `python -m a_package.module4` works either way.
6.  Remove the `__all__` line from `exporting.py`.
    Predict what `star_import.py` prints without it, run it to check,
    then restore the line.
