# state.py
# A State has an operation, and can be moved
# into the next State given an Input:

class State:
    def run(self):
        raise NotImplementedError("run not implemented")
    def next(self, input):
        raise NotImplementedError("next not implemented")
