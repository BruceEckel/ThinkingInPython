# forwarding_collision.py
from exceptions import expect

def report(label, *values, **options):
    print(label, values, options)

def trace(func, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

nums = (1, 2, 3)
opts = {"label": "oops", "color": "red"}
expect(TypeError, trace, report, *nums, **opts)
#: calling report
#: [TypeError] report() got multiple values for argument
#: 'label'
