# prof_demo.py
def helper() -> int:
    return sum(i * i for i in range(10_000))

def slow() -> None:
    total = 0
    for i in range(2_000_000):
        total += i
    helper()

if __name__ == "__main__":
    slow()
