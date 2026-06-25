# truthiness.py

for value in [0, 1, "", "hi", [], [1], None]:
    print(repr(value), "->", bool(value))
## 0 -> False
## 1 -> True
## '' -> False
## 'hi' -> True
## [] -> False
## [1] -> True
## None -> False

if not []:
    print("empty")        # An empty list is falsy
## empty

name = "" or "default"    # 'or' returns the first truthy operand
print(name)               # default
## default
