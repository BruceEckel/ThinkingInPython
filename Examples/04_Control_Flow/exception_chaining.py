# exception_chaining.py

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

def earlier(e):
    if e.__cause__ is not None:
        return f"direct cause: {type(e.__cause__).__name__}"
    if e.__context__ is not None and not e.__suppress_context__:
        return f"during handling: {type(e.__context__).__name__}"
    return "nothing earlier shown"

for parse in (implicit, explicit, suppressed):
    try:
        parse("seven")
    except BadNumber as e:
        print(f"{parse.__name__}: {earlier(e)}")
#: implicit: during handling: ValueError
#: explicit: direct cause: ValueError
#: suppressed: nothing earlier shown
