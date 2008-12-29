# StateMachine/vendingmachine/VendingMachineTest.py
# Demonstrates use of StateMachine.py

vm = VendingMachine()
for input in [
    Money.quarter,
    Money.quarter,
    Money.dollar,
    FirstDigit.A,
    SecondDigit.two,
    FirstDigit.A,
    SecondDigit.two,
    FirstDigit.C,
    SecondDigit.three,
    FirstDigit.D,
    SecondDigit.one,
    Quit.quit]:
    vm.nextState(input)