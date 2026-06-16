# real_defaults.py
# For per-object defaults, write a constructor, or use a @dataclass,
# which turns the class-attribute syntax into exactly that.
from dataclasses import dataclass


class A:
    def __init__(self, x: int = 100) -> None:
        self.x = x  # an instance variable, one per object


@dataclass
class B:
    x: int = 100  # a constructor default, not a shared value


if __name__ == "__main__":
    a = A()
    a.x = -1
    print(a.x, A().x)  # -1 100: a's change does not leak
    print(B().x, B(7).x)  # 100 7
