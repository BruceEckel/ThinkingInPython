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

class Bucket:
    def __init__(self, count: int) -> None:
        self.count = count

    def __len__(self) -> int:
        return self.count

print(bool(Bucket(0)), bool(Bucket(3)))
#: False True

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
