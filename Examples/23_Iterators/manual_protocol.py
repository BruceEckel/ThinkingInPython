# manual_protocol.py
nums = [1, 2]
it = iter(nums)  # What a for loop calls first
print(iter(nums) is iter(nums))  # A fresh iterator per pass
#: False
print(iter(it) is it)  # An iterator returns itself
#: True
print(next(it), next(it))  # What the loop calls per step
#: 1 2
try:
    next(it)
except StopIteration:
    print("StopIteration ends the loop")
#: StopIteration ends the loop
