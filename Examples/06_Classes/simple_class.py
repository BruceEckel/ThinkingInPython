# simple_class.py

class Simple:
    def __init__(self, str):
        print("Inside the Simple constructor")
        self.s = str
    # Two methods:
    def show(self, msg=""):
        if msg:
            print(msg + ':', self.s)
        else:
            print(self.s)
    def show_twice(self):
        self.show()  # Calling another method
        self.show()

if __name__ == "__main__":
    # Create an object:
    x = Simple("Constructor argument")
    x.show()
    x.show("A message")
    x.show_twice()
