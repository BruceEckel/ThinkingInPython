# yield_from_delegates.py
from collections.abc import Generator

def ask(question: str) -> Generator[str, str, str]:
    answer = yield question
    return answer

def interview() -> Generator[str, str, str]:
    name = yield from ask("name")
    town = yield from ask("town")
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
