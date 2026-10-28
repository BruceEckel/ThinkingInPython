# Modules and Packages: Solutions

## 1. A fourth module, imported three ways

> Add a fourth module, `a_package/module5.py`,
> with its own `function5()` and a top-level `print()` so the module prints a message when it loads.
> Import it three ways, using `import a_package.module5`,
> `from a_package import module5`,
> and `from a_package.module5 import function5`,
> and confirm the loading message prints once,
> however many of the three you use together.

<details>
<summary>Where to look</summary>

[Packages](../../Chapters/06_Foundations--Modules_and_Packages.md#packages)
shows the three import forms and the messages each module prints as it loads.
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
<summary>Done when</summary>

a script holding all three imports prints `importing module5 in a_package` once,
after `initializing a_package`,
and then the result of `function5()` through each of the three names.
You can also name the cache that keeps the second and third imports from rerunning the module's top-level code.

<details>
<summary>Solution</summary>

The package's `__init__.py` is the one from the chapter:

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

Python caches every module in `sys.modules` on its first import,
keyed by the module's full dotted name.
A later `import` of the same module, in any of these forms,
takes the module from the cache instead of running its top-level code again,
and then binds the names it requests.
The package's `__init__.py` runs once for the same reason.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A nested module, and a badly named package

> Add `a_package/b_package/module6.py` with a `function6()` that calls `function5()` from `module5`.
> Import and call `function6()` from a script outside `a_package`,
> then rename `b_package` to `bPackage` (and rename it back afterward)
> and explain, from the conventions in [File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names),
> why that name is a poor choice although the import still works.

<details>
<summary>Where to look</summary>

[Imports Within a Package](../../Chapters/06_Foundations--Modules_and_Packages.md#imports-within-a-package)
covers a module that imports a sibling,
and [Nested Packages](../../Chapters/06_Foundations--Modules_and_Packages.md#nested-packages)
shows the two-level import.
`module6` imports `module5` from its parent package,
so write the import with its full `a_package.` path.
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
<summary>Done when</summary>

your script outside `a_package` prints `function6 calls function5 in module5 in a_package` after four loading messages,
the same script runs again with the directory renamed to `bPackage` and the import updated,
and you can cite the convention in File Names that the capital letter breaks.

<details>
<summary>Solution</summary>

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

**Import from the parent package.**
`module6` is in `b_package` and imports a module from `a_package`, its parent.
The import crosses a package boundary,
so the absolute form is the right choice here.
The relative equivalent, `from ..module5 import function5`, works too.
Keep the relative form for siblings within one package.

If you write the import as `from module5 import function5`,
dropping the `a_package.` prefix,
both packages initialize and then `use_module6.py` stops with `ModuleNotFoundError: No module named 'module5'`.
Python looks for a top-level `module5` on `sys.path`,
but `module5.py` sits one level down, inside the `a_package` directory.
The full dotted path names `module5` through the package that contains it,
so the solution writes `from a_package.module5 import function5`.

**Trace the load order.**
Python initializes both packages before it runs `module6`.
`module5` then loads before `module6` finishes loading,
because the import at the top of `module6` runs before the rest of its body.

After you rename the directory to `bPackage` and update the import to `a_package.bPackage.module6`,
the script still runs.
Python accepts any valid identifier as a package name,
so the rename breaks a convention, not a rule.

[File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names)
calls for short, all-lowercase package names,
so `bPackage` stands out as something other than a package to anyone scanning an import line.
Its capital letter also makes the name easy to mistype.
On a case-insensitive filesystem the shell and the editor accept `bpackage` as well,
but Python's import check compares case and rejects `bpackage`.
Exercise 4 examines that check.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Watching the Deferral](../../Chapters/06_Foundations--Modules_and_Packages.md#watching-the-deferral)
runs a `lazy import` of a module that prints when it loads.
A `lazy import` binds the name and defers running the module.
The body runs at the name's first use,
so order your uses and your `print()` calls to watch the messages appear.

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
<summary>Done when</summary>

your script prints `noisy2 module loaded` before `noisy module loaded`,
each directly ahead of the output of that module's first use,
while the `lazy import noisy` line still sits above `lazy import noisy2` in the file.

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

Each `lazy import` binds the name and defers the load.
The module's top-level code runs at the first use of that name, so use order,
not declaration order, decides which module loads first.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Renaming `module.py` to `Module.py`

> Rename `module.py` to `Module.py`,
> change `use_module.py` to `import Module`,
> and update its call to `Module.useful_function()`.
> Run it.
> Then change the import and its call back to `module`,
> leaving the file named `Module.py`, and run it again.
> Predict the result before you run it, then explain what you see,
> given that Windows and macOS open `module.py` and `Module.py` as the same file.
> Look up `PYTHONCASEOK` to confirm your explanation.

<details>
<summary>Where to look</summary>

[File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names)
explains how Python compares an import name with the file name on disk.
The filesystem may treat the two names as one file,
but the import system reads the directory listing and makes its own comparison.
The `PYTHONCASEOK` environment variable switches that comparison off,
so setting it tests your explanation.

<details>
<summary>Done when</summary>

you wrote a prediction before each run,
the `import Module` version prints `I'm being useful!`,
and you have the result of the `import module` run against `Module.py` on your own machine.
You can also say why the effect of setting `PYTHONCASEOK` shows which program compares the two names.

<details>
<summary>Solution</summary>

The `import Module` statement resolves, because the name and the file agree.
The call in `use_module.py` becomes `Module.useful_function()` to match.
Left as `module.useful_function()`, the call raises a `NameError`.
Changing the import back to `import module` while the file is still `Module.py` raises `ModuleNotFoundError: No module named 'module'. Did you mean: 'Module'?` on every platform,
Windows and macOS included.
The suggestion shows that `Module.py` sits on the search path under a name that differs in case alone.

Windows's NTFS and macOS's default filesystem both open `module.py` and `Module.py` as the same file,
so an open by either name succeeds.
Python checks the module name before it opens anything.
Its import machinery reads the directory listing and compares the module name against the name on disk case-sensitively.
To that comparison, `"module" + ".py"` and the stored `Module.py` differ,
so Python moves on to the next directory on `sys.path`.

The case check is deliberate, and [PEP 235](https://peps.python.org/pep-0235/)
says why.
Without the check, a program written on Windows imports cleanly there and fails the first time it runs on Linux,
where the two names really are different files.
Because the case rule is the same everywhere,
an import whose case differs from its file fails on your own machine instead of in someone else's CI.

Setting `PYTHONCASEOK` in the environment turns the check off on a case-insensitive platform,
so `import module` finds `Module.py`.
Because Python alone reads that variable, its effect confirms that Python,
not the filesystem, compares the names.
The variable exists for legacy code, so leave it unset in new code.

Following the naming convention prevents the mismatch.
[File Names](../../Chapters/06_Foundations--Modules_and_Packages.md#file-names)
recommends `snake_case` for modules.
With an all-lowercase name, an import and its file always match in case.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. Absolute imports and running a package module as a script

> Change `a_package/module4.py` to the absolute import `from a_package.module1 import function1` and confirm `use_module4.py` still works.
> Then run `python a_package/module4.py`, both before and after the change.
> Both fail, with different errors.
> Explain each, and say why `python -m a_package.module4` works either way.

<details>
<summary>Where to look</summary>

[Imports Within a Package](../../Chapters/06_Foundations--Modules_and_Packages.md#imports-within-a-package)
shows `module4`'s relative import,
and [`PYTHONPATH`](../../Chapters/06_Foundations--Modules_and_Packages.md#pythonpath)
describes where Python searches for top-level names.
A relative import needs the module's `__package__`.
A file run as a script has `__package__` set to `None`.
An absolute import needs the project root on `sys.path`.
The command you run decides the path's first entry.
Compare what `python file.py` and `python -m package.module` put there.

<details>
<summary>Done when</summary>

with the absolute import,
`use_module4.py` still prints `function4 calls function1 in module1 in a_package`,
you have a different error from `python a_package/module4.py` for each import form,
and `python -m a_package.module4` prints the two loading messages with either form.
You can tie each error to one thing a script run lacks.

<details>
<summary>Solution</summary>

Changing `a_package/module4.py` to `from a_package.module1 import function1` leaves `use_module4.py` working as before.
Both forms find the same function and differ in how they name it.

Running the module as a script fails either way, with different errors.
With the relative import, `python a_package/module4.py` reports:

```text
ImportError: attempted relative import with no known parent package
```

Python resolves a relative import against the module's `__package__`.
In a file run as a script, `__package__` is `None`,
since the file runs as `__main__`, a top-level module outside every package.
The single dot has no parent to name.

With the absolute import, the same command reports:

```text
ModuleNotFoundError: No module named 'a_package'. Did you mean: 'b_package'?
```

The name is now fully qualified, so Python resolves it from `sys.path` alone.
But `sys.path[0]` is the directory of the script you ran, `a_package/`,
so Python searches the `a_package/` directory for `a_package`.
With the project root nowhere on the path,
the search for a top-level package called `a_package` fails.
The suggestion names `b_package`, the name on the path closest to `a_package`.

`python -m a_package.module4` works with either form and fixes both problems at once.
`-m` sets `sys.path[0]` to the current directory rather than the script's directory,
so when you run it from the directory that holds `a_package`,
Python finds the package.
`-m` also imports the module as a member of its package rather than running the file by its path,
so `__package__` holds `a_package` and the dot resolves.

A module inside a package works only as a member of that package,
so run it with `-m`.
A file you intend to run with `python file.py` belongs at the top level,
outside any package.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 6. Star import without `__all__`

> Remove the `__all__` line from `exporting.py`.
> Predict what `star_import.py` prints without it, run it to check,
> then restore the line.

<details>
<summary>Where to look</summary>

[What a Module Exports](../../Chapters/06_Foundations--Modules_and_Packages.md#what-a-module-exports)
shows `from module import *` and the role `__all__` plays in it.
Without `__all__`, the star import falls back to a naming convention.
Copy `exporting.py` without the line and print what `dir()` reports after the import.

<details>
<summary>The shape</summary>

```python
# The shape of exporting_no_all.py
def public():
    ...

def _helper():
    ...

def _internal():
    ...

def undeclared():
    ...
```

<details>
<summary>Done when</summary>

you wrote your prediction before running,
`star_import.py` without the line prints a list that matches it and differs from `['_helper', 'public']` by two names,
and after you restore the line it prints `['_helper', 'public']` again.
You can name the rule that admitted or excluded each name.

<details>
<summary>Solution</summary>

```python
# exporting_no_all.py

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
# exercise_6.py
from exporting_no_all import *  # noqa: F403

print(sorted(n for n in dir() if not n.startswith("__")))
#: ['public', 'undeclared']
```

Without `__all__`, the star import falls back to the underscore convention.
The star import binds every top-level name that does not start with an underscore.
Restoring the `__all__` line limits the star import to `public` and `_helper` again.

When a module defines `__all__`, that list replaces the underscore convention.
The star import binds each listed name, leading underscore or not,
and leaves every other name in the module.
Without `__all__`, the underscore is the one way to keep a name out of a star import.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

In [Importing Names with `from` and `as`](../../Chapters/06_Foundations--Modules_and_Packages.md#importing-names-with-from-and-as),
`from_snapshot.py` shows an imported name keeping the value it had at import time.
A `from` import binds your name to the object, not to the module's name.
Compare mutating the list with rebinding the module's attribute,
and use `is` to check whether the two names still share one object.

<details>
<summary>Done when</summary>

after the first `append()` your script's `plugins` shows the new item,
an `is` comparison of the two names prints `True` before the rebinding and `False` after it,
and the script's `plugins` keeps only the first item once the module's new list grows.
Your explanation says which step changes an object and which changes a name.

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
plugin_list.plugins.append("word count")  # [1]
print(plugins, plugin_list.plugins)
#: ['spell check'] ['word count']
print(plugins is plugin_list.plugins)
#: False
```

**Share one list between two names.**
`from plugin_list import plugins` binds the script's `plugins` to the list the module's name references,
so at first the two names share one object.
Appending changes that object, so both names show the new item.

**Replace the module's list.**
The assignment `plugin_list.plugins = []` rebinds the module's name to a second list.
The `append()` at `[1]` goes through the module's name,
so it changes the second list.
The script's name still references the first list, which stays as it was.

`exercise_7.py` is `from_snapshot.py` with a mutable value.
The `from` import shares the module's object.
When a module may rebind a name to a new list or dict,
import the module and read the name through it each time,
as in `plugin_list.plugins`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
