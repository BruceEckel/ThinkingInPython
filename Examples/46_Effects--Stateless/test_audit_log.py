# test_audit_log.py
import pytest
from audit_log import Log, greet_all
from greeter import Console
from recorder import Recorder
from stateless import as_type, run, supply

@pytest.mark.parametrize("console", [
    Console(), as_type(Console)(Recorder())])
def test_greet_all(console: Console) -> None:
    log = Log()
    run(supply(console, log)(greet_all)(["Alice"]))
    assert log.entries == ["greeted Alice"]
