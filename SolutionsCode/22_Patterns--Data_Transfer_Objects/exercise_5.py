# exercise_5.py
def summarize(data: list[float]) -> tuple[float, int]:
    return (sum(data) / len(data), len(data))

result = summarize([2.0, 4.0, 6.0])
print(result)
#: (4.0, 3)
print(result[0], result[1])
#: 4.0 3
mean, count = summarize([1.0, 3.0])
print(mean, count)
#: 2.0 2
