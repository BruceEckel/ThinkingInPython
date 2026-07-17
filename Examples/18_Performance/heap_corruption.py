# heap_corruption.py
from heapq import heapify, nsmallest

heap = [10, 9, 8, 7, 6, 5, 4, 3]
heapify(heap)              # In-place
print(heap)
#: [3, 6, 4, 7, 10, 5, 8, 9]
print(heap.pop(0))         # Smallest
#: 3
print(heap)                # 'heap[0]' no longer smallest
#: [6, 4, 7, 10, 5, 8, 9]
print(nsmallest(1, heap))  # The true smallest
#: [4]
print(heap)                # Not reordered by nsmallest()
#: [4, 7, 10, 5, 8, 9]
