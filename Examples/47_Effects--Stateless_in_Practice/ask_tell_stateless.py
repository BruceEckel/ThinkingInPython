# ask_tell_stateless.py
from record import record
from stateless import Ability, Depend

@record(slots=False)
class Ask(Ability[str]):
    prompt: str

@record(slots=False)
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
