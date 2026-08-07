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
module the first time it is imported, in `sys.modules`, keyed by the
module's full dotted name. A later `import` of the same module, by any
of these spellings, finds the cached module and skips running its
top-level code again; it only binds a name to the module already in
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
own import runs while its body is executing, which is why the two
loading messages print before anything the script itself does.
The import crosses a package boundary, from `b_package` up to
`a_package`, so the absolute form is the right choice here. The
relative equivalent, `from ..module5 import function5`, works too and
is the form to prefer only for a package's own siblings.

Renaming the directory to `bPackage` and updating the imports to
`a_package.bPackage.module4` still runs. Nothing in the language
objects, since a package name only has to be a valid identifier. What
it costs is everything a convention buys:
[File Names](../Chapters/06_Modules_and_Packages.md#file-names) calls
for short, all-lowercase package names, so `bPackage` reads as a class
to anyone scanning an import line, and its capital letter is a
portability hazard on a case-insensitive filesystem, where
`import a_package.bpackage` would also succeed on Windows and then
fail on Linux.

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

Even though `noisy` is declared first, its body does not run until
`noisy.announce()` executes, which happens after `noisy2`'s. Each
`lazy import` only reserves the name; the module's top-level code runs
at the first genuine use of that name, whichever module that turns out
to be.

## 4. Renaming `module.py` to `Module.py`

`import Module` works, because the name and the file agree. Changing
the import back to `import module` while the file is still `Module.py`
raises `ModuleNotFoundError: No module named 'module'`, and it does so
on every platform, Windows and macOS included.

That is the part worth predicting wrongly first. Windows's NTFS and
macOS's default filesystem both open `module.py` and `Module.py` as the
same file, so the filesystem would happily hand Python the file under
either spelling. Python declines to accept it. Its import machinery
reads the directory listing and compares the module name against the
name on disk case-sensitively, so `"module" + ".py"` does not match the
stored `Module.py` and the search moves on.

This is deliberate, and [PEP 235](https://peps.python.org/pep-0235/)
says why: without it, a program written on Windows would import
happily there and fail the first time it ran on Linux, where the two
names really are different files. Making the case rule the same
everywhere turns a portability bug that surfaces in someone else's CI
into one that surfaces on your own machine.

Setting `PYTHONCASEOK` in the environment turns the check off on a
case-insensitive platform, and `import module` then finds `Module.py`.
It exists for legacy code and is not something to rely on; its
presence is what confirms the check is Python's rather than the
filesystem's.

None of this arises if you follow the convention.
[File Names](../Chapters/06_Modules_and_Packages.md#file-names)
recommends `snake_case` for modules, which sidesteps the whole question
by never mixing case in a module name to begin with.

## 5. Absolute imports and running a package module as a script

Changing `a_package/module4.py` to
`from a_package.module1 import function1` leaves `use_module4.py`
working exactly as before. Both forms find the same function; they
differ only in how they name it.

Running the module directly fails either way, with different errors.
With the relative import, `python a_package/module4.py` reports:

```text
ImportError: attempted relative import with no known parent package
```

A relative import is resolved against the module's `__package__`, and
a file run as a script has none: it is `__main__`, which belongs to no
package. There is no parent for the single dot to mean.

With the absolute import, the same command reports:

```text
ModuleNotFoundError: No module named 'a_package'
```

The name is now fully qualified, so the parent question does not
arise, but `sys.path[0]` is the directory of the script you ran, which
is `a_package/` itself. The project root is nowhere on the path, so
nothing can find a top-level package called `a_package`. Python is
inside the package looking for it.

`python -m a_package.module4` works with either form, and fixes both
problems at once. `-m` sets `sys.path[0]` to the current directory
rather than the script's, so `a_package` is findable, and it imports
the module as a member of its package rather than executing a loose
file, so `__package__` is set and the dot resolves.

The lesson is that a module inside a package is not a script. `-m` is
how you run one, and a file you intend to run both ways belongs at the
top level, outside any package.
