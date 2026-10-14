# bookkeeping_scales.py
from ask_tell import Ask, Capture, Scripted, Tell, greet

def session(ask: Ask, tell: Tell) -> None:
    greet(ask, tell)

def menu(ask: Ask, tell: Tell) -> None:
    session(ask, tell)

def main(ask: Ask, tell: Tell) -> None:
    menu(ask, tell)

captured = Capture()
main(Scripted(), captured)
print(captured.messages)
#: ['Hello, Alice!']
