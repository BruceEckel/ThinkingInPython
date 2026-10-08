# marked_methods.py
from collections.abc import Callable
from typing import Any, ClassVar

def on[F: Callable[..., object]](
        event: str
) -> Callable[[F], F]:
    def mark(func: F) -> F:
        func.__dict__["event"] = event
        return func
    return mark

class Widget:
    handlers: ClassVar[dict[str, Callable[..., Any]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        marked = {
            attr.__dict__["event"]: attr
            for attr in vars(cls).values()
            if "event" in getattr(attr, "__dict__", {})
        }
        cls.handlers = {**cls.handlers, **marked}

    def dispatch(self, event: str) -> None:
        self.handlers[event](self)

class Button(Widget):
    @on("click")
    def press(self) -> None:
        print("pressed")

    @on("hover")
    def glow(self) -> None:
        print("glowing")

    def label(self) -> str:
        return "OK"

class SubmitButton(Button):
    @on("submit")
    def send(self) -> None:
        print("sent")

print(sorted(Button.handlers))
#: ['click', 'hover']
print(sorted(SubmitButton.handlers))
#: ['click', 'hover', 'submit']
Button().dispatch("click")
#: pressed
print(Button.press.__dict__)
#: {'event': 'click'}
# ty: Function `press` has no attribute `event`:
# print(Button.press.event)
