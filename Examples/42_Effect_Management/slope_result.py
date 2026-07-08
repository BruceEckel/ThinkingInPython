# slope_result.py
from result import Failure, Success
from safe import safe

@safe
def slope(rise: int, run: int) -> float:
    return rise / run

for args in [(10, 2), (10, 0)]:
    match slope(*args):
        case Success(answer):
            print(f"slope{args} = {answer}")
        case Failure(error):
            print(f"slope{args}: {type(error).__name__}")
#: slope(10, 2) = 5.0
#: slope(10, 0): ZeroDivisionError
