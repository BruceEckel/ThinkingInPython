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

def name(e):
    return None if e is None else type(e).__name__

for parse in (implicit, explicit, suppressed):
    try:
        parse("seven")
    except BadNumber as e:
        print(parse.__name__, name(e.__cause__),
              name(e.__context__), e.__suppress_context__)
#: implicit None ValueError False
#: explicit ValueError ValueError True
#: suppressed None ValueError True
