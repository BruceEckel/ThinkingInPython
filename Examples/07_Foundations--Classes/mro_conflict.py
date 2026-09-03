# mro_conflict.py

class A:
    def show(self):
        print("A.show")

class B:
    def show(self):
        print("B.show")

class C(A, B):
    pass  # Defines no show() of its own

print([c.__name__ for c in C.__mro__])
#: ['C', 'A', 'B', 'object']
C().show()  # A comes first in the MRO
#: A.show
