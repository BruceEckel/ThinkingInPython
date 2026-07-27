# yield_from_delegates.py
from collections.abc import Generator

def ask(question: str) -> Generator[str, str, str]:
    answer = yield question
    print(f"ask({question = }) -> {answer = }")
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
        print(f"{stop.value = }")
        break
#: ask(question = 'name') -> answer = 'Alice'
#: ask(question = 'town') -> answer = 'Portland'
#: stop.value = 'Alice of Portland'
