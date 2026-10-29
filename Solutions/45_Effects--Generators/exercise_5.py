# exercise_5.py
from collections.abc import Generator
from typing import NewType

Question = NewType("Question", str)
Answer = NewType("Answer", str)
Result = NewType("Result", str)

def ask(
    question: Question
) -> Generator[Question, Answer, Answer]:
    answer: Answer = yield question
    return answer

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield from ask(Question("name"))
    town: Answer = yield from ask(Question("town"))
    return Result(f"{name} of {town}")

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

def sequence[R](
    *steps: Generator[Question, Answer, R]
) -> Generator[Question, Answer, list[R]]:
    results: list[R] = []
    for step in steps:
        result = yield from step
        results.append(result)
    return results

def joined(
    *steps: Generator[Question, Answer, str]
) -> Generator[Question, Answer, Result]:
    results = yield from sequence(*steps)
    return Result(", ".join(results))

answers = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("color"): Answer("blue"),
}
print(drive(
    joined(interview(), ask(Question("color"))), answers
))
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'color', answer = 'blue'
#: Alice of Wonderland, blue
