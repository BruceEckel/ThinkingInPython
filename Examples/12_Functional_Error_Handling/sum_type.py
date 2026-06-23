# sum_type.py

def func_a(i: int) -> int | str:
    if i == 3:
        return f"func_a({i})"  # The error, returned as a value
    return i

outputs = [func_a(i) for i in range(5)]
print(outputs)

for r in outputs:
    match r:
        case int(answer):
            print(f"answer = {answer}")
        case str(error):
            print(f"error = {error!r}")
