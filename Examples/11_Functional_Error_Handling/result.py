# result.py
# A Result is either a Success holding an answer, or a Failure
# holding an error. Both are frozen, like the types in the Data
# Classes as Types chapter. bind chains steps: it feeds a Success
# into the next function, and passes a Failure straight through
# unchanged.

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


@dataclass(frozen=True)
class Failure[E]:
    error: E

    def bind[B](
        self, func: Callable[..., Result[B, E]]
    ) -> Failure[E]:
        return self  # Pass the failure forward unchanged.


type Result[A, E] = Success[A] | Failure[E]
