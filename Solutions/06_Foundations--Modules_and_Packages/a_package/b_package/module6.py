# a_package/b_package/module6.py
from a_package.module5 import function5

print("importing module6 in b_package")

def function6():
    return f"function6 calls {function5()}"
