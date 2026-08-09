# combining_two.py
from composing import func_b
from result import Ok, Result
from returning_result import func_a

def pair(i: int, j: int) -> Result[str, str]:
    return func_a(i).bind(
        lambda a: func_b(j).bind(
            lambda b: Ok(f"{a} and {b}")))

if __name__ == "__main__":
    for args in [(7, 5), (1, 5), (7, 2)]:
        print(args, pair(*args))
#: (7, 5) Ok(answer='7 and 5')
#: (1, 5) Err(error='func_a(1)')
#: (7, 2) Err(error='func_b(2)')
