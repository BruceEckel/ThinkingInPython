# greet_console.py
from ask_tell import greet

class Console:
    def ask(self, prompt: str) -> str:
        return input(prompt)

    def tell(self, message: str) -> None:
        print(message)

greet(Console(), Console())
