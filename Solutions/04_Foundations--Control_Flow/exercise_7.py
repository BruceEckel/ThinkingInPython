# exercise_7.py
import textwrap
import traceback

class BadNumber(Exception):
    pass

def substituted(text):
    try:
        return int(text)
    except ValueError:
        raise BadNumber(text) from ArithmeticError(
            "no digits here")

def joining_line(e):
    for part in traceback.format_exception(e):
        line = part.strip()
        if (line.endswith("exception occurred:")
            or line.endswith("following exception:")):
            return line
    return "nothing shown above it"

try:
    substituted("seven")
except BadNumber as e:
    for chunk in textwrap.wrap(joining_line(e), 55):
        print(" ", chunk)
    print(type(e.__cause__).__name__,
          type(e.__context__).__name__)
#:   The above exception was the direct cause of the
#:   following exception:
#: ArithmeticError ValueError
