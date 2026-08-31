# exercise_5.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import final

@final
@dataclass(frozen=True)
class Ok[A]:
    answer: A

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        return func(self.answer)

@final
@dataclass(frozen=True)
class Err[E]:
    error: E

    def bind[B, F](
        self, func: Callable[..., Result[B, F]]
    ) -> Err[E]:
        return self

type Result[A, E] = Ok[A] | Err[E]

def load_setting(name: str,
                 text: str) -> Result[int, Exception]:
    try:
        return Ok(int(text))
    except ValueError as e:
        e.add_note(f"setting {name!r} received {text!r}")
        return Err(e)

def report(result: Result[int, Exception]) -> None:
    match result:
        case Ok(answer):
            print(f"ok: {answer}")
        case Err(error):
            print(f"failed: {type(error).__name__}")
            for note in error.__notes__:
                print(f"  {note}")

report(load_setting("timeout", "30").bind(
    lambda _: load_setting("retries", "3")))
#: ok: 3
report(load_setting("timeout", "soon").bind(
    lambda _: load_setting("retries", "3")))
#: failed: ValueError
#:   setting 'timeout' received 'soon'
report(load_setting("timeout", "30").bind(
    lambda _: load_setting("retries", "many")))
#: failed: ValueError
#:   setting 'retries' received 'many'
