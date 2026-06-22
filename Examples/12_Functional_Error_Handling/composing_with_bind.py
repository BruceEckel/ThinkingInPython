# composing_with_bind.py
# Bind removes the boilerplate. Chain the steps; a Failure anywhere
# in the chain short-circuits the rest and is passed through to the
# end.
from composing import func_b, func_c
from result import Result
from returning_result import func_a

def composed(i: int) -> Result[int, str]:
    return func_a(i).bind(func_b).bind(func_c)

if __name__ == "__main__":
    for i in range(5):
        print(i, composed(i))
