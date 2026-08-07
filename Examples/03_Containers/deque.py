# deque.py
from collections import deque

dq = deque([1, 2, 3])
dq.append(4)  # Add on the right
dq.appendleft(0)  # Add on the left
print(dq)
#: deque([0, 1, 2, 3, 4])
print(dq.popleft())  # Remove from the left
#: 0
print(dq.pop())  # Remove from the right
#: 4
print(dq)
#: deque([1, 2, 3])
window = deque(maxlen=3)  # A bounded sliding window
for i in range(5):
    window.append(i)
print(window)
#: deque([2, 3, 4], maxlen=3)
