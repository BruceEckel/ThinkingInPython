# must_unwrap.py
from result import Err, Ok
from returning_result import func_a

print(hasattr(Ok(1), "unwrap"), hasattr(Err("x"), "unwrap"))
#: True False
try:
    func_a(1).unwrap()  # type: ignore
except AttributeError as e:
    print(e)
#: 'Err' object has no attribute 'unwrap'
