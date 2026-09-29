# forward_formats.py
from annotationlib import Format, get_annotations
from exceptions import expect

class Order:
    item: str
    buyer: Customer

expect(NameError, get_annotations, Order,
       format=Format.VALUE)
#: [NameError] name 'Customer' is not defined
fwd = get_annotations(Order, format=Format.FORWARDREF)
print(fwd["item"])
#: <class 'str'>
ref = fwd["buyer"]
print(type(ref).__name__, ref.__forward_arg__)
#: ForwardRef Customer
print(get_annotations(Order, format=Format.STRING))
#: {'item': 'str', 'buyer': 'Customer'}

class Customer:
    pass

print(get_annotations(Order)["buyer"] is Customer)
#: True
