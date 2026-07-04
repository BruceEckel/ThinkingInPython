# deque.py
from collections import deque
from timeit import timeit

dq = deque([1, 2, 3])
dq.append(4)         # Add on the right
dq.appendleft(0)     # Add on the left
print(dq)
#: deque([0, 1, 2, 3, 4])
print(dq.popleft())  # Remove from the left
#: 0
print(dq.pop())      # Remove from the right
#: 4
print(dq)
#: deque([1, 2, 3])

# A plain list can act as a double-ended queue too:
lst = [1, 2, 3]
lst.append(4)        # Add on the right
lst.insert(0, 0)     # Add on the left
print(lst)
#: [0, 1, 2, 3, 4]
print(lst.pop(0))    # Remove from the left
#: 0
print(lst.pop())     # Remove from the right
#: 4
print(lst)
#: [1, 2, 3]

# Time it to see the difference:
n = 20_000

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
print(deque_time < list_time)
#: True
