# forgot_self.py

class Forgetful:
    def show():  # Missing the self parameter
        print("never runs")

try:
    Forgetful().show()  # type: ignore
except TypeError as e:
    print(e)
#: Forgetful.show() takes 0 positional arguments but 1 was given
