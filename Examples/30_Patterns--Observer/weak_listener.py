# weak_listener.py
from weakref import WeakMethod
from broadcaster import Broadcaster
from exceptions import expected

class Plot:
    def redraw(self, celsius: float) -> None:
        print(f"plot: {celsius}C")

source = Broadcaster[float]()
plot = Plot()
ref = WeakMethod(plot.redraw)

def weak(celsius: float) -> None:
    live = ref()
    if live is None:
        source.unsubscribe(weak)  # Gone: drop out
    else:
        live(celsius)

source.subscribe(weak)
source.announce(25.0)
#: plot: 25.0C

del plot  # The only strong reference
source.announce(30.0)  # Prints nothing

with expected(ValueError):
    source.unsubscribe(weak)
#: [ValueError] list.remove(x): x not in list
