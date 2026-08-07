# override_intro.py
from typing import override

class Base:
    def show(self):
        print("Base.show")

class Derived(Base):
    @override
    def show(self):
        print("Derived.show")

class Typo(Base):
    # @override  # "shwo" does not override anything
    def shwo(self):
        print("Typo.shwo")

Derived().show()
#: Derived.show
