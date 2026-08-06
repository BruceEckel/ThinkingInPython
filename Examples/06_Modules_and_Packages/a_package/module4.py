# a_package/module4.py
from .module1 import function1

def function4():
    return f"function4 calls {function1()}"
