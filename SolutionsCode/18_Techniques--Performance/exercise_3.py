# exercise_3.py
import tracemalloc

N = 1_000_000

def eager_first_evens():  # The original, two lists
    squares = [x * x for x in range(N)]
    evens = [s for s in squares if s % 2 == 0]
    return evens[:5]

def eager_first_evens_comprehension():
    return [x * x for x in range(N) if (x * x) % 2 == 0][:5]

def peak_of(func) -> int:
    tracemalloc.start()
    func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak

print(eager_first_evens_comprehension())
#: [0, 4, 16, 36, 64]
two, one = peak_of(eager_first_evens), peak_of(
    eager_first_evens_comprehension)
print("peak ratio, one list to two:", round(one / two, 1))
#: peak ratio, one list to two: 0.5
