# yield_from_delegates.py
from collections.abc import Generator
from generator_interview import Answer, Question, Result
from two_way_generator import drive

def ask(question: Question) -> Generator[Question, Answer, Answer]:
    answer = yield question
    print(f"ask({question = }) -> {answer = }")
    return answer

def interview() -> Generator[Question, Answer, Result]:
    name = yield from ask(Question("name"))
    town = yield from ask(Question("town"))
    return Result(f"{name} of {town}")

drive(interview(), {Question("name"): Answer("Alice"),
                    Question("town"): Answer("Wonderland")})
#: request = 'name', answers[request] = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: stop.value = 'Alice of Wonderland'
