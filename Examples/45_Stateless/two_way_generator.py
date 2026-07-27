# two_way_generator.py
from collections.abc import Generator

def interview() -> Generator[str, str, str]:
    name = yield "name"
    town = yield "town"
    return f"{name} of {town}"

answers = {"name": "Alice", "town": "Portland"}
conversation = interview()
request = next(conversation)
while True:
    try:
        request = conversation.send(answers[request])
    except StopIteration as stop:
        print(stop.value)
        break
#: Alice of Portland
