# round_trip.py
import pickle
from frozen_sketch import Drawing

drawing = Drawing("Duck").draw("circle").draw("beak")
restored = pickle.loads(pickle.dumps(drawing))
print(restored == drawing, restored is drawing)
#: True False
