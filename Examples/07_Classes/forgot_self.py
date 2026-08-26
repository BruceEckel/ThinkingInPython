# forgot_self.py

class Oops:
    def show():  # Missing the self parameter
        print("never runs")

try:
    Oops().show()  # type: ignore
except TypeError as e:
    print(e)
#: Oops.show() takes 0 positional arguments but 1 was given
