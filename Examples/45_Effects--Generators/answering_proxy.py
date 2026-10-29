# answering_proxy.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result
from yield_from_delegates import interview

def proxy(
    inner: Generator[Question, Answer, Result],
    known: dict[Question, Answer],
) -> Generator[Question, Answer, Result]:
    request = next(inner)
    while True:
        if request in known:
            answer = known[request]  # [1]
            print(f"  proxy answers {request}")
        else:
            answer: Answer = yield request  # [2]
        try:
            request = inner.send(answer)
        except StopIteration as stop:
            return stop.value

print(drive(interview(), ANSWERS))
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: Alice of Wonderland, friend Rabbit
print(drive(
    proxy(interview(), {Question("town"): Answer("Oz")}),
    ANSWERS,
))
#: request = 'name', answer = 'Alice'
#:   proxy answers town
#: request = 'friend', answer = 'Rabbit'
#: Alice of Oz, friend Rabbit
