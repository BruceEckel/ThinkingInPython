# register.py
registry: dict[str, type] = {}

def register(cls: type) -> type:
    registry[cls.__name__] = cls
    return cls

@register
class Espresso:
    ...

@register
class Latte:
    ...

if __name__ == "__main__":
    print(sorted(registry))
## ['Espresso', 'Latte']
