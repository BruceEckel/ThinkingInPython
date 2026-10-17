# except_star.py
group = ExceptionGroup("batch", [
    ValueError(1), TypeError(2),
    ValueError(3), KeyError(4)])
try:
    try:
        raise group
    except* ValueError as values:
        print(f"ValueError: {values.exceptions}")
    except* TypeError as types:
        print(f"TypeError: {types.exceptions}")
except ExceptionGroup as rest:
    print(f"{rest.message}: {rest.exceptions}")
#: ValueError: (ValueError(1), ValueError(3))
#: TypeError: (TypeError(2),)
#: batch: (KeyError(4),)
