# heap_vs_hash.py
import heapq
import random
import timeit
from benchmark import report

n = 10_000
data = list(range(n))
random.seed(0)
random.shuffle(data)  # Neither side gets a free ride

def heap_min_extractions() -> list[int]:
    heap = data.copy()
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(100)]

def sorted_min_extractions() -> list[int]:
    return sorted(data)[:100]

assert (heap_min_extractions()
        == sorted_min_extractions())
t_heap = min(timeit.repeat(
    heap_min_extractions, number=50, repeat=5
))
t_sorted = min(timeit.repeat(
    sorted_min_extractions, number=50, repeat=5
))
report(heap=t_heap, sorted_slice=t_sorted)
print(f"heap beats sorted() by 1.5x+ on shuffled "
      f"data: {t_heap * 1.5 < t_sorted}")
#: heap beats sorted() by 1.5x+ on shuffled data: True
