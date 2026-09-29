"""Chapter 24, Singleton: four frames of one module shared by its importers.

The chapter's answer to *Singleton* is the module: the import system runs
a module's body once, files the module object in `sys.modules`, and hands
that same object to every later import. A class diagram shows none of
this, since the singleton is a lookup the import system performs, not a
rule a class enforces. So the figure follows the chapter's first section
in time, one layout per frame: the importing file on the left, the
`sys.modules` entry in the middle, the module object on the right.

1. `import config` finds no entry, so `config.py` runs (printing
   `config body runs`) and is filed under `'config'`.
2. `import config as again` finds the entry; the body does not run, and
   both names reach the same module (`True True`).
3. `shared_config.py` mutates the one `settings` dict through its own
   name (`{'theme': 'dark'}`).
4. Rebinding that name, `settings = {}`, points it at a new dict and
   leaves `config.settings` as it was: the prose's "Mutate through any
   name. Rebind only through the module." No listing contains this step,
   so its new dict is dashed.

Frames 1 and 2 come from `module_singleton.py`, frame 3 from
`shared_config.py`, and all three from `config.py`; frame 4 continues
frame 3 with the rebinding the prose describes after `shared_config.py`.
"""

from tools.story_figures import (BOX, INK, MUTED, RED, arrow, line, markers,
                                 rect, region, svg, text)

STEM = "singleton_story"
W = 730
FH = 160  # One frame's height
IX, IW = 140, 210  # The importing file
SLX, SLW, SLH = 268, 72, 24  # The names it binds
SLOT_Y = (84, 112)
MX, MW = 380, 100  # sys.modules
KX, KY, KW, KH = 390, 44, 80, 24  # Its 'config' entry
OX, OW = 520, 195  # The config module object
DX, DY, DW, DH = 532, 102, 171, 28  # Its settings dict
TOP = 76  # Height of the target the name arrows point at
TITLE = ("Four steps of a module singleton: the first import runs "
         "config.py and files it in sys.modules, a second import gets the "
         "same module, a mutation through one name reaches every importer, "
         "and rebinding the name leaves config.settings unchanged")


def frame(i: int, y0: float, name: str, lines: tuple[str, ...],
          importer: str, code: tuple[tuple[str, str], ...],
          new: bool = False) -> str:
    """The layout every frame shares; `new` marks the entry just filed."""
    out = ""
    if i:
        out += line((16, y0 - 4), (W - 16, y0 - 4))
    out += text(22, y0 + 44, str(i + 1), 30, RED, bold=True)
    out += text(22, y0 + 66, name, 13, bold=True)
    for j, s in enumerate(lines):
        out += text(22, y0 + 86 + j * 15, s, 10.5, MUTED)

    out += region(IX, y0 + 14, IW, FH - 30, stroke=INK)
    out += text(IX + 10, y0 + 32, importer, 11, bold=True)
    for j, (s, fill) in enumerate(code):
        out += text(IX + 10, y0 + 50 + j * 16, s, 10.5, fill)

    color = RED if new else INK
    out += region(MX, y0 + 22, MW, 54, stroke=BOX)
    out += text(MX + 8, y0 + 37, "sys.modules", 11, MUTED)
    out += rect(KX, y0 + KY, KW, KH, stroke=color, width=1.1, rx=3)
    out += text(KX + KW / 2, y0 + KY + 16, "'config'", 10.5, color, "middle")

    out += region(OX, y0 + 14, OW, FH - 30, stroke=color)
    # The arrows at the module point at its top part, an unstroked rect;
    # the outline is a region so the settings dict can take an arrow too.
    out += rect(OX, y0 + 14, OW, TOP, stroke="none")
    out += text(OX + 12, y0 + 34, "config", 13, color, bold=True)
    out += text(OX + OW - 10, y0 + 34, "module object", 10, MUTED, "end")
    out += arrow((KX + KW, y0 + KY + KH / 2), (OX, y0 + KY + KH / 2), color,
                 "ss-red" if new else "ss-ink")
    return out


def slot(y0: float, k: int, s: str, fill: str = INK) -> str:
    y = y0 + SLOT_Y[k]
    return (rect(SLX, y, SLW, SLH, stroke=fill, width=1.1, rx=3)
            + text(SLX + SLW / 2, y + 16, s, 10.5, fill, "middle"))


def slot_mid(y0: float, k: int) -> tuple[float, float]:
    return (SLX + SLW, y0 + SLOT_Y[k] + SLH / 2)


def settings(y0: float, value: str, fill: str = INK,
             label: str = "settings", label_fill: str = MUTED) -> str:
    return (text(DX, y0 + DY - 6, label, 10, label_fill)
            + rect(DX, y0 + DY, DW, DH, stroke=INK, width=1.1, rx=3)
            + text(DX + DW / 2, y0 + DY + 18, value, 10.5, fill, "middle"))


def prints(y0: float, outputs: tuple[str, ...]) -> str:
    out = text(IX + 10, y0 + 92, "prints", 10, MUTED)
    for j, s in enumerate(outputs):
        out += text(IX + 10, y0 + 108 + j * 16, s, 10.5, RED)
    return out


def render() -> str:
    y = [10 + i * FH for i in range(4)]
    b = ""

    y0 = y[0]
    b += frame(0, y0, "import", ("no entry yet,", "so config.py",
                                 "runs and is filed"),
               "module_singleton.py", (("import config", RED),), new=True)
    b += prints(y0, ("config body runs",))
    b += text(OX + 12, y0 + 64, "body runs once", 10.5, RED)
    b += settings(y0, "{}")
    b += slot(y0, 0, "config", RED)
    b += arrow(slot_mid(y0, 0), (OX, y0 + 84), RED, "ss-red")

    y0 = y[1]
    b += frame(1, y0, "reuse", ("the entry is", "found, so both", "names get the",
                                "same module"),
               "module_singleton.py",
               (("import config", INK), ("import config as again", RED)))
    b += prints(y0, ("True True",))
    b += text(OX + 12, y0 + 64, "body not run again", 10.5, MUTED)
    b += settings(y0, "{}")
    b += slot(y0, 0, "config")
    b += slot(y0, 1, "again", RED)
    b += arrow(slot_mid(y0, 0), (OX, y0 + 74), INK, "ss-ink")
    b += arrow(slot_mid(y0, 1), (OX, y0 + 88), RED, "ss-red")

    y0 = y[2]
    b += frame(2, y0, "mutate", ("a change through", "your own name", "reaches every",
                                 "importer"),
               "shared_config.py",
               (("from config import settings", INK),
                ('settings["theme"] = "dark"', RED)))
    b += prints(y0, ("config body runs", "{'theme': 'dark'}"))
    b += settings(y0, "{'theme': 'dark'}", RED)
    b += slot(y0, 1, "settings")
    b += arrow(slot_mid(y0, 1), (DX, y0 + DY + DH / 2), INK, "ss-ink")

    y0 = y[3]
    b += frame(3, y0, "rebind", ("a new binding", "moves only your", "name; the module",
                                 "keeps its dict"),
               "shared_config.py",
               (('settings["theme"] = "dark"', MUTED), ("settings = {}", RED)))
    b += settings(y0, "{'theme': 'dark'}", label="config.settings: unchanged",
                  label_fill=RED)
    b += rect(MX + 10, y0 + 104, 80, 26, stroke=RED, dash=True, rx=3)
    b += text(MX + 50, y0 + 121, "{}", 10.5, RED, "middle")
    b += slot(y0, 1, "settings", RED)
    b += arrow(slot_mid(y0, 1), (MX + 10, y0 + 117), RED, "ss-red")

    defs = markers(**{"ss-ink": ("filled", INK), "ss-red": ("filled", RED)})
    return svg(W, 10 + 4 * FH, TITLE, defs, b)
