# two_way_generator.py
import inspect
from drive import ANSWERS, drive
from interview_generator import interview

conversation = interview()
print(inspect.getgeneratorstate(conversation))
#: GEN_CREATED
result = drive(conversation, ANSWERS)
#: request = 'name', answer = 'Alice', GEN_SUSPENDED
#: request = 'town', answer = 'Wonderland', GEN_SUSPENDED
#: request = 'friend', answer = 'Rabbit', GEN_SUSPENDED
print(f"{result = }")
#: result = 'Alice of Wonderland, friend Rabbit'
print(inspect.getgeneratorstate(conversation))
#: GEN_CLOSED
