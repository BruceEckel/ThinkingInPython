# simple_class.py

class Simple:
    def __init__(self, text):
        print("Inside the Simple constructor")
        self.text = text
    def show(self, msg=""):
        if msg:
            print(f"{msg}:", self.text)
        else:
            print(self.text)
    def show_twice(self):
        self.show()
        self.show()
