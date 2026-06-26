# exit_on_error.py
# __exit__ runs even when the body raises, before it propagates.
from trace_cm import Trace

try:
    with Trace("A"):
        raise ValueError("boom")
except ValueError as error:
    print("caught:", error)
## enter A
## exit A
## caught: boom
