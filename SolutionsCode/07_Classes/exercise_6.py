# exercise_6.py

class Base:
    def show(self):
        print("Base.show")

class Derived(Base):
    # @override  # Uncomment this and the import to see it complain
    def shwo(self):
        print("Derived.shwo")

Derived().show()
#: Base.show
