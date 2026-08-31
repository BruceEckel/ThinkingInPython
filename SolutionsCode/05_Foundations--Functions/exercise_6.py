# exercise_6.py
def report(label, *values, **options):
    print(label, values, options)

args = ("point", 3, 4)
opts = {"color": "red"}
report(*args, **opts)
#: point (3, 4) {'color': 'red'}
