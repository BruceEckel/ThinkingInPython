# wallet.py
from dataclasses import dataclass
from stateless import Ability, Depend, handle, run

class Get(Ability[int]):
    pass

@dataclass(frozen=True)
class Put(Ability[None]):
    amount: int

def get() -> Depend[Get, int]:
    amount: int = yield from Get()
    return amount

def put(amount: int) -> Depend[Put, None]:
    yield from Put(amount)

def purchase(price: int) -> Depend[Get | Put, bool]:
    funds = yield from get()
    if funds < price:
        return False
    yield from put(funds - price)
    return True

def spree(prices: tuple[int, ...]) -> Depend[
    Get | Put, int
]:
    bought = 0
    for price in prices:
        if (yield from purchase(price)):
            bought += 1
    return bought

@dataclass
class Cell:
    amount: int

cell = Cell(100)

def read(request: Get) -> int:
    return cell.amount

def write(request: Put) -> None:
    cell.amount = request.amount

half = handle(read)(spree)
shop = handle(write)(half)
print(run(shop((60, 50, 30, 20))))
#: 2
print(f"remaining: {cell.amount}")
#: remaining: 10
