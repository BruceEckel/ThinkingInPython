# composing_with_bind.py
from composing import func_b, func_c
from result import Result
from returning_result import func_a

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_c)

if __name__ == "__main__":
    for i in range(5):
        print(i, composed(i))
#: 0 Success(answer=0)
#: 1 Failure(error='func_a(1)')
#: 2 Failure(error='func_b(2)')
#: 3 Failure(error='func_c(3): division by zero')
#: 4 Success(answer=4)
