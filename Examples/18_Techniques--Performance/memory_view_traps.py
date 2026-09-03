# memory_view_traps.py
data = bytearray(b"\x01\x02XYZ")
view = memoryview(data)
kind, version, payload = view[0], view[1], view[2:]
print(kind, version, bytes(payload))
#: 1 2 b'XYZ'
print(payload.obj is data)  # No copy: same buffer
#: True

try:
    # An open view blocks resizing the buffer:
    data.append(1)
except BufferError as e:
    print(str(e))
#: Existing exports of data: object cannot be re-sized

readonly = memoryview(b"ABCDEF")
try:
    # bytes is immutable, so a view over it stays read-only:
    readonly[0] = ord("z")
except TypeError as e:
    print(str(e))
#: cannot modify read-only memory
