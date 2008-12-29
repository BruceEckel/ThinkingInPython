# QuickPython/differentReturns.py
def differentReturns(arg):
    if arg == 1:
        return "one"
    if arg == "one":
        return True

print(differentReturns(1))
print(differentReturns("one"))