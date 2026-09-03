# facade.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Engine:
    def start(self) -> None:
        print("Engine.start()")

@dataclass(frozen=True)
class FuelPump:
    engine: Engine

    def prime(self) -> None:
        print("FuelPump.prime()")
        self.engine.start()

@dataclass(frozen=True)
class Ignition:
    pump: FuelPump

    def turn_key(self) -> None:
        print("Ignition.turn_key()")
        self.pump.prime()

class Facade:
    @staticmethod
    def start_car() -> Ignition:
        ignition = Ignition(FuelPump(Engine()))
        ignition.turn_key()
        return ignition

Facade.start_car()
#: Ignition.turn_key()
#: FuelPump.prime()
#: Engine.start()
