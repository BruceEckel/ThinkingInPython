# Modules and Packages

Each Python file is a namespaced *module* that you can use inside another Python file by *importing* it.
If the file is in the same directory, you can use an unqualified `import` statement:

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

When you import a module, it creates a *namespace* within the importing file.
This automatically prevents name clashes between the imported module's names and the local ones.
To call `useful_function()`, you must *qualify* it with the name of the module:
`module.useful_function()`.

The code at the end of the file starts with an `if` clause which checks whether the standard variable `__name__` is equal to the string `"__main__"`.
In Python, any identifier that begins and ends with double underscores (commonly called a "dunder") is special in some way.
Dunder methods, for example, hook your class into the language's operators and built-in functions.

The reason for the `if` is that any file can also be used as a library module within another program.
In that case, you only want its definitions,
but you don't want the code at the bottom of the file to be executed.
This particular `if` statement is only true when you are running this file directly.
That is, `__name__` is `"__main__"` when you use the command line:

```
python use_module.py
```

However, if `use_module.py` is imported as a module into another program,
`__name__` will not be `"__main__"`, so its `"__main__"` code is not executed.
Here is such a program, which does nothing but import it:

```python
# import_module.py
import use_module
#: 'module' imported
```

If you run `python import_module.py`, you should only see `'module' imported`.
Importing `use_module` runs its top-level code, including the `print()`,
but not its `"__main__"` block.

To bring a name into the current namespace, use the `from` keyword:

```python
# using_from.py
from module import useful_function

if __name__ == "__main__":
    print(useful_function())
#: Use this elsewhere!
```

You can change the namespace of a module during an import using the `as` keyword:

```python
# using_as.py
import module as m

if __name__ == "__main__":
    print(m.useful_function())
#: Use this elsewhere!
```

## Packages

As your programs get larger, you'll further organize your code into *packages*.
A package is a directory that contains multiple modules,
and it forms its own namespace with the name of that directory.

To make something a package,
you put a special file named `__init__.py` in that directory.
Typically, there's no executable code in `__init__.py`.
It is only there to flag the directory as a package.^[People are often confused by the name `__init__.py`. In hindsight, it might have been better to have named the file `__package__.py`.]
A directory without `__init__.py` can still be imported as a *namespace package*,
but an explicit `__init__.py` makes the package's identity and boundary clear,
so this book always uses one.

To demonstrate, we'll create a directory called `a_package` and give it an `__init__.py` containing nothing but a comment:

```python
# a_package/__init__.py
```

Now we'll add two modules to the package:

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
print(a_package.module1.function1())
#: function1 in module1 in a_package
print(a_package.module2.function2())
#: function2 in module2 in a_package
```

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

We can even put a second package underneath the first one:

```python
# a_package/b_package/__init__.py
```

```python
# a_package/b_package/module3.py

print("importing module3 in b_package")

def function3():
    return "function3 in module3 in b_package"
```

To import `module3` we must specify both packages:

```python
# two_levels.py
from a_package.b_package import module3

#: importing module3 in b_package
print(module3.function3())
#: function3 in module3 in b_package
```

## File Names

A file name must be a valid identifier containing letters, digits, and underscores.
It cannot start with a digit.

**Modules** (`.py` files): short, all-lowercase, with underscores between words if that improves
readability. This is `snake_case`.

- Good: `result.py`, `cache_singleton.py`, `list_comprehension.py`
- Avoid: `Result.py` (CapWords is for classes), `cacheSingleton.py` (camelCase), `cache-singleton.py`
  (hyphens aren't importable)

**Packages** (directories with `__init__.py`): also short and all-lowercase, but underscores are
discouraged; prefer a single run-together word when you can.

- Good: `mypackage`, and underscores only when they genuinely help (`a_package`)

**Tests** follow pytest's discovery convention: `test_*.py` (or `*_test.py`). This book uses `test_*.py`,
  e.g. `test_result.py`.

Don't shadow standard-library modules. A file named `random.py`, `types.py`, or `weakref.py` can hide
the stdlib one and break imports.

## `PYTHONPATH`

What if your module or package isn't placed in the same directory as the Python file that's doing the importing?
The original solution to this was to set an environment variable called `PYTHONPATH`, which tells Python where to look for modules and packages.
`PYTHONPATH` can take multiple paths,
and Python will keep searching through those paths until it finds your module or package (or doesn't, and reports an error).

`PYTHONPATH` still works,
but the modern practice is to install your package into the environment you are working in,
which puts it on the search path without any environment variable.
Concretely, with `uv` (this book's tool of choice), that means `uv sync`,
or `uv pip install -e .` for an editable install:
the package resolves by name from anywhere, and edits to its source take effect immediately, without reinstalling.

## Lazy Imports

Every `import` so far runs the target module's top-level code immediately,
which is why importing `a_package.module1` earlier printed its message the moment
it was imported.
For a large program that imports many modules but uses only some of them on any
given run, that eager work slows startup.

Python 3.15 ([PEP 810](https://peps.python.org/pep-0810/)) adds the `lazy` soft
keyword.
A `lazy import` defers loading the module until the first time you use the
imported name, so you pay the cost only for what you actually use, while still
declaring all imports at the top of the file:

```python
# lazy_imports.py
lazy import json
lazy from pathlib import Path

# Once used, the names behave exactly like eager imports:
print(json.dumps({"a": 1}))
#: {"a": 1}
print(Path("report/data.txt").suffix)
#: .txt
```

Nothing is loaded at the `lazy import` lines; `json` and `pathlib` load on first
use, at the `json.dumps` and `Path(...)` calls.
You can watch the deferral by importing a module whose body prints when it runs:

```python
# noisy is a module whose top-level body prints when it executes
lazy import noisy

print("before first use")
noisy.announce()        # noisy's body runs here, on first access
print("after first use")
```

The body of `noisy` does not run at the `lazy import` line.
It runs at `noisy.announce()`, the first access, so the output is
`before first use`, then `noisy`'s own message, then `after first use`.
If a lazily imported module is missing or broken, the error surfaces at that
first use rather than at the import line.

`lazy` works with both `import` and `from ... import`, but only at module scope:
using it inside a function, a class body, or a `try` block is a `SyntaxError`,
and neither `lazy from module import *` nor a `lazy from __future__` import is
allowed.
To make every import lazy without editing source, use the `-X lazy_imports`
command-line option or the `PYTHON_LAZY_IMPORTS` environment variable.
