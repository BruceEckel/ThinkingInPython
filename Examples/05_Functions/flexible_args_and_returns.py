# flexible_args_and_returns.py

def flexible_args_and_returns(arg):
    if arg == 1:
        return "Hello"
    if arg == "one":
        return 2

print(flexible_args_and_returns(1))
#: Hello
print(flexible_args_and_returns("one"))
#: 2
