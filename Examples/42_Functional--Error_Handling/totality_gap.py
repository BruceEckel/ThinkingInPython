# totality_gap.py
from exceptions import expected
from result import Result
from returning_result import func_a

func_a(1)  # Result discarded; nothing complains

def lies(i: int) -> Result[int, str]:
    raise RuntimeError("not total after all")

with expected(RuntimeError):
    lies(1)
#: [RuntimeError] not total after all
