# exercise_2.py
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Success[A]:
    answer: A

    def unwrap(self) -> A:
        return self.answer

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        return func(self.answer)

    def map_error(self, func: Callable[..., object]) -> Success[A]:
        return self  # A Success has no error to transform

@dataclass(frozen=True)
class Failure[E]:
    error: E

    def bind[B](
        self, func: Callable[..., Result[B, E]]
    ) -> Failure[E]:
        return self

    def map_error[F](self, func: Callable[[E], F]) -> Failure[F]:
        return Failure(func(self.error))

type Result[A, E] = Success[A] | Failure[E]

def prefix(msg: str) -> str:
    return f"error: {msg}"

print(Success(5).map_error(prefix))
#: Success(answer=5)
print(Failure("boom").map_error(prefix))
#: Failure(error='error: boom')
