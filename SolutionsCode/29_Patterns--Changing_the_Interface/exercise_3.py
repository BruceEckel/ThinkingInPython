# exercise_3.py
import shop
from shop import start_car

start_car()
#: _Ignition.turn_key()
#: _FuelPump.prime()
#: _Engine.start()
print([name for name in vars(shop)
       if not name.startswith("_")])
#: ['record', 'start_car']
