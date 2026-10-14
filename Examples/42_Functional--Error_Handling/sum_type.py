# sum_type.py

def func_a(i: int) -> int | str:
    if i == 3:
        # The error, returned as a value
        return f"func_a({i})"
    return i

results = [func_a(i) for i in range(5)]
for result in results:
    match result:
        case int(answer):
            print(f"answer = {answer}")
        case str(error):
            print(f"error = {error!r}")
#: answer = 0
#: answer = 1
#: answer = 2
#: error = 'func_a(3)'
#: answer = 4
