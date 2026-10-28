# interview_generator.py
from collections.abc import Generator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield Question("name")
    town: Answer = yield Question("town")
    friend: Answer = yield Question("friend")
    return Result(f"{name} of {town}, friend {friend}")
