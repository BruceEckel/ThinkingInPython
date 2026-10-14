# add_note.py
import traceback

def parse_seconds(text: str) -> int:
    try:
        return int(text)
    except ValueError as e:
        e.add_note("expected a whole number of seconds")
        raise

def read_setting(name: str, text: str) -> int:
    try:
        return parse_seconds(text)
    except ValueError as e:
        e.add_note(f"setting {name!r} was {text!r}")
        raise

try:
    read_setting("timeout", "no")
except ValueError as e:
    print("".join(traceback.format_exception_only(e)),
          end="")
#: ValueError: invalid literal for int() with base 10: 'no'
#: expected a whole number of seconds
#: setting 'timeout' was 'no'
