# Py4Prog/different_returns.py
def different_returns(arg):
    if arg == 1:
        return "one"
    if arg == "one":
        return True

print(different_returns(1))
print(different_returns("one"))
