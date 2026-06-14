# typed_basics.py
# Hints annotate parameters, returns, and variables. They do not change how the
# code runs; they let a checker and an editor reason about it.


def repeat(text: str, times: int) -> str:
    return text * times


total: int = 0
for word in ["a", "bb", "ccc"]:
    total += len(word)

print(repeat("ab", 3))
print(total)
