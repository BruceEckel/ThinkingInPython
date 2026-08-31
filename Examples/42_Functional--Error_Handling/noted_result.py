# noted_result.py
from result import Err, Ok, Result

def parse_field(name: str,
                text: str) -> Result[int, Exception]:
    try:
        return Ok(int(text))
    except ValueError as e:
        e.add_note(f"field {name!r} received {text!r}")
        return Err(e)

for field, value in (("age", "42"), ("size", "oops")):
    match parse_field(field, value):
        case Ok(answer):
            print(f"{field} = {answer}")
        case Err(error):
            print(f"{field}: {type(error).__name__}")
            for note in error.__notes__:
                print(f"  {note}")
#: age = 42
#: size: ValueError
#:   field 'size' received 'oops'
