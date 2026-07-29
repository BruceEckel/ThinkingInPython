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
#: request = 'name', answers[request] = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: request = 'color', answers[request] = 'blue'
#: ask(question = 'color') -> answer = 'blue'
#: Alice of Wonderland, friend Rabbit, color blue
