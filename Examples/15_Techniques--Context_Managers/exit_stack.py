# exit_stack.py
from contextlib import ExitStack
from multiple import tag

def wrap(names: list[str]) -> None:
    with ExitStack() as stack:
        open_tags = [
            stack.enter_context(tag(n)) for n in names]
        print("using", open_tags)

if __name__ == "__main__":
    wrap(["a", "b"])
    wrap(["a", "b", "c"])
#: <a>
#: <b>
#: using ['a', 'b']
#: </b>
#: </a>
#: <a>
#: <b>
#: <c>
#: using ['a', 'b', 'c']
#: </c>
#: </b>
#: </a>
