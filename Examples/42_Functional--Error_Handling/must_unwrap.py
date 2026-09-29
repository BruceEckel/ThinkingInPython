# must_unwrap.py
from exceptions import expected
from result import Err, Ok
from returning_result import func_a

print(hasattr(Ok(1), "unwrap"), hasattr(Err("x"), "unwrap"))
#: True False
with expected(AttributeError):
    func_a(1).unwrap()  # type: ignore
#: [AttributeError] 'Err' object has no attribute 'unwrap'
