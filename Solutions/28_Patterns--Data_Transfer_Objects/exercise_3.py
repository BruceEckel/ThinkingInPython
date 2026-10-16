# exercise_3.py
from typing import NamedTuple
from exceptions import expected

class Recipe(NamedTuple):
    name: str
    steps: list[str]

toast = Recipe("Toast", ["slice", "heat"])
toast.steps.append("butter")
print(toast)
#: Recipe(name='Toast', steps=['slice', 'heat', 'butter'])
with expected(TypeError):
    key = {toast: "breakfast"}
#: [TypeError] cannot use 'Recipe' as a dict key (unhashable
#: type: 'list')
