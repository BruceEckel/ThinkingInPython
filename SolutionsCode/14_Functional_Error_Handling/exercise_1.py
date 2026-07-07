# exercise_1.py
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

@dataclass(frozen=True)
class Failure[E]:
    error: E

    def bind[B](
        self, func: Callable[..., Result[B, E]]
    ) -> Failure[E]:
        return self  # Pass the failure forward unchanged

type Result[A, E] = Success[A] | Failure[E]

def func_a(i: int) -> Result[int, str]:
    if i == 1:
        return Failure(f"func_a({i})")
    return Success(i)

def func_b(i: int) -> Result[int, str]:
    if i == 2:
        return Failure(f"func_b({i})")
    return Success(i)

def func_c(i: int) -> Result[int, str]:
    try:
        1 / (i - 3)
    except ZeroDivisionError as e:
        return Failure(f"func_c({i}): {e}")
    return Success(i)

def func_e(i: int) -> Result[int, str]:
    if i == 4:
        return Failure(f"func_e({i})")
    return Success(i * 10)

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_c).bind(func_e)

for i in range(5):
    print(i, composed(i))
#: 0 Success(answer=0)
#: 1 Failure(error='func_a(1)')
#: 2 Failure(error='func_b(2)')
#: 3 Failure(error='func_c(3): division by zero')
#: 4 Failure(error='func_e(4)')
