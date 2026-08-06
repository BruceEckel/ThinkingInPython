# spent_generator.py
nums = (n for n in range(10))
print(sum(n * n for n in nums))
#: 285
print(any(n == 5 for n in nums))
#: False
print(list(nums))
#: []
