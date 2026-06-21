# class_attribute_confusion.py
class Stars:
    rating = 5  # One value, shared by the whole class.


a = Stars()
b = Stars()
print(a.rating, b.rating)  # 5 5: Both read the class attr
a.rating = 1  # Assigning makes an instance variable on a
print(a.rating, b.rating)  # 1 5: a shadows it, b sees the class
Stars.rating = 9  # Change the shared class attr
print(a.rating, b.rating)  # 1 9: a instance variable , b class attr
