# generator_interview.py
from collections.abc import Generator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name = yield Question("name")  # Ask the world for the name
    town = yield Question("town")  # Ask the world for the town
    return Result(f"{name} of {town}")

if __name__ == "__main__":
    i = interview()
    question1: Question = next(i)
    print(f"{question1 = }")
    question2: Question = i.send(Answer("Alice"))
    print(f"{question2 = }")
    try:
        i.send(Answer("Wonderland"))
    except StopIteration as stop:
        result: Result = stop.value
    print(f"{result = }")
#: question1 = 'name'
#: question2 = 'town'
#: result = 'Alice of Wonderland'
