# FunctionObjects/CommandPattern.py

class Command:
    def execute(self): pass

class Loony(Command):
    def execute(self):
        print("You're a loony.")

class NewBrain(Command):
    def execute(self):
        print("You might even need a new brain.")

class Afford(Command):
    def execute(self):
        print("I couldn't afford a whole new brain.")

# An object that holds commands:
class Macro:
    def __init__(self):
        self.commands = []
    def add(self, command):
        self.commands.append(command)
    def run(self):
        for c in self.commands:
            c.execute()

macro = Macro()
macro.add(Loony())
macro.add(NewBrain())
macro.add(Afford())
macro.run()