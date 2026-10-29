# follow_up.py
from collections.abc import Generator
from drive import ANSWERS, drive
from interview_generator import Answer, Question, Result

def follow_up() -> Generator[Question, Answer, Result]:
    name: Answer = yield Question("name")
    pet: Answer = yield Question(f"pet of {name}")
    return Result(f"{name} keeps a {pet}")

print(drive(follow_up(), ANSWERS | {
    Question("pet of Alice"): Answer("cat"),
}))
#: request = 'name', answer = 'Alice'
#: request = 'pet of Alice', answer = 'cat'
#: Alice keeps a cat
print(drive(follow_up(), {
    Question("name"): Answer("Bob"),
    Question("pet of Bob"): Answer("dog"),
}))
#: request = 'name', answer = 'Bob'
#: request = 'pet of Bob', answer = 'dog'
#: Bob keeps a dog
