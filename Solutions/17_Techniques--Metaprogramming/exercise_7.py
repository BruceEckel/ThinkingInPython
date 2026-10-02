# exercise_7.py
from typing import Any

def describe(self: Any) -> str:
    return f"{self} degrees {self.unit}"

Celsius = type("Celsius", (float,),
               {"unit": "C", "describe": describe})

c = Celsius(21.5)
print(c.describe())
#: 21.5 degrees C
print(type(Celsius) is type)
#: True
print(c + 0.5, isinstance(c, float))
#: 22.0 True
