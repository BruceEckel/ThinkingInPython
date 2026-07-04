# round_trip.py
import pickle
from frozen_sketch import Sketch

drawing = Sketch("Duck").draw("circle").draw("beak")
restored = pickle.loads(pickle.dumps(drawing))
print(restored == drawing, restored is drawing)
#: True False
