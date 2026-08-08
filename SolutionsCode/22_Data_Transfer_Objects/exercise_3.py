# exercise_3.py
from typing import NamedTuple

class Recipe(NamedTuple):
    name: str
    steps: list[str]

toast = Recipe("Toast", ["slice", "heat"])
toast.steps.append("butter")
print(toast)
#: Recipe(name='Toast', steps=['slice', 'heat', 'butter'])
try:
    key = {toast: "breakfast"}
except TypeError as e:
    print(type(e).__name__)
#: TypeError
