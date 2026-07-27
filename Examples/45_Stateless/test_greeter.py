# test_greeter.py
from greeter import greet
from recorder import Recorder
from stateless import run, supply

def test_greet() -> None:
    recorder = Recorder()
    run(supply(recorder)(greet)("Alice"))
    assert recorder.messages == ["Hello, Alice!"]
