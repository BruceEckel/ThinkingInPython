# bitwise.py
# Binary literals (starting with 0b) make the bit patterns readable
print(bin(0b1100 & 0b1010))  # AND, bits set in both
#: 0b1000
print(bin(0b1100 | 0b1010))  # OR, bits set in either
#: 0b1110
print(bin(0b1100 ^ 0b1010))  # XOR, bits set in exactly one
#: 0b110
print(bin(~0b1100))          # NOT, inverts every bit
#: -0b1101
print(bin(1 << 4))           # Left shift, same as 1 * 2 ** 4
#: 0b10000
print(bin(64 >> 2))          # Right shift, same as 64 // 2 ** 2
#: 0b10000

flags = 0
flags |= 0b0010         # Set bits with the augmented form
flags |= 0b1000
print(bin(flags))
#: 0b1010
