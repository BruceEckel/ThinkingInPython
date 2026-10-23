# yield_from_nested.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result
from yield_from_delegates import ask, interview

def survey() -> Generator[Question, Answer, Result]:
    profile: Result = yield from interview()
    color: Answer = yield from ask(Question("color"))
    return Result(f"{profile}, color {color}")

print(drive(survey(),
            ANSWERS | {Question("color"): Answer("blue")}))
#: request = 'name', answer = 'Alice', GEN_SUSPENDED
#:   ask() received Alice
#: request = 'town', answer = 'Wonderland', GEN_SUSPENDED
#:   ask() received Wonderland
#: request = 'friend', answer = 'Rabbit', GEN_SUSPENDED
#:   ask() received Rabbit
#: request = 'color', answer = 'blue', GEN_SUSPENDED
#:   ask() received blue
#: Alice of Wonderland, friend Rabbit, color blue
