# comprehension_steps.py
from dense_comprehension import warehouses

in_stock = [
    (wh, name, price)
    for wh, items in warehouses.items()
    for name, qty, price in items
    if qty > 0 and price < 10
]
in_stock.sort(key=lambda t: t[2])

report = [
    f"{wh}: {name} (${price:.2f})"
    for wh, name, price in in_stock
]

for line in report:
    print(line)
#: East: hammer ($2.25)
#: East: wrench ($4.50)
#: West: wrench ($4.75)
