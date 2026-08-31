# exercise_7.py
nums = (n for n in range(10))
print(any(n == 5 for n in nums))
#: True
print(sum(n * n for n in nums))
#: 230
print(list(nums))
#: []
