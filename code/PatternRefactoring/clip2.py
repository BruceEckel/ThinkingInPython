# PatternRefactoring/clip2.py
class Messenger:
    # Must change this to add another type:
    MAX_NUM = 4
    def __init__(self, typeNum, val):
        self.type = typeNum % MAX_NUM
        self.data = val