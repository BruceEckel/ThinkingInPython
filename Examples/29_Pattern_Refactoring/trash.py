# trash.py
# The Trash hierarchy, with self-registration and a per-pound value.


class Trash:
    value: float = 0.0  # dollars per pound, set by each subclass
    registry: dict[str, type[Trash]] = {}  # name -> subclass

    def __init__(self, weight: float) -> None:
        self.weight = weight

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Trash.registry[cls.__name__] = cls

    @classmethod
    def create(cls, name: str, weight: float) -> Trash:
        return Trash.registry[name](weight)


class Aluminum(Trash):
    value = 1.67


class Paper(Trash):
    value = 0.10


class Glass(Trash):
    value = 0.23


class Cardboard(Trash):
    value = 0.79


def sum_value(items: list[Trash]) -> float:
    total = 0.0
    for t in items:
        print(f"weight of {type(t).__name__} = {t.weight}")
        total += t.weight * t.value
    print(f"Total value = {total:.2f}")
    return total
