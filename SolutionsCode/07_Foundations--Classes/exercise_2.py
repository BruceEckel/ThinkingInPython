# exercise_2.py
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, k):
        return cls(k - 273.15)

    @staticmethod
    def is_freezing(celsius):
        return celsius <= 0

t1 = Temperature.from_fahrenheit(212)
t2 = Temperature.from_kelvin(373.15)
print(round(t1.celsius, 2), round(t2.celsius, 2))
#: 100.0 100.0
