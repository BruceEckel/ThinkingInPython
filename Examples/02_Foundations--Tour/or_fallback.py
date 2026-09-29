# or_fallback.py

# 'or' returns the first truthy operand
name = "" or "default"
print(name)
#: default
items = []
print(items and items[0])  # Stops at the falsy operand
#: []
count = 0
print(count or 10)  # 0 is falsy, so the fallback wins
#: 10
print(10 if count is None else count)  # Keeps the 0
#: 0
