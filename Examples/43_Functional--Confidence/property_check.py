# property_check.py
import random
from codec import decode, encode

random.seed(42)  # A failing search must be reproducible
alphabet = "abcde"
for _ in range(1000):
    sample = "".join(
        random.choices(alphabet, k=random.randint(0, 8)))
    assert decode(encode(sample)) == sample
print("1000 random cases passed")
#: 1000 random cases passed
