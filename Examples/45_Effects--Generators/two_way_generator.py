# two_way_generator.py
from collections.abc import Generator
from typing import Final
from interview_generator import (Answer, Question,
                                 Result, interview)

ANSWERS: Final[dict[Question, Answer]] = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}

def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer]) -> Result:
    request = next(conversation)
    while True:
        answer = answers[request]
        print(f"{request = }, {answer = }")
        try:
            request = conversation.send(answer)
        except StopIteration as stop:
            return stop.value

if __name__ == "__main__":
    conversation = interview()
    print(f"{type(conversation)}: {conversation.__name__}")  # type: ignore
    result = drive(conversation, ANSWERS)
    print(f"{result = }")
#: <class 'generator'>: interview
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
#: result = 'Alice of Wonderland, friend Rabbit'
