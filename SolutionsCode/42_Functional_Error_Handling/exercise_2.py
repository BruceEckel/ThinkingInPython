# exercise_2.py
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Ok[A]:
    answer: A

    def unwrap(self) -> A:
        return self.answer

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        return func(self.answer)

    def map_error(self, func: Callable[..., object]) -> Ok[A]:
        return self  # An Ok has no error to transform

@dataclass(frozen=True)
class Err[E]:
    error: E

    def bind[B](
        self, func: Callable[..., Result[B, E]]
    ) -> Err[E]:
        return self

    def map_error[F](self, func: Callable[[E], F]) -> Err[F]:
        return Err(func(self.error))

type Result[A, E] = Ok[A] | Err[E]

def prefix(msg: str) -> str:
    return f"error: {msg}"

print(Ok(5).map_error(prefix))
#: Ok(answer=5)
print(Err("boom").map_error(prefix))
#: Err(error='error: boom')
