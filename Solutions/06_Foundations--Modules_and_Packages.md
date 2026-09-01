# Modules and Packages: Solutions

## 1. A third module, imported three ways

```python
# a_package/module5.py
print("importing module5 in a_package")

def function5():
    return "function5 in module5 in a_package"
```

```python
# use_module5.py
import a_package.module5
from a_package import module5
from a_package.module5 import function5

print(a_package.module5.function5())
print(module5.function5())
print(function5())
#: importing module5 in a_package
#: function5 in module5 in a_package
#: function5 in module5 in a_package
#: function5 in module5 in a_package
```

The `"importing module5..."` message prints only once, no matter how
many of the three import styles you combine. Python caches every
module in `sys.modules` on its first import, keyed by the module's
full dotted name. A later `import` of the same module, by any
of these spellings, finds the cached module and skips running its
top-level code again. It only binds a name to the module already in
the cache.

## 2. A nested module, and a badly named package

```python
# a_package/b_package/module6.py
from a_package.module5 import function5

print("importing module6 in b_package")

def function6():
    return f"function6 calls {function5()}"
```

```python
# use_module6.py
from a_package.b_package.module6 import function6

print(function6())
#: importing module5 in a_package
#: importing module6 in b_package
#: function6 calls function5 in module5 in a_package
```

`module5` loads before `module6` finishes loading, because `module6`'s
own import runs while its body is executing. Both loading messages
therefore print before the script's own `print()` runs.
The import crosses a package boundary, from `b_package` up to
`a_package`, so the absolute form is the right choice here. The
relative equivalent, `from ..module5 import function5`, works too.
Prefer that form only for siblings within one package.

After you rename the directory to `bPackage` and update the import to
`a_package.bPackage.module6`, the script still runs. Python accepts
any valid identifier as a package name. The rename costs everything
the convention buys.
[File Names](../Chapters/06_Foundations--Modules_and_Packages.md#file-names) calls
for short, all-lowercase package names, so `bPackage` reads as a class
to anyone scanning an import line. Its capital letter also adds a
spelling to get wrong: on a case-insensitive filesystem the shell and
the editor accept `bpackage` as well, and only Python's case-sensitive
import check, the one exercise 4 examines, rejects that spelling.

## 3. Lazy imports load in use order, not declaration order

```python
# noisy.py
print("noisy module loaded")

def announce():
    print("noisy.announce() called")
```

```python
# noisy2.py
print("noisy2 module loaded")

def announce():
    print("noisy2.announce() called")
```

```python
# lazy_demo.py
lazy import noisy
lazy import noisy2

print("before any use")
noisy2.announce()
print("between")
noisy.announce()
print("after both")
#: before any use
#: noisy2 module loaded
#: noisy2.announce() called
#: between
#: noisy module loaded
#: noisy.announce() called
#: after both
```

Even though the `lazy import noisy` line comes first, `noisy`'s body
does not run until `noisy.announce()` executes, and that call comes
after `noisy2.announce()`. Each `lazy import` only reserves the name.
The module's top-level code runs at the first genuine use of that
name, so use order, not declaration order, decides which module loads
first.

## 4. Renaming `module.py` to `Module.py`

`import Module` works, because the name and the file agree. Changing
the import back to `import module` while the file is still `Module.py`
raises `ModuleNotFoundError: No module named 'module'`, and it does so
on every platform, Windows and macOS included.

The failure on Windows and macOS is the surprising part. Windows's
NTFS and macOS's default filesystem both open `module.py` and
`Module.py` as the same file, so the filesystem would happily hand
Python the file under either spelling. Python declines to accept it.
Its import machinery reads the directory listing and compares the
module name against the name on disk case-sensitively, so
`"module" + ".py"` does not match the stored `Module.py` and the
search moves on.

The case check is deliberate, and
[PEP 235](https://peps.python.org/pep-0235/) says why: without it, a
program written on Windows would import happily there and fail the
first time it ran on Linux, where the two names really are different
files. Making the case rule the same everywhere turns a portability
bug that surfaces in someone else's CI into one that surfaces on your
own machine.

Setting `PYTHONCASEOK` in the environment turns the check off on a
case-insensitive platform, and `import module` then finds `Module.py`.
The variable exists for legacy code. New code should leave it unset.
That the switch exists at all confirms the check is Python's rather
than the filesystem's.

None of this arises if you follow the convention.
[File Names](../Chapters/06_Foundations--Modules_and_Packages.md#file-names)
recommends `snake_case` for modules, and an all-lowercase name has
only one spelling for the check to match.

## 5. Absolute imports and running a package module as a script

Changing `a_package/module4.py` to
`from a_package.module1 import function1` leaves `use_module4.py`
working exactly as before. Both forms find the same function. They
differ only in how they name it.

Running the module directly fails either way, with different errors.
With the relative import, `python a_package/module4.py` reports:

```text
ImportError: attempted relative import with no known parent package
```

Python resolves a relative import against the module's `__package__`,
and a file run as a script has none: it runs as `__main__`, which
belongs to no package. The single dot has no parent to name.

With the absolute import, the same command reports:

```text
ModuleNotFoundError: No module named 'a_package'
```

The name is now fully qualified, so the parent question does not
arise. But `sys.path[0]` is the directory of the script you ran,
`a_package/` itself. The project root is nowhere on the path, so the
search for a top-level package called `a_package` fails: Python is
inside the package, looking for it.

`python -m a_package.module4` works with either form, and fixes both
problems at once. `-m` sets `sys.path[0]` to the current directory
rather than the script's, so `a_package` is findable. It also imports
the module as a member of its package rather than running a loose
file, so `__package__` holds `a_package` and the dot resolves.

A module inside a package is not a script. `-m` is how you run a
package module, and a file you intend to run both ways belongs at the
top level, outside any package.

## 6. Star import without `__all__`

```python
# exporting_no_all.py

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
# exercise_6.py
from exporting_no_all import *  # noqa: F403

print(sorted(n for n in dir() if not n.startswith("__")))
#: ['helper', 'public', 'undeclared']
```

Without `__all__`, the star import falls back to the underscore
convention: every top-level name that does not start with an
underscore arrives. `undeclared` therefore joins `public` and
`helper`, and `_internal` stays out. Restoring the line shrinks the
surface back to the two listed names. The two rules compose in one
direction only: `__all__` can export an underscored name, but without
`__all__` an underscore is the only way to keep a name out of a star
import.
