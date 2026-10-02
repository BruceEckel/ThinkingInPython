# exercise_4.py
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable

def grouped[V, K: Hashable](
    data: Iterable[V], key: Callable[[V], K]
) -> dict[K, list[V]]:
    out: defaultdict[K, list[V]] = defaultdict(list)
    for item in data:
        out[key(item)].append(item)
    return dict(out)

print(grouped(["b", "a", "b"], str.upper))
#: {'B': ['b', 'b'], 'A': ['a']}
