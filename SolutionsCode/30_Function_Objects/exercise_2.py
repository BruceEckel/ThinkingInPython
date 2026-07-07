# exercise_2.py
TOLERANCE = 1e-12
MAX_ITER = 200

def bisection(f, a, b):
    if f(a) * f(b) > 0:
        return None
    mid = (a + b) / 2
    for _ in range(MAX_ITER):
        if abs(f(mid)) < TOLERANCE:
            return mid
        if f(a) * f(mid) < 0:
            b = mid
        else:
            a = mid
        mid = (a + b) / 2
    return mid

def secant(f, a, b):
    x0, x1 = a, b
    for _ in range(MAX_ITER):
        f0, f1 = f(x0), f(x1)
        if f1 == f0:
            return None
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < TOLERANCE:
            return x2
        x0, x1 = x1, x2
    return None

def newton(f, a, b):
    x = (a + b) / 2
    h = 1e-7
    for _ in range(MAX_ITER):
        slope = (f(x + h) - f(x - h)) / (2 * h)
        if slope == 0:
            return None
        step = f(x) / slope
        x -= step
        if abs(step) < TOLERANCE:
            return x
    return None

def solve(f, a, b, chain):
    for finder in chain:
        root = finder(f, a, b)
        if root is not None:
            print(f"{finder.__name__} succeeded: {root:.6f}")
            return root
        print(f"{finder.__name__} failed: could not converge")
    print("all finders failed")
    return None

def f(x):
    return x * x - 2

solve(f, 1.0, 1.3, [bisection, secant, newton])
#: bisection failed: could not converge
#: secant succeeded: 1.414214
