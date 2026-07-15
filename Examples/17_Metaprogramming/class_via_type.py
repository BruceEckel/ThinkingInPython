# class_via_type.py
class C:
    pass

D = type("D", (), {})  # The same construction, by hand

print(type(C), type(D))
#: <class 'type'> <class 'type'>
# Both inherit object:
print(C.__bases__, D.__bases__)
#: (<class 'object'>,) (<class 'object'>,)
# Both make ordinary instances:
print(isinstance(C(), C), isinstance(D(), D))
#: True True
