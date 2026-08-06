# Modules and Packages

Each Python file is a namespaced *module* you can `import` into another Python file.
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

Importing a module creates a *namespace* within the file that imports it.
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
In that case, you only want its definitions,
but you don't want the code at the bottom of the file to run.
This particular `if` statement is only true when you are running this file directly.
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

The message prints once even though the module is imported twice.
The first `import` stored the finished module object in `sys.modules`,
a dict keyed by dotted module name.
Every later `import` of that name, from any file in the program,
finds it there and binds the same object instead of re-running the file,
which is why `use_module` and `second` are one object.
A module's top-level code is a one-time setup step rather than something that runs per import.

To bring a name into the current namespace, use the `from` keyword:

```python
# using_from.py
from module import useful_function

if __name__ == "__main__":
    print(useful_function())
#: Use this elsewhere!
```

You can rename a module's namespace during an import using the `as` keyword:

```python
# using_as.py
import module as m

if __name__ == "__main__":
    print(m.useful_function())
#: Use this elsewhere!
```

A module's own namespace is concrete, not just a figure of speech.
`globals()` returns it as a mutable `dict`,
the same dict Python already searches when it looks up a top-level name.
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
It matters whenever code needs to define a module-level name that isn't known until runtime,
such as a class built dynamically and registered under a computed name.

## Packages

As your programs get larger, you'll further organize your code into *packages*.
A package is a directory that contains multiple modules,
and it forms its own namespace with the name of that directory.

To make something a package,
you put a special file named `__init__.py` in that directory.
Typically, there's no executable code in `__init__.py`.
It is only there to flag the directory as a package.^[The name `__init__.py` often confuses people. In hindsight, it might have been better to have named the file `__package__.py`.]
You can still import a directory without `__init__.py` as a *namespace package*,
but an explicit `__init__.py` makes the package's identity and boundary clear,
so this book uses one by default.

To explore this, create a directory called `a_package` and give it an `__init__.py` containing only a comment:

```python
# a_package/__init__.py
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

You can also name the package with `from`:

```python
# from_packages.py
from a_package import module1, module2

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

#: importing module1 in a_package
#: importing module2 in a_package
print(function1())
#: function1 in module1 in a_package
print(function2())
#: function2 in module2 in a_package
```

You can put a second package underneath the first one:

```python
# a_package/b_package/__init__.py
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

#: importing module3 in b_package
print(module3.function3())
#: function3 in module3 in b_package
```

### Imports Within a Package

The listings above import into a package from outside it.
A package's own modules also import each other,
and there the leading dot of a *relative import* means "the package this module lives in":

```python
# a_package/module4.py
from .module1 import function1

def function4():
    return f"function4 calls {function1()}"
```

```python
# use_module4.py
from a_package.module4 import function4

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

## File Names

To be importable, a module's file name must be a valid Python identifier:
letters, digits, and underscores, not starting with a digit, and not a keyword.
Any other name still runs as a script but can never be the target of an `import`.

**Modules** (`.py` files): short, all-lowercase,
with underscores between words if that improves readability.
This is `snake_case`.

- Good: `result.py`, `cache_singleton.py`, `list_comprehension.py`
- Avoid: `Result.py` (CapWords is for classes), `cacheSingleton.py` (camelCase),
  `cache-singleton.py` (hyphens aren't importable)

**Packages** (directories with `__init__.py`): also short and all-lowercase,
but underscores are discouraged.
Prefer a single run-together word when you can.

- Good: `mypackage`, and underscores only when they genuinely help (`a_package`)

**Tests** follow pytest's discovery convention: `test_*.py` (or `*_test.py`).
This book uses `test_*.py`, e.g. `test_result.py`.

Don't shadow standard-library modules.
A file named `random.py`, `types.py`,
or `weakref.py` can hide the stdlib one and break imports.

## `PYTHONPATH`

Python searches `sys.path`, a list of directories it builds at startup.
`print(sys.path)` shows it.
Its first entry is the directory of the script you ran,
which is why `use_module.py` could `import module` with no setup at all;
`PYTHONPATH` prepends its entries after that,
and installed packages sit further down.

What if your module or package isn't placed in the same directory as the Python file that's doing the importing?
The original solution to this was to set an environment variable called `PYTHONPATH`,
which tells Python where to look for modules and packages.
`PYTHONPATH` takes multiple paths,
and Python keeps searching through those paths until it finds your module or package
(or doesn't, and reports an error).

`PYTHONPATH` still works,
but the modern practice is to install your package into the environment you are working in,
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
while still declaring all imports at the top of the file:

```python
# lazy_imports.py
lazy import json
lazy from pathlib import Path

print(json.dumps({"a": 1}))
#: {"a": 1}
print(Path("report/data.txt").suffix)
#: .txt
```

Nothing loads at the `lazy import` lines,
and once loaded the names behave exactly like eagerly imported ones.
`json` and `pathlib` load on first use,
at the `json.dumps` and `Path(...)` calls.

Before 3.15, the way to defer a costly import was to move it inside the function that needed it.
That works, but it hides the dependency:
nothing at the top of the file says the module is used,
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

The body of `noisy` does not run at the `lazy import` line.
It runs at `noisy.announce()`, the first access,
which is why `noisy module loaded` prints after `before first use`.
If a lazily imported module is missing or broken,
the error surfaces at that first use rather than at the import line.

`lazy` works with both `import` and `from ... import`, but only at module scope.
Using it inside a function, a class body, or a `try` block is a `SyntaxError`,
and neither `lazy from module import *` nor a `lazy from __future__` import is allowed.
To make every import lazy without editing source,
run with `-X lazy_imports=all` or set `PYTHON_LAZY_IMPORTS=all`.
Both require a value: `all` defers every module-level import, and `normal`,
the default, defers only the imports you marked `lazy`.

## Exercises

1.  Add a third module, `a_package/module3.py`,
    with its own `function3()` that prints a message when the module loads.
    Import it three different ways, one each using `import a_package.module3`,
    `from a_package import module3`,
    and `from a_package.module3 import function3`,
    and confirm the loading message prints only once no matter how many of the three you use together.
2.  Add `a_package/b_package/module4.py` with a `function4()` that calls `function3()` from `module3`.
    Import and call `function4()` from a script outside `a_package`,
    then rename `b_package` to `bPackage` and explain,
    from the naming rules above,
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
    Explain the result, and say what would happen on a case-sensitive filesystem such as Linux's default.
