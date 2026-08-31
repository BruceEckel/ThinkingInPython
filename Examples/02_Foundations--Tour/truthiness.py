# truthiness.py

for value in [0, 1, "", "hi", [], [1], None]:
    print(repr(value), "->", bool(value))
#: 0 -> False
#: 1 -> True
#: '' -> False
#: 'hi' -> True
#: [] -> False
#: [1] -> True
#: None -> False

if not []:
    print("empty")  # An empty list is falsy
#: empty

# 'or' returns the first truthy operand
name = "" or "default"
print(name)
#: default
count = 0
print(count or 10)  # 0 is falsy, so the fallback wins
#: 10
