# noted_result.py
from result import Err, Ok, Result

def parse_field(name: str, text: str) -> Result[int, Exception]:
    try:
        return Ok(int(text))
    except ValueError as e:
        e.add_note(f"field {name!r} received {text!r}")
        return Err(e)

for field, value in (("age", "42"), ("size", "oops")):
    result = parse_field(field, value)
    if isinstance(result, Ok):
        print(f"{field} = {result.answer}")
    else:
        print(f"{field}: {type(result.error).__name__}")
        for note in result.error.__notes__:
            print(f"  {note}")
#: age = 42
#: size: ValueError
#:   field 'size' received 'oops'
