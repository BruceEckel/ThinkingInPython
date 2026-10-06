# weak_responder.py
import gc
from weakref import WeakMethod
from broadcaster import Broadcaster
from exceptions import expected

class Plot:
    def redraw(self, celsius: float) -> None:
        print(f"plot: {celsius}C")

broadcaster = Broadcaster[float]()
plot = Plot()
ref = WeakMethod(plot.redraw)

def weak(celsius: float) -> None:
    live = ref()
    if live is None:
        broadcaster.disconnect(weak)  # Gone: drop out
    else:
        live(celsius)

broadcaster.connect(weak)
broadcaster.announce(25.0)
#: plot: 25.0C

del plot  # The only strong reference
gc.collect()
broadcaster.announce(30.0)  # Prints nothing

with expected(ValueError):
    broadcaster.disconnect(weak)
#: [ValueError] list.remove(x): x not in list
