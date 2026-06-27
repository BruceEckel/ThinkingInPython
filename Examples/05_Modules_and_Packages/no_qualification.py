# no_qualification.py
from a_package.module1 import function1
from a_package.module2 import function2

#: importing module1 in a_package
#: importing module2 in a_package
print(function1())
#: function1 in module1 in a_package
print(function2())
#: function2 in module2 in a_package
