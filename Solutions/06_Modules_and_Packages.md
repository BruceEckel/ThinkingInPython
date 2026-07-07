# Modules and Packages: Solutions

## 1. A third module, imported three ways

```python
# a_package/module3.py
print("importing module3 in a_package")

def function3():
    return "function3 in module3 in a_package"
```

```python
# use_module3.py
import a_package.module3
from a_package import module3
from a_package.module3 import function3

print(a_package.module3.function3())
print(module3.function3())
print(function3())
#: importing module3 in a_package
#: function3 in module3 in a_package
#: function3 in module3 in a_package
#: function3 in module3 in a_package
```

The `"importing module3..."` message prints only once, no matter how
many of the three import styles you combine. Python caches every
module the first time it is imported, in `sys.modules`, keyed by the
module's full dotted name. A later `import` of the same module, by any
of these spellings, finds the cached module and skips running its
top-level code again; it only binds a name to the module already in
the cache.

## 2. Importing an already-imported module a second time

Adding a second `import a_package.module1` at the bottom of
`using_packages.py` produces no new `"importing module1..."` message.
This is the same caching behavior as exercise 1: the first `import
a_package.module1` at the top of the file already ran `module1`'s
top-level code and cached the result. Every subsequent `import
a_package.module1` anywhere in the same process, even from a
different file, finds the cached module and does nothing further.

## 3. Lazy imports load in use order, not declaration order

```python
# noisy.py
print("noisy module body running")

def announce():
    print("noisy announces!")
```

```python
# noisy2.py
print("noisy2 module body running")

def announce():
    print("noisy2 announces!")
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
#: noisy2 module body running
#: noisy2 announces!
#: between
#: noisy module body running
#: noisy announces!
#: after both
```

Even though `noisy` is declared first, its body does not run until
`noisy.announce()` executes, which happens after `noisy2`'s. Each
`lazy import` only reserves the name; the module's top-level code runs
at the first genuine use of that name, whichever module that turns out
to be.

## 4. Renaming `module.py` to `Module.py`

Renaming the file to `Module.py` and updating `use_module.py` to
`import Module` still works on this machine, because Windows's default
filesystem (NTFS) treats file names case-insensitively: `Module.py`
and `module.py` name the same file as far as the filesystem is
concerned, so `import Module` finds it regardless of the case used at
the import site.

On a case-sensitive filesystem, which is the default on Linux (and can
be enabled on macOS), `Module.py` and `module.py` are two distinct,
unrelated file names. `import module` would then raise
`ModuleNotFoundError`, because no file matching that exact,
lowercase name exists; only `import Module` would work. Relying on
case-insensitive matching is a portability trap: code that imports
happen to work on Windows can fail the moment it runs on Linux CI.
This is also why [File Names](#file-names) recommends `snake_case` for
modules: it sidesteps the whole question by never mixing case in a
module name to begin with.
