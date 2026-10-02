# exercise_2.py
import timeit

for size in (1, 2, 5, 10, 20, 50, 100, 200, 500):
    small_list = list(range(size))
    small_set = set(small_list)
    target = size - 1
    t_list = timeit.timeit(
        lambda: target in small_list, number=20_000)
    t_set = timeit.timeit(
        lambda: target in small_set, number=20_000)
    winner = "list" if t_list < t_set else "set"
    print(size, winner)
