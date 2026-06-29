# modify_class.py
class Foo:
    pass

Foo.field = 42  # type: ignore
x = Foo()
print(x.field)  # type: ignore
#: 42

Foo.method = lambda self: "Hi!"  # type: ignore
print(x.method())  # type: ignore
#: Hi!
