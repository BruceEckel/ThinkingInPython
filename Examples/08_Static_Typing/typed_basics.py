# typed_basics.py

def repeat(text: str, times: int) -> str:
    return text * times

total: int = 0
for word in ["a", "bb", "ccc"]:
    total += len(word)

print(repeat("ab", 3))
print(total)
