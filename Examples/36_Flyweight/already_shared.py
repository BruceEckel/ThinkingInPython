# already_shared.py
from sys import intern

low, low2 = int("256"), int("256")
high, high2 = int("257"), int("257")
print(low is low2, high is high2)
#: True True
joined = "".join(["fly", "weight"])
joined2 = "".join(["fly", "weight"])
print(joined == joined2, joined is joined2)
#: True False
print(intern(joined) is intern(joined2))
#: True
