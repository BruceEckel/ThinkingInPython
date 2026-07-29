# two_way_generator.py
from collections.abc import Generator
from generator_interview import Answer, Question, Result, interview

def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer]) -> Result:
    request = next(conversation)
    while True:
        try:
            print(f"{request = }, {answers[request] = }")
            request = conversation.send(answers[request])
        except StopIteration as stop:
            return stop.value

if __name__ == "__main__":
    conversation = interview()
    print(f"{type(c := conversation)}: {c.__name__}")  # type: ignore
    answers = {Question("name"): Answer("Alice"),
               Question("town"): Answer("Wonderland"),
               Question("friend"): Answer("Rabbit")}
    result = drive(conversation, answers)
    print(f"{result = }")
#: <class 'generator'>: interview
#: request = 'name', answers[request] = 'Alice'
#: request = 'town', answers[request] = 'Wonderland'
#: request = 'friend', answers[request] = 'Rabbit'
#: result = 'Alice of Wonderland, friend Rabbit'
