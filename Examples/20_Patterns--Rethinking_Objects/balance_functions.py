# balance_functions.py
def deposit(balance: float, amount: float) -> float:
    return balance + amount

def withdraw(balance: float, amount: float) -> float:
    if amount > balance:
        raise ValueError("Insufficient funds")
    return balance - amount

balance = 100.0
balance = deposit(balance, 50.0)
balance = withdraw(balance, 30.0)
print(balance)
#: 120.0
withdraw(balance, 30.0)  # [1]
print(balance)
#: 120.0
