# mixed_types.py

mixed = [1, "two", 3.0, True, None, [5, 6]]
for item in mixed:
    print(item, type(item).__name__)
#: 1 int
#: two str
#: 3.0 float
#: True bool
#: None NoneType
#: [5, 6] list
