# exercise_4.py
totalSum = 0  # noqa: N816 (deliberately non-idiomatic; see below)
totalSum += 5  # noqa: N816
flagBits = 0b0010  # noqa: N816
flagBits |= 0b1000  # noqa: N816
print(totalSum, bin(flagBits))
#: 5 0b1010
