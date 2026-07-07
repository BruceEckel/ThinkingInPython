# exercise_4.py
def report(label, *values, total=False, **options):
    print(label, values, options)
    if total:
        print(sum(values))

report("nums", 1, 2, 3, total=True)
#: nums (1, 2, 3) {}
#: 6
