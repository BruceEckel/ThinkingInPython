# exercise_1.py
class Stars:
    rating = 5

a = Stars()
b = Stars()
a.rating = 1       # Shadows the class attribute on 'a' only
Stars.rating = 9   # Changes the shared class attribute
c = Stars()
print(c.rating)
#: 9
