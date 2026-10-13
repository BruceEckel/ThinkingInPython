# import_once.py
import sys
import use_module
import use_module as second

#: use_module body runs
print(use_module is second)
#: True
print(sys.modules["use_module"] is use_module)
#: True
