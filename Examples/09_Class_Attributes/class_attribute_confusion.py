# class_attribute_confusion.py

class Stars:
    rating = 5  # Shared across all instances

a, b = Stars(), Stars()
print(a.rating, b.rating)  # Both read the same storage
#: 5 5
a.rating = 1  # Assigning makes an instance variable on 'a'
print(a.rating, b.rating)  # 'a' shadows it, 'b' sees the class
#: 1 5
Stars.rating = 9  # Change the shared storage
print(a.rating, b.rating)  # 'b' reads the class attribute
#: 1 9
