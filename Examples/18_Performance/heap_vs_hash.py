# heap_vs_hash.py
import heapq
import timeit

n = 10_000
data = list(range(n, 0, -1))

def heap_min_extractions() -> list[int]:
    heap = data.copy()
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(100)]

def hash_min_extractions() -> list[int]:
    remaining = set(data)
    result = []
    for _ in range(100):
        smallest = min(remaining)
        remaining.remove(smallest)
        result.append(smallest)
    return result

assert heap_min_extractions() == hash_min_extractions()
t_heap = timeit.timeit(heap_min_extractions, number=50)
t_hash = timeit.timeit(hash_min_extractions, number=50)
print(f"heap at least 10x faster than repeated min() on a set: "
      f"{t_heap * 10 < t_hash}")
#: heap at least 10x faster than repeated min() on a set: True
