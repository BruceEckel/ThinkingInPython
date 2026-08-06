# a_package/b_package/module4.py
from a_package.b_package.module3 import function3

print("importing module4 in b_package")

def function4():
    return f"function4 calls {function3()}"
