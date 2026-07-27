# ask_tell_effect.py
from dataclasses import dataclass
from stateless import Ability, Depend, handle, run

@dataclass(frozen=True)
class Ask(Ability[str]):
    prompt: str

@dataclass(frozen=True)
class Tell(Ability[None]):
    message: str

def greet() -> Depend[Ask | Tell, None]:
    name = yield from Ask("What is your name? ")
    yield from Tell(f"Hello, {name}!")

messages: list[str] = []

def scripted(ask: Ask) -> str:
    return "Alice"

def capture(tell: Tell) -> None:
    messages.append(tell.message)

effect = handle(scripted)(handle(capture)(greet))
run(effect())
print(messages)
#: ['Hello, Alice!']
