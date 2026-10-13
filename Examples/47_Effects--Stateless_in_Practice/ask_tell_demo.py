# ask_tell_demo.py
from ask_tell_stateless import Ask, Tell, greet
from stateless import handle, run

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
