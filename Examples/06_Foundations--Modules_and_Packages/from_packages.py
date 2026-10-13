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
