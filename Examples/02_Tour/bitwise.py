# bitwise.py
# Bitwise and shift operators on integers. Binary literals
# (starting with 0b) make the bit patterns easy to see.
print(0b1100 & 0b1010)  # AND, bits set in both
## 8
print(0b1100 | 0b1010)  # OR, bits set in either
## 14
print(0b1100 ^ 0b1010)  # XOR, bits set in exactly one
## 6
print(~0b1100)          # NOT, inverts every bit
## -13
print(1 << 4)           # Left shift, same as 1 * 2 ** 4
## 16
print(64 >> 2)          # Right shift, same as 64 // 2 ** 2
## 16

flags = 0
flags |= 0b0010         # Set bits with the augmented form
flags |= 0b1000
print(flags)
## 10
