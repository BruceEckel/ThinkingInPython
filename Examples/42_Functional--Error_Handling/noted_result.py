# noted_result.py
from result import Err, Ok, Result

def parse_field(name: str,
                text: str) -> Result[int, Exception]:
    try:
        return Ok(int(text))
    except ValueError as e:
        e.add_note(f"field {name!r} received {text!r}")
        return Err(e)

for name, text in (("age", "42"), ("size", "oops")):
    match parse_field(name, text):
        case Ok(answer):
            print(f"{name} = {answer}")
        case Err(error):
            print(f"{name}: {type(error).__name__}")
            for note in error.__notes__:
                print(f"  {note}")
#: age = 42
#: size: ValueError
#:   field 'size' received 'oops'
