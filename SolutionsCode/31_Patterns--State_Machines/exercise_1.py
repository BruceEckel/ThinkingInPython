# exercise_1.py
from typing import Protocol

class Mood(Protocol):
    def hello(self) -> str: ...

class Happy:
    def hello(self) -> str:
        return "Great to see you!"

class Grumpy:
    def hello(self) -> str:
        return "What do you want?"

class Prozac:
    def hello(self) -> str:
        return "Everything is wonderful. Just wonderful."

class UnpredictablePerson:
    def __init__(self, mood: Mood) -> None:
        self._mood = mood

    def change_to(self, mood: Mood) -> None:
        self._mood = mood

    def hello(self) -> str:
        return self._mood.hello()

person = UnpredictablePerson(Happy())
print(person.hello())
#: Great to see you!
person.change_to(Grumpy())
print(person.hello())
#: What do you want?
person.change_to(Prozac())
print(person.hello())
#: Everything is wonderful. Just wonderful.
