# stateMachine/vendingmachine/VendingMachine.py
# Demonstrates use of StateMachine.py
import sys
sys.path += ['../stateMachine2']
import StateMachine

class State:
    def __init__(self, name): self.name = name
    def __str__(self): return self.name

State.quiescent = State("Quiesecent")
State.collecting = State("Collecting")
State.selecting = State("Selecting")
State.unavailable = State("Unavailable")
State.wantMore = State("Want More?")
State.noChange = State("Use Exact Change Only")
State.makesChange = State("Machine makes change")

class HasChange:
    def __init__(self, name): self.name = name
    def __str__(self): return self.name

HasChange.yes = HasChange("Has change")
HasChange.no = HasChange("Cannot make change")

class ChangeAvailable(StateMachine):
    def __init__(self):
        StateMachine.__init__(State.makesChange, {
          # Current state, input
          (State.makesChange, HasChange.no) :
            # test, transition, next state:
            (null, null, State.noChange),
          (State.noChange, HasChange.yes) :
            (null, null, State.noChange)
        })

class Money:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __str__(self): return self.name
    def getValue(self): return self.value

Money.quarter = Money("Quarter", 25)
Money.dollar = Money("Dollar", 100)

class Quit:
    def __str__(self): return "Quit"

Quit.quit = Quit()

class Digit:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __str__(self): return self.name
    def getValue(self): return self.value

class FirstDigit(Digit): pass
FirstDigit.A = FirstDigit("A", 0)
FirstDigit.B = FirstDigit("B", 1)
FirstDigit.C = FirstDigit("C", 2)
FirstDigit.D = FirstDigit("D", 3)

class SecondDigit(Digit): pass
SecondDigit.one = SecondDigit("one", 0)
SecondDigit.two = SecondDigit("two", 1)
SecondDigit.three = SecondDigit("three", 2)
SecondDigit.four = SecondDigit("four", 3)

class ItemSlot:
    id = 0
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity
    def __str__(self): return `ItemSlot.id`
    def getPrice(self): return self.price
    def getQuantity(self): return self.quantity
    def decrQuantity(self): self.quantity -= 1

class VendingMachine(StateMachine):
    changeAvailable = ChangeAvailable()
    amount = 0
    FirstDigit first = null
    ItemSlot[][] items = ItemSlot[4][4]

    # Conditions:
    def notEnough(self, input):
        i1 = first.getValue()
        i2 = input.getValue()
        return items[i1][i2].getPrice() > amount

    def itemAvailable(self, input):
        i1 = first.getValue()
        i2 = input.getValue()
        return items[i1][i2].getQuantity() > 0

    def itemNotAvailable(self, input):
        return !itemAvailable.condition(input)
        #i1 = first.getValue()
        #i2 = input.getValue()
        #return items[i1][i2].getQuantity() == 0

    # Transitions:
    def clearSelection(self, input):
        i1 = first.getValue()
        i2 = input.getValue()
        ItemSlot is = items[i1][i2]
        print (
          "Clearing selection: item " + is +
          " costs " + is.getPrice() +
          " and has quantity " + is.getQuantity())
        first = null

    def dispense(self, input):
        i1 = first.getValue()
        i2 = input.getValue()
        ItemSlot is = items[i1][i2]
        print(("Dispensing item " +
          is + " costs " + is.getPrice() +
          " and has quantity " + is.getQuantity()))
        items[i1][i2].decrQuantity()
        print ("Quantity " +
          is.getQuantity())
        amount -= is.getPrice()
        print("Amount remaining " +
          amount)

    def showTotal(self, input):
        amount += ((Money)input).getValue()
        print("Total amount = " + amount)

    def returnChange(self, input):
        print("Returning " + amount)
        amount = 0

    def showDigit(self, input):
        first = (FirstDigit)input
        print("First Digit= "+ first)

    def __init__(self):
        StateMachine.__init__(self, State.quiescent)
        for(int i = 0 i < items.length i++)
            for(int j = 0 j < items[i].length j++)
                items[i][j] = ItemSlot((j+1)*25, 5)
        items[3][0] = ItemSlot(25, 0)
        """
        buildTable(Object[][][]{
         ::State.quiescent, # Current state
            # Input, test, transition, next state:
           :Money.class, null,
             showTotal, State.collecting,
         ::State.collecting, # Current state
            # Input, test, transition, next state:
           :Quit.quit, null,
             returnChange, State.quiescent,
           :Money.class, null,
             showTotal, State.collecting,
           :FirstDigit.class, null,
             showDigit, State.selecting,
         ::State.selecting, # Current state
            # Input, test, transition, next state:
           :Quit.quit, null,
             returnChange, State.quiescent,
           :SecondDigit.class, notEnough,
             clearSelection, State.collecting,
           :SecondDigit.class, itemNotAvailable,
             clearSelection, State.unavailable,
           :SecondDigit.class, itemAvailable,
             dispense, State.wantMore,
         ::State.unavailable, # Current state
            # Input, test, transition, next state:
           :Quit.quit, null,
             returnChange, State.quiescent,
           :FirstDigit.class, null,
             showDigit, State.selecting,
         ::State.wantMore, # Current state
            # Input, test, transition, next state:
           :Quit.quit, null,
             returnChange, State.quiescent,
           :FirstDigit.class, null,
             showDigit, State.selecting,
        )
        """