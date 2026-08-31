# import_once.py
import sys
import use_module
import use_module as second

#: 'module' imported
print(use_module is second)
#: True
print(sys.modules["use_module"] is use_module)
#: True
