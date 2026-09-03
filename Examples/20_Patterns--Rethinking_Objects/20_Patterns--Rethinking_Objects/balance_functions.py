# 20_Patterns--Rethinking_Objects/balance_functions.py
def deposit(balance: float, amount: float) -> float:
    return balance + amount

def withdraw(balance: float, amount: float) -> float:
    if amount > balance:
        raise ValueError("Insufficient funds")
    return balance - amount

if __name__ == "__main__":
    balance = 100.0
    balance = deposit(balance, 50.0)
    balance = withdraw(balance, 30.0)
    print(balance)
#: 120.0
