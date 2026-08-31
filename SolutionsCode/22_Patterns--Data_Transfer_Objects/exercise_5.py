# exercise_5.py
def summarize(data: list[float]) -> tuple[float, int]:
    return (sum(data) / len(data), len(data))

print(summarize([2.0, 4.0, 6.0]))
#: (4.0, 3)
mean, count = summarize([1.0, 3.0])
print(mean, count)
#: 2.0 2
