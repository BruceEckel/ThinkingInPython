# two_way_generator.py
from collections.abc import Generator

def interview() -> Generator[str, str, str]:
    name = yield "name"
    town = yield "town"
    return f"{name} of {town}"

def drive(conversation: Generator[str, str, str],
          answers: dict[str, str]) -> None:
    request = next(conversation)
    while True:
        try:
            print(f"{request = }, {answers[request] = }")
            request = conversation.send(answers[request])
        except StopIteration as stop:
            print(f"{stop.value = }")
            return

if __name__ == "__main__":
    conversation = interview()
    print(f"{type(c := conversation)}: {c.__name__}")  # type: ignore
    drive(conversation, {"name": "Alice", "town": "Portland"})
#: <class 'generator'>: interview
#: request = 'name', answers[request] = 'Alice'
#: request = 'town', answers[request] = 'Portland'
#: stop.value = 'Alice of Portland'
