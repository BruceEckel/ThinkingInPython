# UnitTesting/TestDemo.py
# Creating a test

class TestDemo:
    objCounter = 0
    id = ++objCounter
    def TestDemo(String s):
        print(s + ": count = " + id)

    def close(self):
        print("Cleaning up: " + id)

    def someCondition(self): return True
    class Test(UnitTest):
        TestDemo test1 = TestDemo("test1")
        TestDemo test2 = TestDemo("test2")
        def cleanup(self):
            test2.close()
            test1.close()

        def testA(self):
            print("TestDemo.testA")
            affirm(test1.someCondition())

        def testB(self):
            print("TestDemo.testB")
            affirm(test2.someCondition())
            affirm(TestDemo.objCounter != 0)

        # Causes the build to halt:
        #! def test3(): affirm(0)