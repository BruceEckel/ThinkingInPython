# exercise_6.py

class Base:
    def display(self):
        print("Base.display")

class Derived(Base):
    # @override  # Uncomment (and import) to see it complain
    def show(self):
        print("Derived.show")

Derived().show()
#: Derived.show
