# two_way_generator.py
from collections.abc import Generator
from typing import Final
from interview_generator import Answer, Question, Result, interview

ANSWERS: Final[dict[Question, Answer]] = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}

def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer]) -> Result:
    request = next(conversation)
    while True:
        print(f"{request = }, {answers[request] = }")
        try:
            request = conversation.send(answers[request])
        except StopIteration as stop:
            return stop.value

if __name__ == "__main__":
    conversation = interview()
    print(f"{type(c := conversation)}: {c.__name__}")  # type: ignore
    result = drive(conversation, ANSWERS)
    print(f"{result = }")
#: <class 'generator'>: interview
#: request = 'name', answers[request] = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: result = 'Alice of Wonderland, friend Rabbit'
