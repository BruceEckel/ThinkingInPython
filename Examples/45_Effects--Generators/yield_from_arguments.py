# yield_from_arguments.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result
from yield_from_delegates import ask, interview

def sequence(
    *steps: Generator[Question, Answer, str]
) -> Generator[Question, Answer, Result]:
    results: list[str] = []
    for step in steps:
        result = yield from step
        results.append(result)
    return Result(", ".join(results))

print(drive(
    sequence(interview(), ask(Question("color"))),
    ANSWERS | {Question("color"): Answer("blue")},
))
#: request = 'name', answer = 'Alice'
#:   ask() received Alice
#: request = 'town', answer = 'Wonderland'
#:   ask() received Wonderland
#: request = 'friend', answer = 'Rabbit'
#:   ask() received Rabbit
#: request = 'color', answer = 'blue'
#:   ask() received blue
#: Alice of Wonderland, friend Rabbit, blue
