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
        answer = answers[request]
        print(f"{request = }, {answer = }")
        try:
            request = conversation.send(answer)
        except StopIteration as stop:
            return stop.value

def drive_naive(
        conversation: Generator[Question, Answer, Result],
        answers: Iterator[Answer]) -> Result:
    request = next(conversation)
    while True:
        try:  # Both next() calls share one except clause
            reply = next(answers)
            print(f"{request = }, {reply = }")
            request = conversation.send(reply)
        except StopIteration as stop:
            return stop.value

def drive_in_order(
        conversation: Generator[Question, Answer, Result],
        answers: Iterator[Answer]) -> Result:
    request = next(conversation)
    while True:
        # Fetched outside the try on purpose
        reply = next(answers)
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
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
in_order = iter([Answer("Alice"), Answer("Wonderland"),
                 Answer("Rabbit")])
print(drive_in_order(interview(), in_order))
#: request = 'name', reply = 'Alice'
#: request = 'town', reply = 'Wonderland'
#: request = 'friend', reply = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
# One answer, three questions:
try:
    drive_in_order(interview(), iter([Answer("Alice")]))
except StopIteration:
    print("answer source ran out")
#: request = 'name', reply = 'Alice'
#: answer source ran out
print(repr(drive_naive(interview(),
                       iter([Answer("Alice")]))))
#: request = 'name', reply = 'Alice'
#: None
