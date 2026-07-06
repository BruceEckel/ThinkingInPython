# small_integer_flyweights.py
low, low2 = int("256"), int("256")
high, high2 = int("100000"), int("100000")
print(low is low2, high is high2)
#: True False
