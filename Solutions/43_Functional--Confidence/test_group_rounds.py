# test_group_rounds.py
import random
from collections import Counter
from collections.abc import Iterator
from itertools import combinations, islice
from hypothesis import given, strategies

type Group = tuple[str, ...]
type Round = list[Group]

def group_rounds(
    students: list[str], size: int, seed: int = 0
) -> Iterator[Round]:
    history: Counter[frozenset[str]] = Counter()
    rng = random.Random(seed)

    def met(group: list[str], candidate: str) -> int:
        return sum(history[frozenset((m, candidate))]
                   for m in group)

    while True:
        pool = list(students)
        rng.shuffle(pool)
        groups: list[list[str]] = []
        while len(pool) >= size:
            leader = pool.pop()
            group = [leader]
            while len(group) < size:
                stranger = min(pool,
                               key=lambda c: met(group, c))
                pool.remove(stranger)
                group.append(stranger)
            groups.append(group)
        # Roster smaller than one group
        if pool and not groups:
            groups.append([])
        # Too few left for a full group of `size`
        for extra in pool:
            host = min(groups, key=lambda g: met(g, extra))
            host.append(extra)
        round_result: Round = [tuple(g) for g in groups]
        for g in round_result:
            for pair in combinations(g, 2):
                history[frozenset(pair)] += 1
        yield round_result

rosters = strategies.lists(
    strategies.text("abcdefghij", min_size=1, max_size=3),
    min_size=2, max_size=12, unique=True)

@given(rosters,
       strategies.integers(min_value=1, max_value=5))
def test_every_student_appears_once_per_round(
        names: list[str], size: int) -> None:
    for grouping in islice(group_rounds(names, size), 3):
        placed = [*group for group in grouping]
        assert sorted(placed) == sorted(names)
