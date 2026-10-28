# drive.py
import inspect
from collections.abc import Generator
from typing import Final
from interview_generator import Answer, Question, Result

ANSWERS: Final[dict[Question, Answer]] = {
    Question("name"): Answer("Alice"),
    Question("town"): Answer("Wonderland"),
    Question("friend"): Answer("Rabbit"),
}

def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer],
          *, show_state: bool = False) -> Result:
    try:
        request: Question = next(conversation)
    except StopIteration as stop:
        return stop.value
    while True:
        answer = answers[request]
        line = f"{request = }, {answer = }"
        if show_state:
            state = inspect.getgeneratorstate(conversation)
            line += f", {state}"
        print(line)
        try:
            request = conversation.send(answer)
        except StopIteration as stop:
            return stop.value
