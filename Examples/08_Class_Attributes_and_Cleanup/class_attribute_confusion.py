# class_attribute_confusion.py
class Stars:
    rating = 5  # One value, shared by the whole class

a = Stars()
b = Stars()
print(a.rating, b.rating)  # Both read the class attr
## 5 5
a.rating = 1  # Assigning makes an instance variable on a
print(a.rating, b.rating)  # 'a' shadows it, 'b' sees the class
## 1 5
Stars.rating = 9  # Change the shared class attr
print(a.rating, b.rating)  # 'a' instance variable, 'b' class attr
## 1 9
