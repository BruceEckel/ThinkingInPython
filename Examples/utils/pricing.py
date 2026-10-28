# utils/pricing.py
type Price = int

def cpu_price(order: int) -> Price:
    total = 0
    for _ in range(1_000_000):  # Processor work
        total += 1
    return order * 10
