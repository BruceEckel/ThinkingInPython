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
This automatically prevents name clashes between the names in the imported module and the local names.
To call `useful_function()`, you must *qualify* it with the name of the module:
`module.useful_function()`.

The code at the end of the file starts with an `if` clause which checks to see if the standard variable `__name__` is equivalent to `__main__`.
In Python, any identifier that begins and ends with double underscores (commonly called "dunder") is special in some way.
Methods named with double underscores are *special methods*,
and they hook your class into the language's operators and built-in functions.

The reason for the `if` is that any file can also be used as a library module within another program.
In that case, you just want the classes defined,
but you don't want the code at the bottom of the file to be executed.
This particular `if` statement is only true when you are running this file directly.
That is, `__name__` is `__main__` when you use the command line:

```
python use_module.py
```

However, if `use_module.py` is imported as a module into another program,
`__name__` will not be `__main__`, so its `__main__` code is not executed.
Here is such a program, which does nothing but import it:

```python
# import_module.py
import use_module
#: 'module' imported
```

If you run `python import_module.py`, you should only see `'module' imported` displayed.
Importing `use_module` runs its top-level code, including the `print()`,
but not its `__main__` block.

If you want to bring a name into the current namespace,
you can do so using the `from` keyword:

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

As your programs get larger you'll want to further organize your code into *packages*.
A package is a directory (and its own namespace, which has the name of that directory) that can contain multiple modules.

To make something a package,
you put a special file named `__init__.py` in that directory.
Except in special cases, this file is empty;
it is only there to flag the directory as a package.^[People are often confused by the name `__init__.py`. In hindsight, it might have been better to have named the file `__package__.py`.]

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

## `PYTHONPATH`

What if your module or package isn't placed in the same directory as the Python file that's doing the importing?
The original (and now semi-deprecated) solution to this was to set an environment variable called `PYTHONPATH` which tells Python where to look for modules and packages.
`PYTHONPATH` can take multiple paths,
and Python will keep searching through those paths until it finds your module or package (or doesn't, and reports an error).

`PYTHONPATH` still works but has been effectively superseded by the *virtual environment*,
which solves much more than just "where are the modules and packages."
