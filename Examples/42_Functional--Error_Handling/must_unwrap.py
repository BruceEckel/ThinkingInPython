# must_unwrap.py
from exceptions import expected
from returning_result import func_a

with expected(AttributeError):
    func_a(1).unwrap()  # type: ignore
#: [AttributeError] 'Err' object has no attribute 'unwrap'
