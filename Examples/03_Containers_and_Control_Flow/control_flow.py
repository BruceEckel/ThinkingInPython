# control_flow.py

def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"

print(classify(-3), classify(0), classify(7))

x = 5
print(0 < x < 10)  # True: chained comparison
grade = "pass" if x >= 3 else "fail"  # conditional expression
print(grade)
