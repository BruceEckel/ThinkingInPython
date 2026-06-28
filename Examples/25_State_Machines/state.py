# state.py
# A State has an operation, and can be moved
# into the next State given an Input:

class State:
    def run(self) -> None:
        raise NotImplementedError("run not implemented")
    def next(self, event: object) -> State:
        raise NotImplementedError("next not implemented")
