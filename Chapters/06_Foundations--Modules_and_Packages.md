# Modules and Packages

> A program outgrows one file,
> and the pieces must find each other by name.

Each Python file is a *module* you can `import` into another Python file.
If the file is in the same directory, you import it by its file name,
without the `.py` ([`PYTHONPATH`](#pythonpath) covers where else Python looks):

```python
# module.py

def useful_function():
    return "I'm being useful!"
```

```python
# use_module.py
import module

print("use_module body runs")
#: use_module body runs

if __name__ == "__main__":
    print(module.useful_function())
#: I'm being useful!
```

A module's *namespace* is the set of names the module defines.
Importing the module makes that namespace accessible in the importing file under the module's name.
Accessing those names through the module's name keeps them separate from the importing file's own names.
To call `useful_function()`, you must *qualify* it with the name of the module:
`module.useful_function()`.

The code at the end of `use_module.py` starts with an `if` clause that checks whether the standard variable `__name__` equals the string `"__main__"`.
Any identifier that begins and ends with double underscores (a dunder)
is one that Python itself sets or calls.
Python calls a class's dunder methods, for example,
to apply the language's operators and built-in functions to its objects.
[Classes](07_Foundations--Classes.md)
shows how `print()` and `str()` call a class's `__str__()`.

Python programmers call this `__name__` check the *main guard*.
When another program imports this file as a library module,
the guard skips the code at the bottom of the file,
the part meant for a command-line run.
`__name__` is `"__main__"` only when you run this file as a script from the command line:

```
python use_module.py
```

However, if another program imports `use_module.py` as a module,
`__name__` is `"use_module"`, so Python skips the `"__main__"` block.
The next script consists of one statement, `import use_module`:

```python
# import_module.py
import use_module
#: use_module body runs
```

Python runs a module's top-level code once,
however many times the program imports the module:

```python
# import_once.py
import sys
import use_module
import use_module as second

#: use_module body runs
print(use_module is second)
#: True
print(sys.modules["use_module"] is use_module)
#: True
```

The first `import` creates the module object, stores it in `sys.modules`,
and then runs the file's body to fill it.
`sys.modules` is a dict keyed by dotted module name.
Every later `import` of that name, from any file in the program,
finds the module there and binds the same object.
The `as second` clause binds that object under a second name
([covered next](#importing-names-with-from-and-as)),
so `use_module` and `second` are one object.

Because every later `import` finds the cached object in `sys.modules`,
a running program keeps the module it loaded,
however you edit the module's file afterward.
To load the edited file, restart the program,
or call `importlib.reload(use_module)`,
which re-runs the body into the existing module object.
Reloading leaves every name bound by a `from ... import` pointing at the old objects,
so restarting is the reliable choice.

## Importing Names with `from` and `as`

The `from` keyword brings `useful_function` into the current namespace:

```python
# using_from.py
from module import useful_function

print(useful_function())
#: I'm being useful!
```

`from` works like an assignment.
It binds a name in this file to the object the module's name refers to at that moment.
The two names are separate,
so rebinding the module's name afterward leaves this file's name as it was:

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
print(f"{debug=} {app_settings.debug=}")
#: debug=False app_settings.debug=True
app_settings.show()
#: app_settings.debug is True
```

`show()` prints the new value because it looks the name up in its own module every time it runs.
Because the `debug` in `from_snapshot.py` is a separate binding that `from` set once,
at import, it still holds `False`.

Import the module and write `app_settings.debug` when the value can change.
Use `from ... import` for names that keep the same value,
such as functions and classes.

The `as` keyword binds the imported module to a name you choose:

```python
# using_as.py
import module as m

print(m.useful_function())
#: I'm being useful!
```

## The Module Namespace

A module's namespace is an ordinary dict you can read and write.
`globals()` returns it,
the same dict Python searches when it looks up a top-level name.
`module.__dict__` from outside is the same object `globals()` returns inside `module`,
so `module.useful_function()` and a top-level lookup inside `module.py` find the same function.
Assigning into that dict works like writing the assignment as a statement:

```python
# globals_demo.py
x = 10
print(globals()["x"])
#: 10

globals()["y"] = 42
print(y)  # type: ignore  # noqa: F821
#: 42
```

The type checker and the linter both report `y` as undefined,
because the source creates `y` only as a dict key.
The two directives on the `print(y)` line silence those reports.
Creating names this way loses both checks on that name,
so keep the technique rare.

Assigning into `globals()` is useful when code must define a module-level name known only at runtime,
such as a class built dynamically under a computed name.
[Metaprogramming](17_Techniques--Metaprogramming.md) builds classes that way,
though it collects them in a dictionary instead of in the module's namespace.

## Packages

As your programs get larger, you further organize your code into *packages*.
A package is a directory that contains multiple modules,
each one a *submodule* of the package.
It forms its own namespace, named after the directory.

To make a directory a package, you put a special file named `__init__.py` in it.
`__init__.py` runs once,
the first time a program imports the package or any module inside it.
An empty `__init__.py`, the common case,
only flags the directory as a package.^[The name `__init__.py` often confuses people. In hindsight, it might have been better to name the file `__package__.py`.]
An `__init__.py` with content usually re-exports the package's public names.
If `a_package/__init__.py` re-exports `function1`,
callers write `from a_package import function1`.
Callers then never write the name of the submodule that defines `function1`.

You can also import a directory without `__init__.py` as a *namespace package*.
Namespace packages let one package span several directories,
such as separately installed distributions that each supply part of the package.
The import system merges every directory with the package's name on [`sys.path`](#pythonpath)
into one package.

A directory can also become a namespace package by accident.
If you forget `__init__.py`,
the import still succeeds and hides the missing file.
Any module or `__init__.py` package of the same name then takes precedence over your package,
wherever it sits on `sys.path`, including a directory later in the search.
This book uses an explicit `__init__.py` by default,
because a directory with `__init__.py` is one package,
found at its own place on `sys.path`,
and no module or package later in the search can replace it.

To explore packages,
create a directory called `a_package` whose `__init__.py` prints a message,
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
print(sorted(n for n in dir() if not n.startswith("__")))
#: ['a_package']
print(a_package.module1.function1())
#: function1 in module1 in a_package
print(a_package.module2.function2())
#: function2 in module2 in a_package
```

`dir()` with no argument returns the names bound at the top of this file,
and the filter drops the dunder names every module carries.
The list shows that `import a_package.module1` binds the one name `a_package` in this file.
Loading `module1` also stores that submodule as an attribute of `a_package`,
so `a_package.module1.function1()` resolves.
The shorter `module1.function1()` raises a `NameError` here,
since `a_package` is the one name in the list.
`module1.function1()` works in `from_packages.py`, below,
where `from` binds `module1` in that file.

Importing the package alone leaves its submodules unloaded:

```python
# package_only.py
import a_package
from exceptions import expect

#: initializing a_package
expect(AttributeError, lambda: a_package.module1)  # type: ignore
#: [AttributeError] module 'a_package' has no attribute
#: 'module1'
```

The submodule becomes an attribute of the package only when something imports it by name.
The type checker reports the same missing attribute before the program runs,
flagging `a_package.module1` as a `possibly-missing-submodule`.
The `# type: ignore` silences that warning.

You can also specify the package with `from`:

```python
# from_packages.py
from a_package import module1, module2

#: initializing a_package
#: importing module1 in a_package
#: importing module2 in a_package
print(sorted(n for n in dir() if not n.startswith("__")))
#: ['module1', 'module2']
print(module1.function1())
#: function1 in module1 in a_package
print(module2.function2())
#: function2 in module2 in a_package
```

You can bring specific functions into the namespace by specifying both the package and the module:

```python
# no_qualification.py
from a_package.module1 import function1
from a_package.module2 import function2

#: initializing a_package
#: importing module1 in a_package
#: importing module2 in a_package
print(sorted(n for n in dir() if not n.startswith("__")))
#: ['function1', 'function2']
print(function1())
#: function1 in module1 in a_package
print(function2())
#: function2 in module2 in a_package
```

`no_qualification.py`, `from_packages.py`,
and `using_packages.py` print the same loading messages,
because `from` loads what `import` loads.
The whole module runs either way.
Each listing's import statement decides which names that listing binds,
so the `dir()` list differs in each of the three.

### Nested Packages

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

The listings so far import a package's modules from outside the package.
A package's own modules also import each other.
Inside the package, the leading dot of a *relative import* means "the package containing this module":

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

`module4` finds its sibling relative to its own package,
so the package's internal imports keep working after you rename the package.
A dotless `from module1 import function1` looks for a top-level module named `module1` on the [search path](#pythonpath),
the way `use_module.py` looks for `module`.
`module1.py` sits inside `a_package`, so with the dotless import,
`use_module4.py` stops with `ModuleNotFoundError: No module named 'module1'`.

Two dots refer to the parent package,
so `a_package/b_package/module3.py` could import from `a_package` with `from .. import module1` or `from ..module1 import function1`.
The absolute form `from a_package.module1 import function1` works from inside the package too.
Use it when the import crosses a package boundary,
since it spells out the full path from the top-level package.
Keep relative imports for a package's own submodules.

A relative import needs a package context.
A file run as a script becomes the top-level module `__main__`,
outside every package.
Running `python a_package/module4.py` raises `ImportError: attempted relative import with no known parent package`.
From the directory that holds `a_package`,
run it as `python -m a_package.module4` instead.

### Circular Imports

Two modules in a package can end up importing each other.
Python places the first one to load in `sys.modules` before its body finishes.
The first module's body has stopped at its `import` of the second,
so the names it defines below that line are still missing.
A `from` import in the second module then finds a partially initialized module and fails with `ImportError: cannot import name ... (most likely due to a circular import)`.
A plain `import` of that same module succeeds at this point,
since it needs the module to exist in `sys.modules`,
not to have finished running.
If the second module's top-level code uses one of the missing names,
Python raises an `AttributeError` there.

The "circular import" wording appears when the module's file lives outside the directory of the script you ran,
as every module inside a package does.
In the usual case, two modules sit beside your script,
in the directory that is the first entry of [`sys.path`](#pythonpath).
For a file there, Python's message names a possible collision with a library instead of a cycle:
`ImportError: cannot import name 'f' from 'modx' (consider renaming '.../modx.py' if it has the same name as a library you intended to import)`.
Python names the offending file by its full path, abbreviated here as `...`.

A cycle usually means the two modules share a piece of code.
Move the shared piece into a third module both can import.

When the cycle exists only in [annotations](08_Foundations--Static_Types.md#type-hints),
an `if TYPE_CHECKING:` import breaks it.
`typing.TYPE_CHECKING` is `False` at runtime,
so Python skips the import under it,
while the type checker reads the import as if the condition were true.
Importing the module succeeds,
because Python evaluates an annotation only when something reads it.

If code reads an annotation at runtime,
through `__annotations__` or `typing.get_type_hints()`,
and the annotation names a guarded import, Python raises a `NameError`.
The guard therefore suits names that appear in annotations alone.
[A robot in a maze](38_Patterns--Simulation.md#rooms-robots-and-the-item-factory)
imports `Room` that way, and every use of the name is an annotation.

## What a Module Exports

Every name at a module's top level is importable,
because Python has no `private` keyword.
A module states its boundary by convention and by one optional list.

A leading underscore marks a name as internal.
The mark informs a reader.
Python still grants access to an underscored name like any other.
For a module `accounting` that defines `_Engine`, `accounting._Engine` resolves,
and `from accounting import _Engine` works.
The underscore changes one mechanical thing:
`from accounting import *` skips every name that begins with one.

`__all__` lists the exports.
You assign it at module level as a list of strings naming the public names.
`from module import *` then binds every name on that list,
including one that begins with an underscore.
An `__all__` also gathers the public names into one readable place.
Documentation tools read it to report a module's public names.

```python
# exporting.py

__all__ = ["public", "_helper"]

def public():
    return "public"

def _helper():
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
#: ['_helper', 'public']
```

`undeclared` stays in `exporting` with `_internal`,
although its name looks public.

The `# noqa: F403` silences the linter's warning about the star import.
A star import hides the source of each name from a reader and from the tools.
Name what you import,
and keep the star for experiments at the interactive prompt.

The underscore and `__all__` both say which names a caller should use.
That stated boundary lets a module act as a [*Façade*](29_Patterns--Changing_the_Interface.md#façade)
over its internals.
Because every `import` of a module binds the one object cached in `sys.modules`,
a module is also a shared single instance
([*Singleton*](23_Patterns--Singleton.md#a-module-is-already-a-singleton)).

## File Names

To be the target of an `import` statement,
a module's file name must be a valid Python identifier and not a keyword.
`import my-mod` is a syntax error.
`importlib.import_module("my-mod")` loads the file.
Plugin loaders open oddly named files that way.
Give your own modules importable names.

**Modules** (`.py` files).
A module name is short and all-lowercase,
with underscores between words if that improves readability,
the style called `snake_case`.

- Good: `result.py`, `cache_singleton.py`, `list_comprehension.py`
- Avoid: `Result.py` (CapWords is for classes), `cacheSingleton.py` (camelCase),
  `cache-singleton.py` (hyphens aren't importable)

**Packages** (directories with `__init__.py`).
A package name is also short and all-lowercase,
but convention discourages underscores.
Prefer a single run-together word when you can.

- Good: `mypackage`, and underscores only when they aid readability
  (`a_package`)

**Tests** follow pytest's discovery convention: `test_*.py` (or `*_test.py`).
This book uses `test_*.py`, e.g. `test_result.py`.

Give your modules names that no standard library module uses.
A file named `random.py`, `string.py`,
or `weakref.py` can shadow the stdlib module,
so `import random` loads your file instead,
even inside a standard-library module,
because Python [searches the script's directory before the standard library](#pythonpath).

Give a shared module a distinctive name.
Python caches modules by name in `sys.modules`,
so the first `config.py` imported anywhere in the process is the module every later `import config` binds.

Windows and macOS default to case-insensitive filesystems,
so `module.py` and `Module.py` name the same file there.
Python's import system still matches names case-sensitively by default,
so `import module` raises a `ModuleNotFoundError` for a file saved as `Module.py`,
even on a filesystem that treats the two names as one.
`PYTHONCASEOK` turns that case check off, so `import module` finds `Module.py`.
A program that relies on that setting runs on Windows and macOS and raises a `ModuleNotFoundError` on Linux,
whose filesystems are case-sensitive.
Write a module's file name and its import in the same case,
so the import behaves the same on every filesystem.

## `PYTHONPATH`

Python searches `sys.path`, a list of directories it builds at startup.
`print(sys.path)` shows it.
Its first entry is the directory of the script you ran
(the current directory when you use `-m` or the REPL).
That entry lets `use_module.py` run `import module` with no setup.
The entries from `PYTHONPATH` come next, then the standard library,
and installed packages sit further down.
Running with `-P` drops that first entry,
so `import random` finds the standard library's module ahead of a local `random.py`.

What if your module or package lives in a different directory from the Python file that imports it?
The original solution was the `PYTHONPATH` environment variable,
which tells Python where to look for modules and packages.
`PYTHONPATH` takes multiple paths,
which Python adds to `sys.path` in the order given.
Python searches `sys.path` from the front and uses the first directory that holds your module or package.
It raises a `ModuleNotFoundError` when no directory does.

`PYTHONPATH` works, but today you install your package into the environment you use.
The install puts the package on the search path with no environment variable.
With `uv` (this book's tool of choice), you run `uv sync`,
or `uv pip install -e .` for an editable install.
The package resolves by name from anywhere,
and edits to its source take effect the next time you run a program that imports it.

## Lazy Imports

Every `import` so far runs the target module's top-level code immediately,
so importing `a_package.module1` prints its message as it loads.
That eager work slows the startup of a large program that imports many modules but uses only some of them on any given run.

Python 3.15 ([PEP 810](https://peps.python.org/pep-0810/))
adds the `lazy` soft keyword: a keyword only inside an `import` statement,
the way `match` is a keyword only inside a [`match` statement](04_Foundations--Control_Flow.md#pattern-matching).
A `lazy import` looks like an ordinary one with `lazy` in front.
It defers loading the module until the first time you use the imported name.
A run then loads only the modules it uses,
while all imports stay at the top of the file.
Once the module loads, its names behave like eagerly imported ones.

### Watching the Deferral

To see when `lazy` loads a module, give the module a body that prints a message:

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

The body of `noisy` runs at `noisy.announce()`, the first access,
so `noisy module loaded` prints after `before first use`.
If a lazily imported module is missing or broken,
Python raises the exception at that first use rather than at the import line.

The `from` form takes `lazy` too.
`lazy from noisy import announce` defers loading `noisy` until the first use of `announce`.

`sys.lazy_modules` holds the names still waiting to load.
Before your code runs, CPython loads standard-library modules,
and some of them add lazy imports of their own to that set:

```python
# lazy_modules_check.py
import sys
lazy from noisy import announce

print(len(sys.lazy_modules) > 1)
#: True
print("noisy" in sys.lazy_modules)
#: True
announce()
#: noisy module loaded
#: noisy.announce() called
print("noisy" in sys.lazy_modules)
#: False
```

This script marks one import lazy, yet the set holds more than one name.
`sys.lazy_modules` mixes the standard library's deferred imports with your program's deferred imports.
`noisy` leaves the set once `announce()` loads it,
so the set tracks names still waiting, not names your program ever deferred.
Check it for a specific name you marked lazy.

### Deferring an Import Before 3.15

Before 3.15, deferring a slow import meant moving it inside the function that needed it.
That works, but it hides the dependency.
The module's name moves from the top of the file into a function body,
where tools that read imports miss it.
The `import` statement also re-runs its `sys.modules` lookup on every call.
`lazy import` keeps the declaration at the top,
where a reader and a tool look for imports, and loads the module once,
at first use.

Before `lazy import` existed,
packages deferred submodule loading with a module-level `__getattr__()` in `__init__.py`
([PEP 562](https://peps.python.org/pep-0562/)).
That `__getattr__()` imports and returns a submodule the first time a caller asks for it by name.
NumPy and SciPy use that technique to keep import time low.
`lazy import` replaces the hand-written `__getattr__()` with one keyword and defers every imported name,
a package's submodules among them.
On a Python older than 3.15, code still needs the `__getattr__()` pattern.

### Limits of `lazy`

`lazy` works with both `import` and `from ... import`, but only at module level.
Using it inside a function, a class body, or a `try` block is a `SyntaxError`,
and Python likewise rejects `lazy from module import *` and a `lazy from __future__` import.

To change which imports are lazy for a whole run from outside the source,
run with `-X lazy_imports=MODE` or set `PYTHON_LAZY_IMPORTS=MODE`.
Both accept one of two values.
`normal`, the default, defers only the imports you marked `lazy`.
`all` defers every module-level import the keyword can mark.
The rest stay eager, such as an import inside a `try` block.
The PEP also describes a third value, `none`, which makes every import eager,
including the ones marked `lazy`.
CPython removed it before the 3.15 release.

Keep an import eager when you import a module for what its body does rather than for a name it defines.
A module that registers a [plugin class](26_Patterns--Factory.md#hazards-of-self-registration),
installs a codec, or fills a table does that work as it loads.
If nothing touches the lazily imported name,
the module stays unloaded for the rest of the run, so that work never happens.
The failure is silent.
The run finishes, and the table ends up one row short.
`all` defers ordinary `import` statements as well as the marked ones,
including the ones that exist to run a module's body.
The same silent failure therefore makes `all` an experiment to run rather than a setting to leave on.

## Exercises

Try each exercise before opening its [solution](../Solutions/06_Foundations--Modules_and_Packages/).

1.  Add a fourth module, `a_package/module5.py`,
    with its own `function5()` and a top-level `print()` so the module prints a message when it loads.
    Import it three ways, using `import a_package.module5`,
    `from a_package import module5`,
    and `from a_package.module5 import function5`,
    and confirm the loading message prints once,
    however many of the three you use together.
2.  Add `a_package/b_package/module6.py` with a `function6()` that calls `function5()` from `module5`.
    Import and call `function6()` from a script outside `a_package`,
    then rename `b_package` to `bPackage` (and rename it back afterward)
    and explain, from the conventions in [File Names](#file-names),
    why that name is a poor choice although the import still works.
3.  Write a small module `noisy2.py` whose top-level body prints a message,
    like `noisy.py`.
    In a new script, `lazy import` both `noisy` and `noisy2`,
    then use `noisy2` before `noisy`.
    Confirm the two loading messages print in the order you used the modules,
    not the order you wrote the `lazy import` lines.
4.  Rename `module.py` to `Module.py`,
    change `use_module.py` to `import Module`,
    and update its call to `Module.useful_function()`.
    Run it.
    Then change the import and its call back to `module`,
    leaving the file named `Module.py`, and run it again.
    Predict the result before you run it, then explain what you see,
    given that Windows and macOS open `module.py` and `Module.py` as the same file.
    Look up `PYTHONCASEOK` to confirm your explanation.
5.  Change `a_package/module4.py` to the absolute import `from a_package.module1 import function1` and confirm `use_module4.py` still works.
    Then run `python a_package/module4.py`, both before and after the change.
    Both fail, with different errors.
    Explain each, and say why `python -m a_package.module4` works either way.
6.  Remove the `__all__` line from `exporting.py`.
    Predict what `star_import.py` prints without it, run it to check,
    then restore the line.
7.  Give a module a top-level list, `plugins = []`,
    and bring the list into a script with `from ... import plugins`.
    Append to the list through the module's name,
    then print the script's `plugins`.
    Rebind the module's name to a new list, append to that one, and print both.
    Explain why the first change reaches the script's name and the second does not.
