# monitoring_coverage.py
import sys
from collections import Counter
from types import CodeType
from typing import Final

monitoring = sys.monitoring
TOOL: Final[int] = monitoring.COVERAGE_ID
PY_START: Final[int] = monitoring.events.PY_START
NO_EVENTS: Final[int] = monitoring.events.NO_EVENTS
calls: Counter[str] = Counter()

def on_start(code: CodeType, offset: int) -> object:
    calls[code.co_name] += 1
    return monitoring.DISABLE

def used(n: int) -> int:
    return n + 1

def unused(n: int) -> int:
    return n - 1

monitoring.use_tool_id(TOOL, "coverage")
monitoring.register_callback(TOOL, PY_START, on_start)
monitoring.set_events(TOOL, PY_START)
print(sum(used(n) for n in range(1000)))
#: 500500
monitoring.set_events(TOOL, NO_EVENTS)
monitoring.free_tool_id(TOOL)
print(calls["used"], calls["unused"])
#: 1 0
