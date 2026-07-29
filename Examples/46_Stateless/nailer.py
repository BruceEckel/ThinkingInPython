# nailer.py
from dataclasses import dataclass
from stateless import Depend, Need, need

@dataclass(frozen=True)
class Material:
    brittleness: int

@dataclass(frozen=True)
class Nailer:
    force: int

def holds() -> Depend[Need[Material] | Need[Nailer], bool]:
    material = yield from need(Material)
    nailer = yield from need(Nailer)
    return nailer.force < material.brittleness
