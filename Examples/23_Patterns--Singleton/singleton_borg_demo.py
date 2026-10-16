# singleton_borg_demo.py
from singleton_borg import Singleton

x = Singleton("sausage")
y = Singleton("eggs")
z = Singleton("spam")
# Last write wins: distinct objects, one shared __dict__:
print(x.val, x is y, x.__dict__ is y.__dict__ is z.__dict__)
#: spam False True
