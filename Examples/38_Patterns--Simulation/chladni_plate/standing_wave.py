# chladni_plate/standing_wave.py
import math

type Mode = tuple[int, int]  # Vibration pattern (m, n)

def amplitude(x: float, y: float, mode: Mode) -> float:
    m, n = mode
    return abs(
        math.cos(m * math.pi * x)
        * math.cos(n * math.pi * y)
        - math.cos(n * math.pi * x)
        * math.cos(m * math.pi * y))
