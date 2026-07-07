# chladni_plate/chladni.py
import math
import random
from dataclasses import dataclass

type Mode = tuple[int, int]   # Vibration pattern (m, n)

def amplitude(x: float, y: float, mode: Mode) -> float:
    "Vibration strength at (x, y), zero on the nodal lines."
    m, n = mode
    return abs(
        math.cos(m * math.pi * x) * math.cos(n * math.pi * y)
        - math.cos(n * math.pi * x) * math.cos(m * math.pi * y))

def bounce(v: float) -> float:
    "Reflect v back off the edges of the unit interval."
    if v < 0.0:
        return -v
    if v > 1.0:
        return 2.0 - v
    return v

@dataclass
class Grain:
    x: float
    y: float

class Plate:
    def __init__(self, grains: int, mode: Mode,
                 seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.mode = mode
        self.grains = [
            Grain(self.rng.random(), self.rng.random())
            for _ in range(grains)]

    def step(self, kick: float = 0.05) -> None:
        "Kick every grain, harder where the plate moves more."
        for g in self.grains:
            a = amplitude(g.x, g.y, self.mode)
            g.x = bounce(
                g.x + self.rng.uniform(-kick, kick) * a)
            g.y = bounce(
                g.y + self.rng.uniform(-kick, kick) * a)

    def agitation(self) -> float:
        "Mean vibration strength underneath the grains."
        return sum(
            amplitude(g.x, g.y, self.mode)
            for g in self.grains) / len(self.grains)

    def render(self, width: int = 60, height: int = 30) -> str:
        "Character picture of grain density."
        counts: list[list[int]] = [
            [0] * width for _ in range(height)]
        for g in self.grains:
            col = min(int(g.x * width), width - 1)
            row = min(int(g.y * height), height - 1)
            counts[row][col] += 1
        shades = " .:*#"
        return "\n".join(
            "".join(shades[min(c, len(shades) - 1)]
                    for c in row).rstrip()
            for row in counts)
