# dense_comprehension.py
from warehouses import warehouses

report = [
    f"{wh}: {name} (${price:.2f})"
    for wh, name, price in sorted(
        [(wh, name, price)
         for wh, items in warehouses.items()
         for name, qty, price in items
         if qty > 0 and price < 10],
        key=lambda t: t[2])
]
for line in report:
    print(line)
#: East: hammer ($2.25)
#: East: wrench ($4.50)
#: West: wrench ($4.75)
