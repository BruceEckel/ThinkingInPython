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
