# UnitTesting/TestDemo2.py
# Inheriting from a class that
# already has a test is no problem.

class TestDemo2(TestDemo):
    def __init__(self, s): TestDemo.__init__(s)
    # You can even use the same name
    # as the test class in the base class:
    class Test(UnitTest):
        def testA(self):
            print("TestDemo2.testA")
            affirm(1 + 1 == 2)

        def testB(self):
            print("TestDemo2.testB")
            affirm(2 * 2 == 4)