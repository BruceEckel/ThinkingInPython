# flexible_args_and_returns.py

def flexible_args_and_returns(arg):
    if arg == 1:
        return "one"
    if arg == "one":
        return True

print(flexible_args_and_returns(1))
## one
print(flexible_args_and_returns("one"))
## True
