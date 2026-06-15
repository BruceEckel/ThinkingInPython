# state_machine.py
# Takes a list of Inputs to move from State to
# State using a template method.

class StateMachine:
    def __init__(self, initial_state):
        self.currentState = initial_state
        self.currentState.run()
    # Template method:
    def run_all(self, inputs):
        for i in inputs:
            print(i)
            self.currentState = self.currentState.next(i)
            self.currentState.run()
