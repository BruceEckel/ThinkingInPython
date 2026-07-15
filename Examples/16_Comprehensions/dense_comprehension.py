# dense_comprehension.py
warehouses = {
    "East": [
        ("widget", 12, 4.50),
        ("gadget", 0, 9.00),
        ("gizmo", 5, 2.25),
    ],
    "West": [
        ("widget", 3, 4.75),
        ("thingamajig", 8, 15.00),
    ],
}

report = [
    f"{wh}: {name} (${price:.2f})"
    for wh, name, price in sorted(
        [(wh, name, price)
         for wh, items in warehouses.items()
         for name, qty, price in items
         if qty > 0 and price < 10],
        key=lambda t: t[2])
]

if __name__ == "__main__":
    for line in report:
        print(line)
#: East: gizmo ($2.25)
#: East: widget ($4.50)
#: West: widget ($4.75)
