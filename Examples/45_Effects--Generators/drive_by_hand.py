# drive_by_hand.py
import inspect
from interview_generator import (Answer, Question,
                                 Result, interview)

conversation = interview()
query1: Question = next(conversation)
print(f"{query1 = }")
#: query1 = 'name'
query2: Question = conversation.send(Answer("Alice"))
print(f"{query2 = }")
#: query2 = 'town'
query3: Question = conversation.send(Answer("Wonderland"))
print(f"{query3 = }")
#: query3 = 'friend'
print(inspect.getgeneratorlocals(conversation))
#: {'name': 'Alice', 'town': 'Wonderland'}
try:
    conversation.send(Answer("Rabbit"))
except StopIteration as stop:
    result: Result = stop.value
print(f"{result = }")
#: result = 'Alice of Wonderland, friend Rabbit'
