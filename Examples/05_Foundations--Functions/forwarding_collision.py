# forwarding_collision.py

def report(label, *values, **options):
    print(label, values, options)

def trace(func, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

nums = (1, 2, 3)
opts = {"label": "oops", "color": "red"}
try:
    trace(report, *nums, **opts)
except TypeError as e:
    print(e)
#: calling report
#: report() got multiple values for argument 'label'
