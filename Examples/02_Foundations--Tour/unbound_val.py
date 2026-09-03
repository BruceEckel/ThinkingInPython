# unbound_val.py

response = "no"
if response == "yes":
    val = 1
try:
    print(val)  # type: ignore
except NameError as e:
    print(e)
#: name 'val' is not defined
