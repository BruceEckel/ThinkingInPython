# safe_demo.py
from result import Err, Ok
from safe import safe

@safe
def parse(text: str) -> int:
    return int(text)

if __name__ == "__main__":
    for text in ("42", "oops"):
        match parse(text):
            case Ok(answer):
                print(f"{text}: parsed {answer}")
            case Err(error):
                print(f"{text}: {type(error).__name__}")
#: 42: parsed 42
#: oops: ValueError
