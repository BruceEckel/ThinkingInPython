# slope_edge.py
from nonzero import NonZero, slope
from result import Err, Ok, Result

def parse_run(text: str) -> Result[NonZero, ValueError]:
    try:
        return Ok(NonZero(int(text)))
    except ValueError as error:
        return Err(error)

for text in ["2", "0", "two"]:
    match parse_run(text):
        case Ok(run):
            print(f"{text!r}: {slope(10, run)}")
        case Err(error):
            print(f"{text!r}: {error}")
#: '2': 5.0
#: '0': NonZero cannot hold 0
#: 'two': invalid literal for int() with base 10: 'two'
