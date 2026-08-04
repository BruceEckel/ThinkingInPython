# add_note.py
import traceback

def parse_seconds(text: str) -> int:
    try:
        return int(text)
    except ValueError as e:
        e.add_note(f"timeout was set to {text!r}")
        e.add_note("expected a whole number of seconds")
        raise

try:
    parse_seconds("soon")
except ValueError as e:
    print("".join(traceback.format_exception_only(e)), end="")
#: ValueError: invalid literal for int() with base 10: 'soon'
#: timeout was set to 'soon'
#: expected a whole number of seconds
