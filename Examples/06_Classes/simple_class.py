# simple_class.py

class Simple:
    def __init__(self, text):
        print("Inside the Simple constructor")
        self.s = text
    # Two methods:
    def show(self, msg=""):
        if msg:
            print(msg + ':', self.s)
        else:
            print(self.s)
    def show_twice(self):
        self.show()  # Calling another method
        self.show()
