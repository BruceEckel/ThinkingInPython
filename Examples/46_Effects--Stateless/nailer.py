# nailer.py
from record import record
from stateless import Depend, Need, need

@record
class Material:
    strength: int

@record
class Nailer:
    force: int

def holds() -> Depend[Need[Material] | Need[Nailer], bool]:
    material = yield from need(Material)
    nailer = yield from need(Nailer)
    return nailer.force < material.strength
