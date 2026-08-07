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
