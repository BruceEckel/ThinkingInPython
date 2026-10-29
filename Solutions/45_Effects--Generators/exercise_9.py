# exercise_9.py
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

def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer]) -> Result:
    try:
        request: Question = next(conversation)
    except StopIteration as stop:
        return stop.value
    while True:
        answer = answers[request]
        print(f"{request = }, {answer = }")
        try:
            request = conversation.send(answer)
        except StopIteration as stop:
            return stop.value

def proxy(
    inner: Generator[Question, Answer, Result],
    known: dict[Question, Answer],
) -> Generator[Question, Answer, Result]:
    return (yield from inner)

answers = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}
print(drive(
    proxy(interview(), {Question("town"): Answer("Oz")}),
    answers,
))
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
