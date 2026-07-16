# function_is_descriptor.py
class Person:
    def __init__(self, name: str) -> None:
        self.name = name

    def greet(self) -> str:
        return f"Hello, {self.name}"

# def created a plain function in the class namespace:
plain = Person.__dict__["greet"]
print(type(plain).__name__, hasattr(plain, "__get__"))
#: function True

# Reading it through an instance triggers __get__(),
# which returns a bound method:
p = Person("Ann")
print(p.greet())
#: Hello, Ann

print(plain.__get__(p, Person)())
#: Hello, Ann
