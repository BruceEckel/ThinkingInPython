# weak_listener.py
from weakref import WeakMethod

class Plot:
    def redraw(self, celsius: float) -> None:
        print(f"plot: {celsius}C")

plot = Plot()
ref = WeakMethod(plot.redraw)
live = ref()
if live is not None:
    live(25.0)
#: plot: 25.0C

# The bound method holds plot too
del plot, live
print(ref())
#: None
