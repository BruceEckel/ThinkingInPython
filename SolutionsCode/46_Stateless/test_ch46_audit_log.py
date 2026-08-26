# test_ch46_audit_log.py
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable
from stateless import (Depend, Need, as_type, need,
                       run, supply)

@runtime_checkable
class Console(Protocol):
    def print(self, message: str) -> None: ...

@runtime_checkable
class Log(Protocol):
    def write(self, entry: str) -> None: ...

def greet(name: str) -> Depend[Need[Console], None]:
    console = yield from need(Console)
    console.print(f"Hello, {name}!")

def greet_logged(
    name: str,
) -> Depend[Need[Console] | Need[Log], None]:
    yield from greet(name)
    log = yield from need(Log)
    log.write(f"greeted {name}")

def greet_all(
    names: list[str],
) -> Depend[Need[Console] | Need[Log], None]:
    for name in names:
        yield from greet_logged(name)

@dataclass
class Recorder:
    printed: list[str] = field(default_factory=list)
    entries: list[str] = field(default_factory=list)

    def print(self, message: str) -> None:
        self.printed.append(message)

    def write(self, entry: str) -> None:
        self.entries.append(entry)

def test_greeting_and_logging_are_both_recorded() -> None:
    recorder = Recorder()
    environment = supply(
        as_type(Console)(recorder), as_type(Log)(recorder))
    run(environment(greet_all)(["Alice", "Bob"]))
    assert recorder.printed == ["Hello, Alice!",
                                "Hello, Bob!"]
    assert recorder.entries == ["greeted Alice",
                                "greeted Bob"]

recorder = Recorder()
run(supply(as_type(Console)(recorder),
           as_type(Log)(recorder))(greet_all)(["Cyd"]))
print(recorder.printed, recorder.entries)
#: ['Hello, Cyd!'] ['greeted Cyd']
