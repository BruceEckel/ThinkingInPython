# var_args.py

def report(label, *values, **options):
    print(label, values, options)

report("nums", 1, 2, 3)
## nums (1, 2, 3) {}
report("point", 3, 4, color="red", size=10)   # Extras land in options
## point (3, 4) {'color': 'red', 'size': 10}
