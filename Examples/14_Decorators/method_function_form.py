# method_function_form.py
from tracer import trace

class Ex:
    @trace
    def method(self, x: int) -> int:
        return x

    def __repr__(self) -> str:
        return "Ex()"

ex = Ex()
print(ex.method(5))
#: -> method(Ex(), 5)
#: <- method = 5
#: 5
