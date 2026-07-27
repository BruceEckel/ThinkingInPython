# two_way_generator.py
from collections.abc import Generator

def interview() -> Generator[str, str, str]:
    name = yield "name"
    town = yield "town"
    return f"{name} of {town}"

answers = {"name": "Alice", "town": "Portland"}
conversation = interview()
print(f"{type(c := conversation)}: {c.__name__}")  # type: ignore
#: <class 'generator'>: interview
request = next(conversation)
while True:
    try:
        print(f"{request = }, {answers[request] = }")
        request = conversation.send(answers[request])
    except StopIteration as stop:
        print(f"{stop.value = }")
        break
#: request = 'name', answers[request] = 'Alice'
#: request = 'town', answers[request] = 'Portland'
#: stop.value = 'Alice of Portland'
