# generic_box.py

class Box[T]:
    def __init__(self, content: T) -> None:
        self.content = content

    def get(self) -> T:
        return self.content

box = Box("gift")  # A Box[str]
print(box.get().upper())
#: GIFT
