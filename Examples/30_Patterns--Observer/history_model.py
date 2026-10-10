# history_model.py
from broadcaster import Broadcaster

class History(Broadcaster[str]):
    def __init__(self) -> None:
        super().__init__()
        self._history: list[str] = []

    @property
    def history(self) -> str:
        return "".join(self._history)

    def add(self, char: str) -> None:
        self._history.append(char)
        self.announce(self.history)
