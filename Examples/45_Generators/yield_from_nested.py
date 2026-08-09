# yield_from_nested.py
from collections.abc import Generator
from interview_generator import Answer, Question, Result
from two_way_generator import ANSWERS, drive
from yield_from_delegates import ask, interview

def survey() -> Generator[Question, Answer, Result]:
    profile: Result = yield from interview()
    color: Answer = yield from ask(Question("color"))
    return Result(f"{profile}, color {color}")

print(drive(survey(),
            ANSWERS | {Question("color"): Answer("blue")}))
#: request = 'name', answer = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: request = 'color', answer = 'blue'
#: ask(question = 'color') -> answer = 'blue'
#: Alice of Wonderland, friend Rabbit, color blue
