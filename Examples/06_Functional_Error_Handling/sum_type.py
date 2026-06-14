# sum_type.py
# Return the error as a value instead of raising. The return type becomes a
# union, a "sum type". Nothing is lost, but success and failure are not
# clearly distinguished: both are just values you have to tell apart by type.


def func_a(i: int) -> int | str:
    if i == 1:
        return f"func_a({i})"  # The error, returned as a value.
    return i


outputs = [func_a(i) for i in range(3)]
print(outputs)

for r in outputs:
    match r:
        case int(answer):
            print(f"answer = {answer}")
        case str(error):
            print(f"error = {error!r}")
