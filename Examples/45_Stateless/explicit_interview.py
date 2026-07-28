# explicit_interview.py
from collections.abc import Generator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name = yield Question("name")
    town = yield Question("town")
    return Result(f"{name} of {town}")

i = interview()
question: Question = next(i)
print(f"{question = }")
#: question = 'name'
question: Question = i.send(Answer("Alice"))
print(f"{question = }")
#: question = 'town'
try:
    i.send(Answer("Portland"))
except StopIteration as stop:
    result: Result = stop.value
    print(f"{result = }")
#: result = 'Alice of Portland'
