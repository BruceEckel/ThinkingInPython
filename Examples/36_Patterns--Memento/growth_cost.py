# growth_cost.py
from frozen_sketch import Drawing

states = [Drawing("Duck")]
for i in range(2000):
    states.append(states[-1].draw(str(i)))
print(sum(len(s.strokes) for s in states),
      len(states[-1].strokes))
#: 2001000 2000
