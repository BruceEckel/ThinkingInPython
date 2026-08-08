# method_function_form.py
from tracer import trace

class Example:
    @trace
    def method(self, x: int) -> int:
        return x

    def __repr__(self) -> str:
        return "Example()"

example = Example()
print(example.method(5))
#: -> method(Example(), 5)
#: <- method = 5
#: 5
