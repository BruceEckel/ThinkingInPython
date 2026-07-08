# string_interning.py
from sys import intern

joined = "".join(["fly", "weight"])
joined2 = "".join(["fly", "weight"])
print(joined == joined2, joined is joined2)
#: True False
print(intern(joined) is intern(joined2))
#: True
