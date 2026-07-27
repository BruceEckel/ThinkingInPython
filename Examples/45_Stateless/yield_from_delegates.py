# yield_from_delegates.py
from collections.abc import Generator
from two_way_generator import drive

def ask(question: str) -> Generator[str, str, str]:
    answer = yield question
    print(f"ask({question = }) -> {answer = }")
    return answer

def interview() -> Generator[str, str, str]:
    name = yield from ask("name")
    town = yield from ask("town")
    return f"{name} of {town}"

drive(interview(), {"name": "Alice", "town": "Portland"})
#: request = 'name', answers[request] = 'Alice'
#: ask(question = 'name') -> answer = 'Alice'
#: request = 'town', answers[request] = 'Portland'
#: ask(question = 'town') -> answer = 'Portland'
#: stop.value = 'Alice of Portland'
