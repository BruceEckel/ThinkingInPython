# deque.py
from collections import deque

queue = deque([1, 2, 3])
queue.append(4)         # Add on the right
queue.appendleft(0)     # Add on the left
print(queue)
#: deque([0, 1, 2, 3, 4])
print(queue.popleft())  # Remove from the left
#: 0
print(queue.pop())      # Remove from the right
#: 4
print(queue)
#: deque([1, 2, 3])
