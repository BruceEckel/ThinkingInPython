# exercise_5.py
from heapq import heapify, heappop

heap = [10, 9, 8, 7, 6, 5, 4, 3]
heapify(heap)
print(heap)
#: [3, 6, 4, 7, 10, 5, 8, 9]

for _ in range(3):
    smallest = heappop(heap)
    print(smallest, heap, heap[0] == min(heap))
#: 3 [4, 6, 5, 7, 10, 9, 8] True
#: 4 [5, 6, 8, 7, 10, 9] True
#: 5 [6, 7, 8, 9, 10] True
