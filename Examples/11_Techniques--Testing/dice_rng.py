# dice_rng.py
import random

def roll(rng: random.Random) -> int:
    return rng.randint(1, 6)
