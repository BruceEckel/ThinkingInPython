# sum_type.py

def func_a(i: int) -> int | str:
    if i == 3:
        # The error, returned as a value
        return f"func_a({i})"
    return i

outputs = [func_a(i) for i in range(5)]
print(outputs)
#: [0, 1, 2, 'func_a(3)', 4]

for r in outputs:
    match r:
        case int(answer):
            print(f"answer = {answer}")
        case str(error):
            print(f"error = {error!r}")
#: answer = 0
#: answer = 1
#: answer = 2
#: error = 'func_a(3)'
#: answer = 4
