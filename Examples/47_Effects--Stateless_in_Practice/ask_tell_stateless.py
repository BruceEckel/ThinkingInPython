# ask_tell_stateless.py
from dataclasses import dataclass
from stateless import Ability, Depend, handle, run

@dataclass(frozen=True)
class Ask(Ability[str]):
    prompt: str

@dataclass(frozen=True)
class Tell(Ability[None]):
    message: str

def ask(prompt: str) -> Depend[Ask, str]:
    answer: str = yield from Ask(prompt)
    return answer

def tell(message: str) -> Depend[Tell, None]:
    yield from Tell(message)

def greet() -> Depend[Ask | Tell, None]:
    name = yield from ask("What is your name? ")
    yield from tell(f"Hello, {name}!")

messages: list[str] = []

def capture(request: Tell) -> None:
    messages.append(request.message)

def scripted(request: Ask) -> str:
    return "Alice"

half = handle(capture)(greet)
full = handle(scripted)(half)
run(full())
print(messages)
#: ['Hello, Alice!']
