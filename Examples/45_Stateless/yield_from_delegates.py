# yield_from_delegates.py
from collections.abc import Generator
from generator_interview import Answer, Question, Result
from two_way_generator import ANSWERS, drive

def ask(question: Question) -> Generator[Question, Answer, Answer]:
    answer = yield question
    print(f"ask({question = }) -> {answer = }")
    return answer

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield from ask(Question("name"))
    town: Answer = yield from ask(Question("town"))
    friend: Answer = yield from ask(Question("friend"))
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    print(drive(interview(), ANSWERS))
#: request = 'name', answers[request] = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: ask(question = 'town') -> answer = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: ask(question = 'friend') -> answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
