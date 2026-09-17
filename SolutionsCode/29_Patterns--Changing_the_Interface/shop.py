# shop.py
from record import record

@record
class _Engine:
    def start(self) -> None:
        print("_Engine.start()")

@record
class _FuelPump:
    engine: _Engine

    def prime(self) -> None:
        print("_FuelPump.prime()")
        self.engine.start()

@record
class _Ignition:
    pump: _FuelPump

    def turn_key(self) -> None:
        print("_Ignition.turn_key()")
        self.pump.prime()

def start_car() -> _Ignition:
    ignition = _Ignition(_FuelPump(_Engine()))
    ignition.turn_key()
    return ignition
