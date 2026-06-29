# if_elif.py

def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"

print(classify(-3), classify(0), classify(7))
#: negative zero positive
