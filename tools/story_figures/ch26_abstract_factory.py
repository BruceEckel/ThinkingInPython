"""Chapter 27, Factory: the Abstract Factories section's two runs.

The section's figure, placed before `abstract_factory_abc.py`, replaced
a UML class diagram on 2026-09-29. The class diagram showed which class
inherits from which; it did not show what the section argues, that one
choice of factory picks both halves of a matched pair while the game
code stays the same. So the figure shows `GameEnvironment`'s code once,
outlined in red as the part that does not change between runs, and
under it the listing's two runs side by side: `g1` given
`KittiesAndPuzzles()`, `g2` given `WarriorsAndWeapons()`, each
factory's two methods pointing at the product they return, and the
line each `play()` prints. A dashed box at the bottom is the mix no
listing produces, a `Kitty` meeting a `Weapon`: neither factory builds
that pair. Names, the `GameEnvironment` code, and the printed lines come
from `abstract_factory_abc.py` and its `#:` markers, which
`abstract_factory_protocol.py` repeats.
"""

from tools.story_figures import (BOX, INK, MUTED, RED, arrow, cross, line,
                                 markers, rect, region, svg, text)

STEM = "abstract_factory"
W = 720
CW = 330  # One run's column
COLS = (20, 370)
FX, FW, FH = 15, 175, 100  # The factory box, relative to its column
PX, PW, PH = 235, 80, 28  # The product boxes
TOP = 185  # The runs' regions
ROW = (274, 306)  # Baselines of the two method rows
TITLE = ("The same GameEnvironment code run twice: given "
         "KittiesAndPuzzles it builds a Kitty and a Puzzle and prints "
         "Kitty encounters a Puzzle; given WarriorsAndWeapons it builds a "
         "Warrior and a Weapon and prints Warrior battles a Weapon; "
         "neither factory builds a Kitty with a Weapon")

CODE = (
    "def __init__(self, factory: GameElementFactory) -> None:",
    "    self.character = factory.make_character()",
    "    self.obstacle = factory.make_obstacle()",
    "def play(self) -> None:",
    "    self.character.interact_with(self.obstacle)",
)


def run(x: float, setup: str, factory: str, character: str,
        obstacle: str, call: str, printed: str) -> str:
    """One run's column: its setup line, factory, products, and output."""
    b = region(x, TOP, CW, 215, stroke=INK)
    b += text(x + 15, TOP + 22, setup, 11)
    fy = TOP + 38
    b += rect(x + FX, fy, FW, FH, stroke=INK, width=1.1)
    b += text(x + FX + FW / 2, fy + 21, factory, 12, INK, "middle",
              bold=True)
    b += line((x + FX, fy + 31), (x + FX + FW, fy + 31), BOX)
    for base, method, product in zip(ROW, ("make_character()",
                                           "make_obstacle()"),
                                     (character, obstacle)):
        b += text(x + FX + 12, base, method, 11, MUTED)
        py = base - 4 - PH / 2
        b += rect(x + PX, py, PW, PH, stroke=INK, width=1.1)
        b += text(x + PX + PW / 2, py + 19, product, 12, INK, "middle")
        b += arrow((x + FX + FW, base - 4), (x + PX, base - 4), INK,
                   "af-ink")
    b += text(x + 15, TOP + 168, call, 11, MUTED)
    b += text(x + 15, TOP + 193, printed, 12.5, INK, bold=True)
    return b


def render() -> str:
    b = region(20, 20, 680, 140, stroke=RED)
    b += text(40, 46, "GameEnvironment", 13, bold=True)
    b += text(40 + 16 * 7.8, 46, "the same code in both runs", 11, RED)
    for k, s in enumerate(CODE):
        # SVG collapses leading spaces, so indent by position instead;
        # JetBrains Mono advances 0.6 em per character.
        pad = len(s) - len(s.lstrip())
        b += text(40 + pad * 11.5 * 0.6, 74 + 17 * k, s.lstrip(), 11.5)
    b += text(530, 91, "names no Kitty,", 11, RED)
    b += text(530, 107, "Puzzle, Warrior,", 11, RED)
    b += text(530, 123, "or Weapon", 11, RED)

    b += run(COLS[0], "g1 = GameEnvironment(KittiesAndPuzzles())",
             "KittiesAndPuzzles", "Kitty", "Puzzle", "g1.play() prints",
             "Kitty encounters a Puzzle")
    b += run(COLS[1], "g2 = GameEnvironment(WarriorsAndWeapons())",
             "WarriorsAndWeapons", "Warrior", "Weapon",
             "g2.play() prints", "Warrior battles a Weapon")

    # The pair neither factory builds.
    bx, bw = 250, 220
    b += rect(bx, 425, bw, 30, stroke=BOX, dash=True)
    b += text(bx + bw / 2, 445, "Kitty encounters a Weapon", 12, MUTED,
              "middle")
    b += cross(bx - 18, 440)
    b += text(W / 2, 478, "neither factory builds this pair", 11, RED,
              "middle")

    defs = markers(**{"af-ink": ("filled", INK)})
    return svg(W, 492, TITLE, defs, b)
