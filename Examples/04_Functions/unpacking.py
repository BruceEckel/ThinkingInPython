# unpacking.py
# Turn a sequence into positional arguments with *.
def f(a: int, b: int, c: int) -> None:
    print(a, b, c)


x = [1, 2, 3]
f(*x)
f(*(1, 2, 3))
