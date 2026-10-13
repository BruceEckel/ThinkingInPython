# sketch_demo.py
from sketch import Sketch

sketch = Sketch()
sketch.draw("circle")
sketch.draw("beak")
checkpoint = sketch.save()
sketch.draw("scribble")
print(sketch)
#: circle beak scribble
sketch.restore(checkpoint)
print(sketch)
#: circle beak
