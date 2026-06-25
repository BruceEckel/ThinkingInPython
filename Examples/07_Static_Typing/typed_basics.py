# typed_basics.py

def repeat(text: str, times: int) -> str:
    return text * times

print(repeat("ab", 3))
## ababab

total: int = 0
for word in ["a", "bb", "ccc"]:
    total += len(word)

print(total)
## 6
