# unitTesting/TooMuchAccess.py

class TooMuchAccess(UnitTest):
    Testable tst = Testable()
    def test1(self):
        tst.f2() # Oops!
        tst.f3() # Oops!
        tst.f4() # OK