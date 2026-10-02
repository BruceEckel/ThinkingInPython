# exercise_1.py
from collections import deque
from timeit import timeit
from benchmark import report

n = 2_000  # then 200_000

def list_left_ops():
    items = []
    for i in range(n):
        items.insert(0, i)
    while items:
        items.pop(0)

def deque_left_ops():
    items = deque()
    for i in range(n):
        items.appendleft(i)
    while items:
        items.popleft()

list_time = timeit(list_left_ops, number=1)
deque_time = timeit(deque_left_ops, number=1)
report(list=list_time, deque=deque_time)
print(deque_time < list_time)
#: True
