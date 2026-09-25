# exercise_1.py
balance = 100

def deposit(amount: int) -> int:
    global balance
    balance += amount
    return balance

print(deposit(30), deposit(30))
#: 130 160
