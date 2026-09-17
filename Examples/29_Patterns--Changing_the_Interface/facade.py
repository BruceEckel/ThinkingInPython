# facade.py
from record import record

@record
class Engine:
    def start(self) -> None:
        print("Engine.start()")

@record
class FuelPump:
    engine: Engine

    def prime(self) -> None:
        print("FuelPump.prime()")
        self.engine.start()

@record
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
