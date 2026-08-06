# exercise_5.py
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __repr__(self):
        return f"Temperature({self.celsius})"

    def __str__(self):
        return f"{self.celsius}C"

t = Temperature(21.0)
print(t)
#: 21.0C
print([t, Temperature(0.0)])
#: [Temperature(21.0), Temperature(0.0)]
print(f"{t} is {t!r}")
#: 21.0C is Temperature(21.0)
