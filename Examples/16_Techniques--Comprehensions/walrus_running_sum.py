# walrus_running_sum.py
total = 0
running = [(total := total + n) for n in range(5)]
print(running, total)
#: [0, 1, 3, 6, 10] 10
