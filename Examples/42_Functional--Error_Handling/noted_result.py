# noted_result.py
from result import Err, Ok, Result

def parse_field(name: str,
                text: str) -> Result[int, Exception]:
    try:
        return Ok(int(text))
    except ValueError as e:
        e.add_note(f"field {name!r} received {text!r}")
        return Err(e)

results = [parse_field("age", "42"),
           parse_field("size", "oops")]
for result in results:
    match result:
        case Ok():
            print(result)
        case Err(error):
            print(type(error).__name__)
            for note in error.__notes__:
                print(f"  {note}")
#: Ok(answer=42)
#: ValueError
#:   field 'size' received 'oops'
