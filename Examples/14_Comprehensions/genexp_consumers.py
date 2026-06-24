# genexp_consumers.py
nums = range(1_000_000)

print(sum(n * n for n in nums))  # 333332833333500000
print(any(n == 12_345 for n in nums))  # True
print(max(len(str(n)) for n in nums))  # 6
