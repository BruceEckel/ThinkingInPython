# sliding_window.py
from collections import deque

window = deque(maxlen=3)  # A bounded sliding window
for i in range(5):
    window.append(i)
print(window)
#: deque([2, 3, 4], maxlen=3)
