# exercise_4.py
def checked_divide(a, b):
    if b == 0:
        raise ValueError("Divide by zero")
    return a / b

def demo_exceptions(a, b):
    try:
        checked_divide(a, b)
    except ValueError as e:
        print("caught:", e)
    else:
        print("no exception")
    finally:
        print("finally always runs")

demo_exceptions(1, 2)
#: no exception
#: finally always runs
try:
    demo_exceptions(1, "x")
except TypeError as e:
    print("escaped:", type(e).__name__)
#: finally always runs
#: escaped: TypeError
