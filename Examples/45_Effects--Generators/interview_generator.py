# interview_generator.py
from collections.abc import Generator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name = yield Question("name")
    town = yield Question("town")
    friend = yield Question("friend")
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    conversation = interview()
    question1: Question = next(conversation)
    print(f"{question1 = }")
    question2: Question = conversation.send(Answer("Alice"))
    print(f"{question2 = }")
    question3: Question = conversation.send(
        Answer("Wonderland"))
    print(f"{question3 = }")
    try:
        conversation.send(Answer("Rabbit"))
    except StopIteration as stop:
        result: Result = stop.value
    print(f"{result = }")
#: question1 = 'name'
#: question2 = 'town'
#: question3 = 'friend'
#: result = 'Alice of Wonderland, friend Rabbit'
