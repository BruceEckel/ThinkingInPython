# tabledriven/vending_view.py
import tkinter as tk
from functools import partial
from vending_machine import (
    FirstDigit,
    Money,
    Quit,
    SecondDigit,
    VendingMachine,
)

def show() -> None:
    vm = VendingMachine()
    root = tk.Tk()
    root.title("Vending Machine")
    display = tk.Label(root, width=34, anchor="w")
    display.grid(row=0, column=0, columnspan=4, sticky="we")
    buttons: list[list[tk.Button]] = []

    def render() -> None:
        display.config(text=f"Inserted {vm.amount}c   {vm.message}")
        for r, row in enumerate(vm.items):
            for c, slot in enumerate(row):
                out = slot.quantity == 0
                qty = "OUT" if out else f"x{slot.quantity}"
                buttons[r][c].config(
                    text=f"{r}{c}\n{slot.price}c\n{qty}",
                    state="disabled" if out else "normal")

    def send(event: object) -> None:
        try:
            vm.handle(event)
        except RuntimeError:
            vm.message = "not allowed yet"
        render()

    def select(r: int, c: int) -> None:
        send(FirstDigit(f"row {r}", r))
        send(SecondDigit(f"col {c}", c))

    tk.Button(root, text="+25c",
              command=lambda: send(Money("quarter", 25))
              ).grid(row=1, column=0, sticky="we")
    tk.Button(root, text="+$1",
              command=lambda: send(Money("dollar", 100))
              ).grid(row=1, column=1, sticky="we")
    tk.Button(root, text="Refund",
              command=lambda: send(Quit())
              ).grid(row=1, column=2, columnspan=2, sticky="we")

    for r in range(4):
        button_row: list[tk.Button] = []
        for c in range(4):
            b = tk.Button(root, width=6, height=3,
                          command=partial(select, r, c))
            b.grid(row=2 + r, column=c)
            button_row.append(b)
        buttons.append(button_row)

    render()
    root.mainloop()

if __name__ == "__main__":
    show()
