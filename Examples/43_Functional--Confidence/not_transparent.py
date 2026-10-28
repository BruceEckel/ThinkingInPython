# not_transparent.py
type Balance = int

balance: Balance = 100

def withdraw(amount: int) -> Balance:
    global balance
    balance -= amount
    return balance

print(withdraw(30) + withdraw(30))
#: 110
balance = 100
print(70 + withdraw(30))
#: 140
