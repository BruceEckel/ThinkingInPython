# arena.py
# Helpers shared by both versions: generate random pairs of Items, and
# play one pair off against the other.
import random


def item_pair_gen(base, n):
    items = base.__subclasses__()
    for _ in range(n):
        yield random.choice(items)(), random.choice(items)()


def match(item1, item2):
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
