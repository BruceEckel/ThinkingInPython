# override_intro.py
from typing import override

class Base:
    def show(self):
        print("Base.show")

class Derived(Base):
    @override
    def show(self):
        print("Derived.show")

Derived().show()
## Derived.show
