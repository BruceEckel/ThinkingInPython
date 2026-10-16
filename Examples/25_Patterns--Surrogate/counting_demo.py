# counting_demo.py
from counting_proxy import CountingProxy

class Implementation:
    def f(self) -> None: print("f()")
    def g(self) -> None: print("g()")

p = CountingProxy(Implementation())
p.f()
#: f()
p.g()
#: g()
p.f()
#: f()
print(p.f is p.f, p.f.__name__)
#: False counted
print("calls:", p.calls)
#: calls: 3
