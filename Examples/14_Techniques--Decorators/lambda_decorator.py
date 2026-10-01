# lambda_decorator.py
@lambda f: f()
def fib_table() -> list[int]:
    table = [0, 1]
    while len(table) < 10:
        table.append(table[-1] + table[-2])
    return table

print(fib_table)
#: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
