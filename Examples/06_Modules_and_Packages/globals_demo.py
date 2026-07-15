# globals_demo.py
x = 10
print(globals()["x"])
#: 10

globals()["y"] = 42
print(y)  # type: ignore  # noqa: F821
#: 42
