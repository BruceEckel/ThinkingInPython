# ch18_jit_probe.py
import sys

print(sys._jit.is_available(), sys._jit.is_enabled())
#: False False
