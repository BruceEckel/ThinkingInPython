# decorator/nodecorators/CoffeeShop.py
# Coffee example with no decorators

class Espresso: pass
class DoubleEspresso: pass
class EspressoConPanna: pass

class Cappuccino:
    def __init__(self):
        self.cost = 1
        self.description = "Cappucino"
    def getCost(self):
        return self.cost
    def getDescription(self):
        return self.description

class CappuccinoDecaf: pass
class CappuccinoDecafWhipped: pass
class CappuccinoDry: pass
class CappuccinoDryWhipped: pass
class CappuccinoExtraEspresso: pass
class CappuccinoExtraEspressoWhipped: pass
class CappuccinoWhipped: pass

class CafeMocha: pass
class CafeMochaDecaf: pass
class CafeMochaDecafWhipped:
    def __init__(self):
        self.cost = 1.25
        self.description = \
          "Cafe Mocha decaf whipped cream"
    def getCost(self):
        return self.cost
    def getDescription(self):
        return self.description

class CafeMochaExtraEspresso: pass
class CafeMochaExtraEspressoWhipped: pass
class CafeMochaWet: pass
class CafeMochaWetWhipped: pass
class CafeMochaWhipped: pass

class CafeLatte: pass
class CafeLatteDecaf: pass
class CafeLatteDecafWhipped: pass
class CafeLatteExtraEspresso: pass
class CafeLatteExtraEspressoWhipped: pass
class CafeLatteWet: pass
class CafeLatteWetWhipped: pass
class CafeLatteWhipped: pass

cappuccino = Cappuccino()
print((cappuccino.getDescription() + ": $" +
  `cappuccino.getCost()`))

cafeMocha = CafeMochaDecafWhipped()
print((cafeMocha.getDescription()
  + ": $" + `cafeMocha.getCost()`))