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
print(round(0.5), round(1.5), round(2.5))  # Ties go to even
#: 0 2 2
print(True + True, True == 1)  # A bool is an int
#: 2 True
