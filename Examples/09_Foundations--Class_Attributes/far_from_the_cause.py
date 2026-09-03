# far_from_the_cause.py

class Stars:
    rating = 5  # Shared across all instances

def sell(star: Stars) -> None:
    star.rating = 1  # Shadows, buried in a helper

def show(star: Stars) -> None:
    print(star.rating)  # Reads far from where it shadowed

a, b = Stars(), Stars()
sell(a)
show(a)
#: 1
show(b)  # sell() never touched b
#: 5
