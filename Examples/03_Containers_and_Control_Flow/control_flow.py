# control_flow.py

def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"

print(classify(-3), classify(0), classify(7))
## negative zero positive

x = 5
print(0 < x < 10)  # Chained comparison
## True
grade = "pass" if x >= 3 else "fail"  # Conditional expression
print(grade)
## pass
