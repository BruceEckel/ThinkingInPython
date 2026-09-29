# concatenate.py

total = 7
try:
    print("total: " + total)  # type: ignore
except TypeError as e:
    print(e)
#: can only concatenate str (not "int") to str
print("total: " + str(total))
#: total: 7
