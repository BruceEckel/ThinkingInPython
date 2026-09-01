# Modules and Packages

Each Python file is a *module* you can `import` into another Python file.
If the file is in the same directory,
you can use an unqualified `import` statement:

```python
# module.py

def useful_function():
    return "I'm being useful!"
```

```python
# use_module.py
import module

print("'module' imported")

if __name__ == "__main__":
    print(module.useful_function())
#: 'module' imported
#: I'm being useful!
```

Importing a module makes its *namespace* reachable in the importing file,
under the module's name.
Reaching them through that name keeps the imported module's names from clashing with the local ones.
To call `useful_function()`, you must *qualify* it with the name of the module:
`module.useful_function()`.

The code at the end of `use_module.py` starts with an `if` clause that checks whether the standard variable `__name__` equals the string `"__main__"`.
In Python, any identifier that begins and ends with double underscores
(commonly called a "dunder") is special in some way.
Dunder methods, for example,
connect your class to the language's operators and built-in functions
(see [Classes](07_Foundations--Classes.md)).

The `if` exists because you can also use any file as a library module within another program.
In that case, you want its definitions and none of the code at the bottom of the file.
The condition is true only when you run this file directly.
That is, `__name__` is `"__main__"` when you use the command line:

```
python use_module.py
```

However, if another program imports `use_module.py` as a module,
`__name__` is `"use_module"` instead, so the `"__main__"` block does not run.
The next program only imports `use_module`:

```python
# import_module.py
import use_module
#: 'module' imported
```

Importing `use_module` runs its top-level code, including the `print()`,
but not its `"__main__"` block.
Python runs that code once, however many times the program imports the module:

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
The first `import` stores the finished module object in `sys.modules`,
a dict keyed by dotted module name.
Every later `import` of that name, from any file in the program,
finds it there and binds the same object instead of re-running the file,
so `use_module` and `second` are one object.
One consequence: editing a module's file changes nothing in a program that has already imported it.
Restart the program, or call `importlib.reload(use_module)`,
which re-runs the body into the existing module object.
Reloading leaves every name bound by a `from ... import` pointing at the old objects,
so restarting is the reliable choice.

To bring a name into the current namespace, use the `from` keyword:

```python
# using_from.py
from module import useful_function

if __name__ == "__main__":
    print(useful_function())
#: I'm being useful!
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
The local `debug` is a separate binding that `from` set once, at import,
so it still holds `False`.
Import the module and write `app_settings.debug` when the value can change.
Use `from ... import` for names that keep the same value,
such as functions and classes.

You can rename a module's namespace during an import with the `as` keyword:

```python
# using_as.py
import module as m

if __name__ == "__main__":
    print(m.useful_function())
#: I'm being useful!
```

A module's namespace is an ordinary dict you can read and write.
`globals()` returns it as a mutable `dict`,
the same dict Python already searches when it looks up a top-level name.
It is also the dict behind the dotted name:
`module.__dict__` from outside is the same object `globals()` returns inside `module`,
so `module.useful_function()` and a top-level lookup inside `module.py` find the same function.
Assigning into that dict works like writing the assignment directly:

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
Assigning into `globals()` matters whenever code needs to define a module-level name known only at runtime,
such as a class built dynamically and registered under a computed name
(see [Metaprogramming](17_Techniques--Metaprogramming.md)).

## Packages

As your programs get larger, you further organize your code into *packages*.
A package is a directory that contains multiple modules,
and it forms its own namespace with the name of that directory.

To make a directory a package, you put a special file named `__init__.py` in it.
`__init__.py` runs once, before any module inside the package loads.
An empty `__init__.py`, the common case,
only flags the directory as a package.^[The name `__init__.py` often confuses people. In hindsight, it might have been better to name the file `__package__.py`.]
One with content usually re-exports the package's public names,
so that `from a_package import function1` works and callers never learn which submodule defines `function1`.
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
so `a_package.module1.function1()` resolves.
The shorter `module1.function1()` fails here and works in `from_packages.py`,
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

`no_qualification.py`, `from_packages.py`,
and `using_packages.py` print the same loading messages,
because `from` loads exactly what `import` loads.
The whole module runs either way.
The statement decides only which names this file binds.

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
so `b_package/module3.py` could import from `a_package` that way.
The absolute form `from a_package.module1 import function1` works from inside the package too,
and is the better choice when the import crosses a package boundary.
Keep relative imports for a package's own submodules.

A relative import needs a package context, and a file run as a script has none.
Running `python a_package/module4.py` raises `ImportError: attempted relative import with no known parent package`.
Run it as `python -m a_package.module4` instead.

Two modules in a package can end up importing each other.
Python places the first one to load in `sys.modules` before its body finishes,
so a `from` import in the second finds a partially initialized module and fails with `ImportError: cannot import name ... (most likely due to a circular import)`.
A plain `import` of that same module succeeds at this point,
since it only needs the module to exist in `sys.modules`,
not to have finished running.
The failure then surfaces later,
wherever the code first uses a name the module has not defined yet.
A cycle is a design signal:
move the shared piece into a third module both can import.
When the cycle exists only in annotations,
an `if TYPE_CHECKING:` import breaks it,
because Python does not evaluate annotations at import time
(see [Simulation](38_Patterns--Simulation.md#a-robot-in-a-maze)).

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
An `__all__` also gathers the intended surface into one readable place,
and documentation tools read it when they ask what a module offers.

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
With it, only the listed names arrive,
and the star import skips `_internal` either way.

Neither mechanism stops `module._name`.
Both say which names a caller should use,
and that is enough to treat a module as a façade over its internals
([Changing the Interface](29_Patterns--Changing_the_Interface.md))
or as a shared single instance
([Singleton](24_Patterns--Singleton.md#a-module-is-already-a-singleton)).

## File Names

To be the target of an `import` statement,
a module's file name must be a valid Python identifier and not a keyword.
`import my-mod` is a syntax error.
(`importlib.import_module("my-mod")` still loads the file, and plugin loaders reach oddly named files that way, but choose an importable name anyway.)

**Modules** (`.py` files): short, all-lowercase,
with underscores between words if that improves readability,
the style called `snake_case`.

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
and that entry is why `use_module.py` can `import module` with no setup.
The entries from `PYTHONPATH` come next,
and installed packages sit further down.
Running with `-P` drops that first entry,
so a local `random.py` can no longer shadow the standard library.

What if your module or package isn't in the same directory as the Python file that imports it?
The original solution was the `PYTHONPATH` environment variable,
which tells Python where to look for modules and packages.
`PYTHONPATH` takes multiple paths,
and Python searches those paths in order until one holds your module or package,
or reports `ModuleNotFoundError` when none does.

`PYTHONPATH` still works,
but today you install your package into the environment you use,
and the install puts it on the search path with no environment variable.
Concretely, with `uv` (this book's tool of choice), that means `uv sync`,
or `uv pip install -e .` for an editable install.
The package resolves by name from anywhere,
and edits to its source take effect immediately, without reinstalling.

## Lazy Imports

Every `import` so far runs the target module's top-level code immediately,
and that is why importing `a_package.module1` printed its message as it loaded.
For a large program that imports many modules but uses only some of them on any given run,
that eager work slows startup.

Python 3.15 ([PEP 810](https://peps.python.org/pep-0810/))
adds the `lazy` soft keyword, a keyword only in an `import` statement,
as `match` is in [Control Flow](04_Foundations--Control_Flow.md#pattern-matching).
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
`json` and `pathlib` load at the `json.dumps` and `Path(...)` calls.
The output is the same either way, so this listing cannot show the deferral;
the next one does.

Before 3.15, deferring a costly import meant moving it inside the function that needed it.
That works, but it hides the dependency:
nothing at the top of the file mentions the module,
tools that read imports miss it,
and the `import` statement re-runs its `sys.modules` lookup on every call.
`lazy import` keeps the declaration at the top where a reader and a tool can see it,
and pays the loading cost once, at first use.
You can watch `lazy` defer the load by importing a module whose body prints when it runs:

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
so `noisy module loaded` prints after `before first use`.
If a lazily imported module is missing or broken,
the error surfaces at that first use rather than at the import line.
`sys.lazy_modules` holds the names still waiting to load,
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
The PEP also describes a third value, `none`, a global off switch.
CPython removed it before the 3.15 release.

Don't make an import lazy when you import a module for what its body does rather than for a name it defines.
A module that registers a plugin class
([Factory](27_Patterns--Factory.md#the-pythonic-factory-a-dictionary)),
installs a codec, or fills a table does that work as it loads,
and a lazily imported name nobody touches never loads.
The failure is silent: no error, just a table with a row missing.
That is also why `all` is an experiment to run rather than a setting to leave on,
since it defers ordinary `import` statements too,
including the ones whose only purpose is to run the module.

## Exercises

1.  Add a third module, `a_package/module5.py`,
    with its own `function5()` that prints a message when the module loads.
    Import it three ways, using `import a_package.module5`,
    `from a_package import module5`,
    and `from a_package.module5 import function5`,
    and confirm the loading message prints only once however many of the three you use together.
2.  Add `a_package/b_package/module6.py` with a `function6()` that calls `function5()` from `module5`.
    Import and call `function6()` from a script outside `a_package`,
    then rename `b_package` to `bPackage` (and rename it back afterward)
    and explain, from the rules in [File Names](#file-names),
    why that name is a poor choice even though the import still works.
3.  Write a small module `noisy2.py` whose top-level body prints a message,
    like `noisy.py`.
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
