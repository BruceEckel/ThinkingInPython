# utils/result.py
from collections.abc import Callable
from typing import final
from record import record

@final
@record
class Ok[A]:
    answer: A

    def unwrap(self) -> A:
        return self.answer

    def bind[B, E](
        self, func: Callable[[A], Result[B, E]]
    ) -> Result[B, E]:
        return func(self.answer)

@final
@record
class Err[E]:
    error: E

    def bind[B, F](
        self, func: Callable[..., Result[B, F]]
    ) -> Err[E]:
        return self  # Pass the failure forward unchanged

type Result[A, E] = Ok[A] | Err[E]
