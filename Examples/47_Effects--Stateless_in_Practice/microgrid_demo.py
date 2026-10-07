# microgrid_demo.py
from microgrid import controller, run_load
from power import Backup, Battery, Grid, Solar
from stateless import handle, run

def site() -> tuple[Solar, Battery, Grid, Backup]:
    return (Solar(), Battery(40), Grid(range(22, 24)),
            Backup(3))

solar, battery, grid, backup = site()
sun_first = controller((solar, battery, grid, backup))
run(handle(sun_first)(run_load)(17, 6))
#: Solar online
#:   17:00
#:   18:00
#: Solar offline
#: Battery online
#:   19:00
#:   20:00
#: Battery offline
#: Grid online
#:   21:00
#: Grid offline
#: Backup online
#:   22:00
#: Backup offline
solar, battery, grid, backup = site()
battery_first = controller((battery, solar, grid, backup))
run(handle(battery_first)(run_load)(17, 4))
#: Battery online
#:   17:00
#:   18:00
#: Battery offline
#: Grid online
#:   19:00
#:   20:00
#: Grid offline
