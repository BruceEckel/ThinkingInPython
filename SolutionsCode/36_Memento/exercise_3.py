# exercise_3.py
import json
from dataclasses import asdict, dataclass, replace

@dataclass(frozen=True)
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

drawing = Drawing("Duck").draw("circle").draw("beak")
as_json = json.dumps(asdict(drawing))
data = json.loads(as_json)
print(type(data["strokes"]))
#: <class 'list'>
reconstructed = Drawing(
    data["title"], tuple(data["strokes"]))
print(reconstructed == drawing)
#: True
