# jit_status.py
import sys

def jit_state() -> str:
    if not sys._jit.is_available():
        return "no JIT in this build"
    if not sys._jit.is_enabled():
        return "JIT built in, switched off"
    return "JIT enabled"

print(sys._jit.is_available() or not sys._jit.is_enabled())
#: True
print(jit_state())
