# memory_view.py
data = bytearray(b"ABCDEF")
view = memoryview(data)  # No copy of the underlying bytes
chunk = view[1:4]
print(bytes(chunk))
#: b'BCD'
view[0] = ord("z")  # Writes through to the original
print(data)
#: bytearray(b'zBCDEF')
print(view.nbytes)
#: 6
