# demo_stars.py
from stars import Stars, f1, f2

rating = Stars(4)
print(rating)
#: Stars(number=4)
print(f1(Stars(2)))
#: Stars(number=7)
print(f2(Stars(2)))
#: Stars(number=10)
