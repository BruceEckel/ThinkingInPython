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
