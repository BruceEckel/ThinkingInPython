# lazy_modules_check.py
import sys
lazy import noisy

print(len(sys.lazy_modules) > 1)
#: True
print("noisy" in sys.lazy_modules)
#: True
noisy.announce()
#: noisy module loaded
#: noisy.announce() called
print("noisy" in sys.lazy_modules)
#: False
