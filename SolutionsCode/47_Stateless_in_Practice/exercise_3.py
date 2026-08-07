# exercise_3.py
from grid import (
    Backup,
    Battery,
    Blackout,
    Grid,
    Solar,
    Turbine,
    controller,
    run_load,
)
from stateless import handle, run

full = controller((Solar(), Turbine(range(19, 22)), Battery(40),
                   Grid(range(22, 24)), Backup(3)))
run(handle(full)(run_load)(17, 6))
#: Solar online
#:   17:00
#:   18:00
#: Solar offline
#: Turbine online
#:   19:00
#:   20:00
#:   21:00
#: Turbine offline
#: Battery online
#:   22:00
#: Battery offline

short = controller((Solar(), Turbine(range(19, 20)), Battery(0),
                    Grid(range(0, 24)), Backup(0)))
try:
    run(handle(short)(run_load)(17, 6))
except Blackout as e:
    print(f"Blackout at hour {e.args[0]}, out of run()")
#: Solar online
#:   17:00
#:   18:00
#: Solar offline
#: Turbine online
#:   19:00
#: Turbine offline
#: Blackout at hour 20, out of run()
