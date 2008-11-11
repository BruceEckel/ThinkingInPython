# unitTesting/UnitTest.py
# The basic unit testing class

class UnitTest:
    testID = ""
    static List errors = ArrayList()
    # Override cleanup() if test object
    # creation allocates non-memory
    # resources that must be cleaned up:
    def cleanup(self):
    # Verify the truth of a condition:
    def affirm(boolean condition):
        if(!condition)
            errors.add("failed: " + testID)