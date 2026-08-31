# del_swallows.py

class Resource:
    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        raise RuntimeError(f"{self.name} not released")

resource = Resource("db")
del resource
print("still running")
#: still running
