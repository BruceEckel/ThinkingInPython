# throw_and_close_gotcha.py
from collections.abc import Generator

def stubborn() -> Generator[str]:
    try:
        yield "go"
    except GeneratorExit:
        yield "not done"

s = stubborn()
print(next(s))
#: go
try:
    s.close()
except RuntimeError as e:
    print(f"{type(e).__name__}: {e}")
#: RuntimeError: generator ignored GeneratorExit
