# two_way_generator.py
import inspect
from drive import ANSWERS, drive
from interview_generator import interview

conversation = interview()
print(inspect.getgeneratorstate(conversation))
#: GEN_CREATED
result = drive(conversation, ANSWERS)
#: request = 'name', answer = 'Alice'
#: request = 'town', answer = 'Wonderland'
#: request = 'friend', answer = 'Rabbit'
print(f"{result = }")
#: result = 'Alice of Wonderland, friend Rabbit'
