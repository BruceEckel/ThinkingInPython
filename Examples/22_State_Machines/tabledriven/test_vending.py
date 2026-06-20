# tabledriven/test_vending.py
import pytest
from vending_machine import (
    FirstDigit,
    Money,
    Quit,
    SecondDigit,
    State,
    VendingMachine,
)


def feed(vm: VendingMachine, *events: object) -> None:
    for event in events:
        vm.handle(event)


def test_buy_dispenses_and_charges() -> None:
    vm = VendingMachine()
    assert vm.state is State.QUIESCENT
    # Item [0][1], 50c
    feed(vm, Money("quarter", 25), Money("quarter", 25),
         FirstDigit("A", 0), SecondDigit("two", 1))
    assert vm.state is State.WANT_MORE
    assert vm.amount == 0                 # 50 in, 50 spent
    assert vm.items[0][1].quantity == 4   # One dispensed from five
    assert vm.message == "Dispensing; amount remaining 0"


def test_too_expensive_clears_back_to_collecting() -> None:
    vm = VendingMachine()
    # 50c item, 25c in
    feed(vm, Money("quarter", 25),
         FirstDigit("A", 0), SecondDigit("two", 1))
    assert vm.state is State.COLLECTING
    assert vm.amount == 25                # Money kept
    assert vm.items[0][1].quantity == 5   # Nothing dispensed


def test_sold_out_goes_to_unavailable() -> None:
    vm = VendingMachine()
    # [3][0] is sold out
    feed(vm, Money("quarter", 25),
         FirstDigit("D", 3), SecondDigit("one", 0))
    assert vm.state is State.UNAVAILABLE
    assert vm.items[3][0].quantity == 0


def test_quit_refunds_and_resets() -> None:
    vm = VendingMachine()
    feed(vm, Money("dollar", 100), Quit())
    assert vm.state is State.QUIESCENT
    assert vm.amount == 0


def test_no_transition_raises() -> None:
    vm = VendingMachine()  # QUIESCENT has no transition for Quit
    with pytest.raises(RuntimeError):
        vm.handle(Quit())
