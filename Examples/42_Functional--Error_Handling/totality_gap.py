# totality_gap.py
from result import Result
from returning_result import func_a

func_a(1)  # Result discarded; nothing complains

def lies(i: int) -> Result[int, str]:
    raise RuntimeError("not total after all")
    # ty accepts this: a function that always
    # raises satisfies any declared return type.
