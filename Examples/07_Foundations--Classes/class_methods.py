# class_methods.py

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    # An alternative constructor
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def is_freezing(celsius):  # Needs no self or cls
        return celsius <= 0

class Reading(Temperature):
    pass  # Adds nothing; inherits from_fahrenheit()

t = Temperature.from_fahrenheit(212)
print(round(t.celsius))
#: 100
print(Temperature.is_freezing(-4))
#: True
r = Reading.from_fahrenheit(212)
print(type(r).__name__)
#: Reading
