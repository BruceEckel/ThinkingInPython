# dense_comprehension.py
warehouses = {
    "East": [
        ("wrench", 12, 4.50),
        ("drill", 0, 9.00),
        ("hammer", 5, 2.25),
    ],
    "West": [
        ("wrench", 3, 4.75),
        ("sander", 8, 15.00),
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
#: East: hammer ($2.25)
#: East: wrench ($4.50)
#: West: wrench ($4.75)
