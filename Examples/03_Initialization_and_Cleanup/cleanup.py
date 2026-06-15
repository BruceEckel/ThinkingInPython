# cleanup.py
class Counter:
    count: int = 0   # Number of objects of this class

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, 'created')
        Counter.count += 1

    def __del__(self) -> None:
        print(self.name, 'deleted')
        Counter.count -= 1
        if Counter.count == 0:
            print('Last Counter object deleted')
        else:
            print(Counter.count, 'Counter objects remaining')


x = Counter("First")
del x
