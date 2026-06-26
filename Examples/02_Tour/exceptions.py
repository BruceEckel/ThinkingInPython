# exceptions.py
def divide(a, b):
    return a / b

print(divide(10, 2))
## 5.0
try:
    print(divide(10, 0))
except ZeroDivisionError as error:
    print("Cannot divide by zero:", error)
print("The program keeps running")
## Cannot divide by zero: division by zero
## The program keeps running
