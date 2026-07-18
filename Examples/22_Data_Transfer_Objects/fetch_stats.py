# fetch_stats.py
from typing import NamedTuple

class Stats(NamedTuple):
    mean: float
    count: int

def summarize(data: list[float]) -> Stats:
    return Stats(sum(data) / len(data), len(data))

stats = summarize([2.0, 4.0, 6.0])
print(stats.mean, stats.count)
#: 4.0 3
mean, count = summarize([1.0, 3.0])  # Unpacks like a tuple
print(mean, count)
#: 2.0 2
