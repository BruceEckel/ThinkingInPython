# two_levels.py
from a_package.b_package import module3

#: initializing a_package
#: initializing b_package
#: importing module3 in b_package
print(module3.function3())
#: function3 in module3 in b_package
