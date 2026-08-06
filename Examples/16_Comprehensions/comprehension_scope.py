# comprehension_scope.py
e = "outer"
squares = [e ** 2 for e in range(4)]
print(squares, e)
#: [0, 1, 4, 9] outer
total = 0
running = [(total := total + n) for n in range(5)]
print(running, total)
#: [0, 1, 3, 6, 10] 10
