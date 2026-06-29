# loop_else.py

def find_factor(n):
    for d in range(2, n):
        if n % d == 0:
            print(f"{n} = {d} * {n // d}")
            break
    else:
        print(f"{n} is prime")  # No break means no factor found

find_factor(15)
#: 15 = 3 * 5
find_factor(13)
#: 13 is prime
