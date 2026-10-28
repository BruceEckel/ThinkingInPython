# exercise_1.py
type Balance = int

balance: Balance = 100

def deposit(amount: int) -> Balance:
    global balance
    balance += amount
    return balance

print(deposit(30), deposit(30))
#: 130 160
