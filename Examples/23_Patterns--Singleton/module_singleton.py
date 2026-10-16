# module_singleton.py
import sys
import config  # [1]
import config as again  # [2]

#: config body runs
print(config is again is sys.modules["config"])
#: True
