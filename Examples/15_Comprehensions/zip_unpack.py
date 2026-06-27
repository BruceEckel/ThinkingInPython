# zip_unpack.py
all_slots = [
    ("doubled", lambda v: v * 2),
    ("squared", lambda v: v ** 2),
]
values = [10, 3]
print([
    f"{name}({v}) = {f(v)}"
    for (name, f), v in zip(all_slots, values)
])
#: ['doubled(10) = 20', 'squared(3) = 9']
