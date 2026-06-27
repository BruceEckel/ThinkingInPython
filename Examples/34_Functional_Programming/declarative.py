# declarative.py
numbers = [1, 2, 3, 4, 5, 6]
# Imperative: spell out every step of the how:
result = []
for n in numbers:
    if n % 2 == 0:
        result.append(n * n)
print(result)
## [4, 16, 36]
# Declarative: state the what, as a comprehension:
print([n * n for n in numbers if n % 2 == 0])
## [4, 16, 36]
