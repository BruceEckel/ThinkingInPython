# arithmetic.py

print(7 / 2)  # True division, always a float
#: 3.5
print(7 // 2)  # Floor division
#: 3
print(7 % 2)  # Remainder
#: 1
print(-7 // 2, -7 % 2)  # Floors, not truncates toward zero
#: -4 1
print(2 ** 10)  # Exponentiation
#: 1024
print(10 ** 30)  # A 31-digit int, no overflow
#: 1000000000000000000000000000000
print(abs(-5), round(3.14159, 2))
#: 5 3.14
total = 0
total += 5  # Augmented assignment, like other languages
print(total)
#: 5
scores = [90, 0, 71, 0, 55]
print(sum(s > 60 for s in scores))  # True counts as 1
#: 2
