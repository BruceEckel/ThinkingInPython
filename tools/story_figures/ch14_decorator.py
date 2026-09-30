"""Chapter 14, The Decorator Pattern: one order as nested layers.

The figure sits after the section's claim that a topping wraps a pizza
and is itself a pizza, so a topping can wrap another topping. It
replaced a UML class diagram on 2026-09-29. The class diagram showed
the types and their relations but not the nesting, and the nesting is
the pattern: `Feta(Olives(Margherita()))` is drawn as three boxes, each
inside the next, with `Feta` outermost. Reading `order.cost` travels
inward one layer at a time, each topping reading `self.pizza.cost`,
until `Margherita` answers with its own `cost`. The total then travels
back out, and each layer adds its `add_cost` on the way, so the reader
sees 8.00 become 8.75 and then 10.00. The caller reads one `cost`
from the outermost object and cannot tell how many layers lie inside.

Names, prices, and the printed line come from `pizza_decorator.py`:
`Margherita.cost` 8.00, `Olives.add_cost` 0.75, `Feta.add_cost` 1.25,
`Topping.cost` returning `self.pizza.cost + self.add_cost`, and the
first `#:` line, `Margherita + Olives + Feta: $10.00`.
"""

from tools.story_figures import (INK, MUTED, RED, arrow, markers, rect,
                                 region, svg, text)

STEM = "decorator_pattern"
W, H = 730, 390
CALL_Y, BACK_Y = 178, 240  # The inward call row and the return row
BOX_Y, BOX_H, BOX_W = 140, 115, 125  # Each layer's cost box
RIGHT = 715  # Feta's right edge; each inner layer sits 15 inside it
TITLE = ("Feta(Olives(Margherita())) as three nested layers: reading "
         "order.cost passes inward to Margherita's 8.00, and each topping "
         "adds its add_cost on the way back out, giving 8.75 and then "
         "10.00")
CALLER_X, FETA_X, OLIVES_X, CORE_X = 10, 135, 305, 485
CORE_Y = 110


def layer(name: str, add_cost: str, total: str, x: float, y: float,
          depth: int) -> str:
    """One topping: its region, name, `add_cost`, and `cost` box."""
    inset = 15 * depth
    bx = x + 12
    return (region(x, y, RIGHT - inset - x, 330 - inset - y, stroke=INK)
            + text(x + 12, y + 24, name, 13, bold=True)
            + text(x + 12, y + 42, add_cost, 11, MUTED)
            + rect(bx, BOX_Y, BOX_W, BOX_H, stroke=INK, width=1.1)
            + text(bx + 10, BOX_Y + 18, "cost", 10.5, MUTED)
            + text(bx + 10, CALL_Y + 4, "self.pizza.cost", 11)
            + text(bx + 10, CALL_Y + 24, "+ add_cost", 11, MUTED)
            + text(bx + 10, BACK_Y + 5, total, 12, RED))


def render() -> str:
    b = text(20, 28, "order = Feta(Olives(Margherita()))", 13)

    # The caller holds only the outermost object.
    b += rect(CALLER_X, BOX_Y, 90, BOX_H, stroke=INK, width=1.1)
    b += text(CALLER_X + 10, BOX_Y + 18, "caller", 10.5, MUTED)
    b += text(CALLER_X + 10, CALL_Y + 4, "order.cost", 11)
    b += text(CALLER_X + 10, BACK_Y + 5, "10.00", 12, RED, bold=True)

    b += layer("Feta", "add_cost = 1.25", "8.75 + 1.25", FETA_X, 50, 0)
    b += layer("Olives", "add_cost = 0.75", "8.00 + 0.75", OLIVES_X, 80,
               1)
    b += rect(CORE_X, CORE_Y, RIGHT - 30 - CORE_X, 300 - CORE_Y,
              stroke=INK, width=1.3)
    b += text(CORE_X + 12, CORE_Y + 24, "Margherita", 13, bold=True)
    b += text(CORE_X + 12, CALL_Y + 4, "cost = 8.00", 12)
    b += text(CORE_X + 12, 280, 'description = "Margherita"', 10.5,
              MUTED)

    # Inward, one layer at a time; then the total comes back out.
    lefts = [CALLER_X + 90, FETA_X + 12 + BOX_W, OLIVES_X + 12 + BOX_W]
    rights = [FETA_X + 12, OLIVES_X + 12, CORE_X]
    for a, z in zip(lefts, rights):
        b += arrow((a, CALL_Y), (z, CALL_Y), INK, "dp-ink")
        b += arrow((z, BACK_Y), (a, BACK_Y), MUTED, "dp-back",
                   kind="open", dash=True)

    b += text(20, 362, "prints", 11, MUTED)
    b += text(76, 362, "Margherita + Olives + Feta: $10.00", 12.5)
    b += text(20, 382, "description comes back the same way, each "
              'layer adding " + " and its name', 10.5, MUTED)

    defs = markers(**{"dp-ink": ("filled", INK),
                      "dp-back": ("open", MUTED)})
    return svg(W, H, TITLE, defs, b)
