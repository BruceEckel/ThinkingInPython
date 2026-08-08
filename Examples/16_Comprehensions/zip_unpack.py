# zip_unpack.py
operations = [
    ("doubled", lambda v: v * 2),
    ("squared", lambda v: v ** 2),
]
values = [10, 3, 42]
print([
    f"{name}({v}) = {f(v)}"
    for (name, f), v in zip(operations, values)
])
#: ['doubled(10) = 20', 'squared(3) = 9']
