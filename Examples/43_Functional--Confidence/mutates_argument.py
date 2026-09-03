# mutates_argument.py
def add_item(cart: list[str], item: str) -> list[str]:
    cart.append(item)
    return cart

cart: list[str] = ["milk"]
add_item(cart, "eggs")
add_item(cart, "eggs")
print(cart)
#: ['milk', 'eggs', 'eggs']
