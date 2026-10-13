# composing.py
from result import Err, Result
from steps import func_a, func_b, func_c

def composed(i: int) -> Result[int, str]:
    a = func_a(i)
    if isinstance(a, Err):
        return a
    b = func_b(a.unwrap())
    if isinstance(b, Err):
        return b
    return func_c(b.unwrap())

if __name__ == "__main__":
    for i in range(5):
        print(i, composed(i))
#: 0 Ok(answer=0)
#: 1 Err(error='func_a(1)')
#: 2 Err(error='func_b(2)')
#: 3 Err(error='func_c(3): division by zero')
#: 4 Ok(answer=4)
