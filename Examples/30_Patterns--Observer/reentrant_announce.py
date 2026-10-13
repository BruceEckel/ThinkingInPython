# reentrant_announce.py
from exceptions import expected
from thermometer import Thermometer

t = Thermometer(20.0)
t.connect(lambda c: setattr(t, "celsius", c))
with expected(RecursionError):
    t.celsius = 25.0
#: [RecursionError] maximum recursion depth exceeded
