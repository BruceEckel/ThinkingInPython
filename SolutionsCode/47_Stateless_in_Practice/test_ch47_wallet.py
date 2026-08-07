# test_ch47_wallet.py
from collections.abc import Callable, Iterator
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

def spree(prices: tuple[int, ...]) -> Depend[Get | Put, int]:
    bought = 0
    for price in prices:
        if (yield from purchase(price)):
            bought += 1
    return bought

def reading(balances: Iterator[int]) -> Callable[[Get], int]:
    def read(request: Get) -> int:
        return next(balances)
    return read

def recording(written: list[int]) -> Callable[[Put], None]:
    def write(request: Put) -> None:
        written.append(request.amount)
    return write

def test_spree_attempts_every_price() -> None:
    written: list[int] = []
    balances = iter([100, 40, 40, 10])
    half = handle(reading(balances))(spree)
    shop = handle(recording(written))(half)
    assert run(shop((60, 50, 30, 20))) == 2
    assert written == [40, 10]

written: list[int] = []
scripted = handle(recording(written))(
    handle(reading(iter([100, 40, 40, 10])))(spree))
print(run(scripted((60, 50, 30, 20))), written)
#: 2 [40, 10]
