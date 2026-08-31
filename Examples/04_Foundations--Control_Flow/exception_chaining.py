# exception_chaining.py
import textwrap
import traceback

class BadNumber(Exception):
    pass

def implicit(text):
    try:
        return int(text)
    except ValueError:
        raise BadNumber(text)

def explicit(text):
    try:
        return int(text)
    except ValueError as e:
        raise BadNumber(text) from e

def suppressed(text):
    try:
        return int(text)
    except ValueError:
        raise BadNumber(text) from None

def joining_line(e):
    for part in traceback.format_exception(e):
        line = part.strip()
        if (line.endswith("exception occurred:")
            or line.endswith("following exception:")):
            return line
    return "nothing shown above it"

for parse in (implicit, explicit, suppressed):
    try:
        parse("seven")
    except BadNumber as e:
        print(f"{parse.__name__}:")
        for chunk in textwrap.wrap(joining_line(e), 55):
            print(" ", chunk)
#: implicit:
#:   During handling of the above exception, another
#:   exception occurred:
#: explicit:
#:   The above exception was the direct cause of the
#:   following exception:
#: suppressed:
#:   nothing shown above it
