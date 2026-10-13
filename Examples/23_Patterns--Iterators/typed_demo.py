# typed_demo.py
from exceptions import expect
from typed_generator import typed
from typed_iterator import TypedIterator

checked = TypedIterator(iter([1, 2, 3]), int)
print(next(checked), next(checked))
#: 1 2
print(checked.accepted)  # Read mid-stream
#: 2
print(list(typed([1, 2, 3], int)))
#: [1, 2, 3]
expect(TypeError, list, typed([1, "two"], int))
#: [TypeError] expected <class 'int'>, got str
