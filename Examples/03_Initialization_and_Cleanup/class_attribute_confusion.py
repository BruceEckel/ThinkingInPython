# class_attribute_confusion.py
# A class attribute looks like a per-object default, but it is one
# shared value, and an instance variable of the same name shadows it.
class Stars:
    rating = 5  # One value, shared by the whole class.


a = Stars()
b = Stars()
print(a.rating, b.rating)  # 5 5: both read the class attribute
a.rating = 1  # Assigning makes an instance variable on a.
print(a.rating, b.rating)  # 1 5: a shadows it, b sees the class
Stars.rating = 9  # Now change the shared class attribute.
print(a.rating, b.rating)  # 1 9: a keeps its own, b follows
