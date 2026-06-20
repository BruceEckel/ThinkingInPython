# bitwise.py
# Bitwise and shift operators on integers. Binary literals (0b...)
# make the bit patterns easy to see.
print(0b1100 & 0b1010)  # 8: AND, bits set in both
print(0b1100 | 0b1010)  # 14: OR, bits set in either
print(0b1100 ^ 0b1010)  # 6: XOR, bits set in exactly one
print(~0b1100)          # -13: NOT, inverts every bit
print(1 << 4)           # 16: left shift, same as 1 * 2 ** 4
print(64 >> 2)          # 16: right shift, same as 64 // 2 ** 2

flags = 0
flags |= 0b0010         # set bits with the augmented form
flags |= 0b1000
print(flags)            # 10
