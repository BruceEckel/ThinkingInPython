# test_wallet.py
from stateless import handle, run
from wallet import Cell, ledger, spree

def test_spree_spends_from_its_own_cell() -> None:
    cell = Cell(100)
    read, write = ledger(cell)
    half = handle(read)(spree)
    shop = handle(write)(half)
    assert run(shop((60, 50, 30, 20))) == 2
    assert cell.amount == 10
