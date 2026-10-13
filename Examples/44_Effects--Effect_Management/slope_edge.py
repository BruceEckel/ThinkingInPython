# slope_edge.py
from nonzero import NonZero, slope
from result import Err, Ok
from safe import safe

@safe
def parse_run(text: str) -> NonZero:
    return NonZero(int(text))

for text in ["2", "0"]:
    match parse_run(text):
        case Ok(run):
            print(f"{text!r}: {slope(10, run)}")
        case Err(error):
            print(f"{text!r}: {error}")
#: '2': 5.0
#: '0': NonZero cannot hold 0
