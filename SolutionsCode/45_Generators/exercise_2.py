# exercise_2.py
from collections.abc import Generator, Iterator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def interview() -> Generator[Question, Answer, Result]:
    name = yield Question("name")
    town = yield Question("town")
    friend = yield Question("friend")
    return Result(f"{name} of {town}, friend {friend}")

def drive_from_dict(
        conversation: Generator[Question, Answer, Result],
        answers: dict[Question, Answer]) -> Result:
    request = next(conversation)
    while True:
        print(f"{request = }, {answers[request] = }")
        try:
            request = conversation.send(answers[request])
        except StopIteration as stop:
            return stop.value

def drive_in_order(
        conversation: Generator[Question, Answer, Result],
        answers: Iterator[Answer]) -> Result:
    request = next(conversation)
    while True:
        reply = next(answers)  # Fetched outside the try on purpose
        print(f"{request = }, {reply = }")
        try:
            request = conversation.send(reply)
        except StopIteration as stop:
            return stop.value

by_name = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}
print(drive_from_dict(interview(), by_name))
#: request = 'name', answers[request] = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
in_order = iter([Answer("Alice"), Answer("Wonderland"),
                 Answer("Rabbit")])
print(drive_in_order(interview(), in_order))
#: request = 'name', reply = 'Alice'
#: request = 'town', reply = 'Wonderland'
#: request = 'friend', reply = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
