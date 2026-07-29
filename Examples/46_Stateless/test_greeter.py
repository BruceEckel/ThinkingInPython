# test_greeter.py
from greeter import Console, greet
from recorder import Recorder
from stateless import as_type, run, supply

def test_greet() -> None:
    recorder = Recorder()
    console = as_type(Console)(recorder)
    run(supply(console)(greet)("Alice"))
    assert recorder.messages == ["Hello, Alice!"]
