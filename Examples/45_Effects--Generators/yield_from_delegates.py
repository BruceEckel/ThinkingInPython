# yield_from_delegates.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result

def ask(
    question: Question
) -> Generator[Question, Answer, Answer]:
    answer: Answer = yield question
    print(f"  ask() received {answer}")
    return answer

def interview() -> Generator[Question, Answer, Result]:
    name: Answer = yield from ask(Question("name"))
    town: Answer = yield from ask(Question("town"))
    friend: Answer = yield from ask(Question("friend"))
    return Result(f"{name} of {town}, friend {friend}")

if __name__ == "__main__":
    print(drive(interview(), ANSWERS))
#: request = 'name', answer = 'Alice'
#:   ask() received Alice
#: request = 'town', answer = 'Wonderland'
#:   ask() received Wonderland
#: request = 'friend', answer = 'Rabbit'
#:   ask() received Rabbit
#: Alice of Wonderland, friend Rabbit
