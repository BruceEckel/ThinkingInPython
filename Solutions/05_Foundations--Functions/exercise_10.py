# exercise_10.py
from exceptions import expect

def report(label, *values, **options):
    print(label, values, options)

def trace(func, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

expect(TypeError, trace, report, "point", func="f")  # type: ignore
#: [TypeError] trace() got multiple values for argument
#: 'func'

def positional_trace(func, /, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

positional_trace(report, "point", func="f")
#: calling report
#: point () {'func': 'f'}
