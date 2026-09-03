# nested_handle.py
from typing import reveal_type
from ask_tell_stateless import capture, greet, scripted
from stateless import handle

nested = handle(scripted)(handle(capture)(greet))
half = handle(capture)(greet)
full = handle(scripted)(half)

if __name__ == "__main__":
    reveal_type(nested)
    reveal_type(half)
    reveal_type(full)
