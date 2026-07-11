# exercise_1.py
class Cappuccino:
    cost = 1.75
    description = "Cappuccino"

class Extra:
    add_cost = 0.0
    name = ""

    def __init__(self, drink) -> None:
        self.drink = drink

    @property
    def cost(self) -> float:
        return self.drink.cost + self.add_cost

    @property
    def description(self) -> str:
        return f"{self.drink.description} + {self.name}"

class Decaf(Extra):
    add_cost = 0.0
    name = "Decaf"

class Syrup(Extra):
    add_cost = 0.30
    name = "Syrup"

order = Syrup(Decaf(Cappuccino()))
print(f"{order.description}: ${order.cost:.2f}")
#: Cappuccino + Decaf + Syrup: $2.05
