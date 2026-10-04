# Modules and Packages: Solutions

## 1. A fourth module, imported three ways

> Add a fourth module, `a_package/module5.py`,
> with its own `function5()` and a top-level `print()` so the module announces itself when it loads.
> Import it three ways, using `import a_package.module5`,
> `from a_package import module5`,
> and `from a_package.module5 import function5`,
> and confirm the loading message prints once,
> however many of the three you use together.

<details>
<summary>Where to look</summary>

[Packages](../../Chapters/06_Foundations--Modules_and_Packages.md#packages) shows the three import forms and the messages each module prints as it loads.
Python records every loaded module in `sys.modules` under its full dotted name.
Ask what a second `import` of a name in that cache does with the module's top-level code.

<details>
<summary>The shape</summary>

```python
# The shape of a_package/module5.py
def function5():
    ...
```

<details>
<summary>Solution</summary>

The package's `__init__.py` is the chapter's:

```python
# a_package/__init__.py

print("initializing a_package")
```

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

#: initializing a_package
#: importing module5 in a_package
print(a_package.module5.function5())
#: function5 in module5 in a_package
print(module5.function5())
#: function5 in module5 in a_package
print(function5())
#: function5 in module5 in a_package
```

The `"importing module5..."` message prints once, no matter how
many of the three import styles you combine. Python caches every
module in `sys.modules` on its first import, keyed by the module's
full dotted name. A later `import` of the same module, in any of
these forms, finds the cached module and skips running its top-level
code again. It binds a name to the module in the cache. The
package's `__init__.py` runs once for the same reason.

</details>
</details>
</details>

## 2. A nested module, and a badly named package

> Add `a_package/b_package/module6.py` with a `function6()` that calls `function5()` from `module5`.
> Import and call `function6()` from a script outside `a_package`,
> then rename `b_package` to `bPackage` (and rename it back afterward)
> and explain, from the rules in [File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names),
> why that name is a poor choice although the import still works.

<details>
<summary>Where to look</summary>

[Imports Within a Package](../../Chapters/06_Foundations--Modules_and_Packages.md#imports-within-a-package) covers a module that imports a sibling, and [Nested Packages](../../Chapters/06_Foundations--Modules_and_Packages.md#nested-packages) shows the two-level import.
`module6` reaches `module5` across a package boundary, so write the import with its full `a_package.` path.
For the rename, compare `bPackage` with the naming advice in [File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names).

<details>
<summary>The shape</summary>

```python
# The shape of a_package/b_package/module6.py
from a_package.module5 import function5

def function6():
    ...
```

<details>
<summary>Solution</summary>

If you write the import as `from module5 import function5`, dropping the `a_package.` prefix,
both packages initialize and then `use_module6.py` stops with `ModuleNotFoundError: No module named 'module5'`.
Python looks for a top-level `module5` on `sys.path`,
and no directory there holds a `module5.py`, because the file lives inside `a_package`.
The full dotted path names `module5` through the package that contains it,
so the solution writes `from a_package.module5 import function5`.

`b_package` keeps the chapter's `__init__.py` too:

```python
# a_package/b_package/__init__.py

print("initializing b_package")
```

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

#: initializing a_package
#: initializing b_package
#: importing module5 in a_package
#: importing module6 in b_package
print(function6())
#: function6 calls function5 in module5 in a_package
```

**Reach the parent package's module.** The import crosses a package boundary, from `b_package` up to
`a_package`, so the absolute form is the right choice here. The
relative equivalent, `from ..module5 import function5`, works too.
Prefer the relative form only for siblings within one package.

**Load the import chain first.** Python initializes both packages before it runs `module6`. `module5`
then loads before `module6` finishes loading, because `module6`'s
own import runs while its body is executing. All four messages
therefore print before the script's own `print()` runs.

After you rename the directory to `bPackage` and update the import to
`a_package.bPackage.module6`, the script still runs. Python accepts
any valid identifier as a package name. The rename gives up what
the convention provides.
[File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names) calls
for short, all-lowercase package names, so `bPackage` stands out as
something other than a package to anyone scanning an import line.
Its capital letter also makes the name easy to mistype: on a
case-insensitive filesystem the shell and the editor accept `bpackage`
as well, and Python's case-sensitive import check, the one
exercise 4 examines, rejects `bpackage`.

</details>
</details>
</details>

## 3. Lazy imports load in use order, not declaration order

> Write a small module `noisy2.py` whose top-level body prints a message,
> like `noisy.py`.
> In a new script, `lazy import` both `noisy` and `noisy2`,
> then use `noisy2` before `noisy`.
> Confirm the two loading messages print in the order you used the modules,
> not the order you wrote the `lazy import` lines.

<details>
<summary>Where to look</summary>

[Watching the Deferral](../../Chapters/06_Foundations--Modules_and_Packages.md#watching-the-deferral) runs a `lazy import` of a module that prints when it loads.
A `lazy import` binds the name without running the module.
The body runs when the name is first used, so order your uses and your `print()` calls to watch the messages appear.

<details>
<summary>The shape</summary>

```python
# The shape of noisy.py
def announce():
    ...
```

```python
# The shape of noisy2.py
def announce():
    ...
```

<details>
<summary>Solution</summary>

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
#: before any use
noisy2.announce()
#: noisy2 module loaded
#: noisy2.announce() called
print("between")
#: between
noisy.announce()
#: noisy module loaded
#: noisy.announce() called
print("after both")
#: after both
```

Although the `lazy import noisy` line comes first, `noisy`'s body does
not run until `noisy.announce()` executes, and that call comes after
`noisy2.announce()`. Each `lazy import` reserves the name. The module's
top-level code runs at the first use of that name, so use order, not
declaration order, decides which module loads first.

</details>
</details>
</details>

## 4. Renaming `module.py` to `Module.py`

> Rename `module.py` to `Module.py`,
> change `use_module.py` to `import Module`,
> and update its call to `Module.useful_function()`.
> Run it.
> Then change the import back to `import module`,
> leaving the file named `Module.py`, and run it again.
> Predict the result before you run it, then explain what you see,
> given that Windows and macOS open `module.py` and `Module.py` as the same file.
> Look up `PYTHONCASEOK` to confirm your explanation.

<details>
<summary>Where to look</summary>

[File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names) explains how Python compares an import name with the file name on disk.
The filesystem may treat the two names as one file, but the import system reads the directory listing and decides for itself.
The `PYTHONCASEOK` environment variable switches that comparison off, which tests your explanation.

<details>
<summary>Solution</summary>

The `import Module` statement resolves, because the name and the file
agree, and the call in the body becomes `Module.useful_function()` to
match; left as `module.useful_function()`, the call raises a `NameError`.
Changing the import back to `import module` while the file is still
`Module.py` raises
`ModuleNotFoundError: No module named 'module'. Did you mean: 'Module'?`,
and it does so on every platform, Windows and macOS included. The
suggestion shows that Python found the file and declined it.

The failure on Windows and macOS is the surprising part. Windows's
NTFS and macOS's default filesystem both open `module.py` and
`Module.py` as the same file, so the filesystem would hand Python
the file under either name. Python declines it.
Its import machinery reads the directory listing and compares the
module name against the name on disk case-sensitively, so
`"module" + ".py"` does not match the stored `Module.py` and the
search moves on.

The case check is deliberate, and
[PEP 235](https://peps.python.org/pep-0235/) says why: without it, a
program written on Windows imports happily there and fails the first
time it runs on Linux, where the two names really are different
files. Making the case rule the same everywhere turns a portability
bug that surfaces in someone else's CI into one that surfaces on your
own machine.

Setting `PYTHONCASEOK` in the environment turns the check off on a
case-insensitive platform, and `import module` then finds `Module.py`.
The variable exists for legacy code. Leave it unset in new code.
A Python environment variable turns the check off, so the check is
Python's rather than the filesystem's.

None of this arises if you follow the convention.
[File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names)
recommends `snake_case` for modules, and with an all-lowercase name,
an import and its file cannot differ in case.

</details>
</details>

## 5. Absolute imports and running a package module as a script

> Change `a_package/module4.py` to the absolute import `from a_package.module1 import function1` and confirm `use_module4.py` still works.
> Then run `python a_package/module4.py` directly,
> both before and after the change.
> Both fail, with different errors: explain each,
> and say why `python -m a_package.module4` works either way.

<details>
<summary>Where to look</summary>

[Imports Within a Package](../../Chapters/06_Foundations--Modules_and_Packages.md#imports-within-a-package) shows `module4`'s relative import, and [`PYTHONPATH`](../../Chapters/06_Foundations--Modules_and_Packages.md#pythonpath) describes where Python searches for top-level names.
A relative import needs the module's `__package__`, and a file run as a script has none.
An absolute import needs the project root on `sys.path`, which depends on the source of the first entry.
Compare what `python file.py` and `python -m package.module` put there.

<details>
<summary>Solution</summary>

Changing `a_package/module4.py` to
`from a_package.module1 import function1` leaves `use_module4.py`
working as before. Both forms find the same function. They
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
ModuleNotFoundError: No module named 'a_package'. Did you mean: 'b_package'?
```

The name is now fully qualified, so the parent question does not
arise. But `sys.path[0]` is the directory of the script you ran,
`a_package/`. The project root is nowhere on the path, so the
search for a top-level package called `a_package` fails: Python is
inside the package, looking for it. The suggestion names `b_package`,
the one package Python does find on that path.

`python -m a_package.module4` works with either form, and fixes both
problems at once. `-m` sets `sys.path[0]` to the current directory
rather than the script's, so `a_package` is findable. It also imports
the module as a member of its package rather than running a loose
file, so `__package__` holds `a_package` and the dot resolves.

A module inside a package is not a script. `-m` is how you run a
package module, and a file you intend to run both ways belongs at the
top level, outside any package.

</details>
</details>

## 6. Star import without `__all__`

> Remove the `__all__` line from `exporting.py`.
> Predict what `star_import.py` prints without it, run it to check,
> then restore the line.

<details>
<summary>Where to look</summary>

[What a Module Exports](../../Chapters/06_Foundations--Modules_and_Packages.md#what-a-module-exports) shows `from module import *` and the role `__all__` plays in it.
Without `__all__`, the star import falls back to a naming convention.
Copy `exporting.py` without the line, add a name of your own, and print what `dir()` reports after the import.

<details>
<summary>The shape</summary>

```python
# The shape of exporting_no_all.py
def public():
    ...

def helper():
    ...

def _internal():
    ...

def undeclared():
    ...
```

<details>
<summary>Solution</summary>

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
`helper`, and `_internal` stays out. Restoring the `__all__` line
shrinks the surface back to `public` and `helper`. `__all__` and the
underscore convention compose in one direction only:
`__all__` can export an underscored name, but without
`__all__` an underscore is the only way to keep a name out of a star
import.

</details>
</details>
</details>

## 7. A `from` import shares the object, not the name

> Give a module a top-level list, `plugins = []`,
> and bring the list into a script with `from ... import plugins`.
> Append to the list through the module's name,
> then print the script's `plugins`.
> Rebind the module's name to a new list, append to that one, and print both.
> Explain why the first change reaches the script's name and the second does not.

<details>
<summary>Where to look</summary>

In [Importing Names with `from` and `as`](../../Chapters/06_Foundations--Modules_and_Packages.md#importing-names-with-from-and-as), `from_snapshot.py` shows an imported name keeping the value it had at import time.
A `from` import binds your name to the object, not to the module's name.
Compare mutating the list with rebinding the module's attribute, and use `is` to check whether the two names still share one object.

<details>
<summary>Solution</summary>

```python
# plugin_list.py

plugins = []
```

```python
# exercise_7.py
import plugin_list
from plugin_list import plugins

plugin_list.plugins.append("spell check")
print(plugins)
#: ['spell check']
print(plugins is plugin_list.plugins)
#: True
plugin_list.plugins = []
plugin_list.plugins.append("word count")
print(plugins, plugin_list.plugins)
#: ['spell check'] ['word count']
print(plugins is plugin_list.plugins)
#: False
```

**Share one list between two names.** `from plugin_list import plugins` binds the script's `plugins` to the
list the module's name references, so at first the two names share one
object. Appending changes that object, and both names show the new
item.

**Replace the module's list.** The assignment `plugin_list.plugins = []` rebinds the module's
name to a second list and leaves the script's name on the first, so
the second `append()` reaches a list to which the script's `plugins`
does not refer.

`exercise_7.py` is `from_snapshot.py` with a mutable value: the
`from` import takes no copy, and it does not follow the module's
name when that name moves. When a module's name can move to a new
list or dict, import the module and read `plugin_list.plugins` each
time.

</details>
</details>
