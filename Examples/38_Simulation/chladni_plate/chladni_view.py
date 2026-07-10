# chladni_plate/chladni_view.py
import itertools
import tkinter as tk
from typing import Final
from chladni import Mode, Plate

SIZE: Final[int] = 560
DOT: Final[int] = 3
COLORS: Final[list[str]] = [
    "gold", "coral", "palegreen", "skyblue", "plum"]
MODES: Final[list[Mode]] = [(1, 2), (2, 3), (3, 4), (3, 5)]

def show(grains: int = 1200, step_ms: int = 30,
         frames_per_mode: int = 200) -> None:
    plate = Plate(grains, MODES[0])
    root = tk.Tk()
    root.title(f"Chladni Plate {plate.mode}")
    canvas = tk.Canvas(root, width=SIZE, height=SIZE,
                       background="black", highlightthickness=0)
    canvas.pack()
    palette = itertools.cycle(COLORS)
    dots = [
        canvas.create_oval(0, 0, DOT, DOT, outline="",
                           fill=next(palette))
        for _ in plate.grains]
    modes = itertools.cycle(MODES[1:] + MODES[:1])
    frames = itertools.count(1)

    def frame() -> None:
        if next(frames) % frames_per_mode == 0:
            plate.mode = next(modes)
            root.title(f"Chladni Plate {plate.mode}")
        for _ in range(3):
            plate.step()
        for dot, g in zip(dots, plate.grains):
            canvas.moveto(dot, g.x * SIZE - DOT / 2,
                          g.y * SIZE - DOT / 2)
        root.after(step_ms, frame)

    frame()
    root.mainloop()

if __name__ == "__main__":
    show()
