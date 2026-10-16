> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Metaprogramming

This file is the applied-directly record for the 2026-10-16 sweep and holds no live block.
The chapter carried few AI-writing tells,
so the run mostly trimmed metadiscourse ("the difference matters", "That safety matters"),
bare "real"/"truly" intensifiers,
one §44 parenthetical hedge,
and two restatements that repeated a point made a few lines earlier.
`readability_db.md` binds the keeps: "hook" stays the literal term,
"real" stays wherever the sentence names its contrast,
and the two rhetorical questions stay because each names the problem its section solves.

## Applied directly

- 269, §34 bare intensifier: "names a real event" -> "names a declared event" (matches "legitimate event names" two lines up and "declared event types" below).
- 309, treadmill/§70: the sentence after `greenhouse_demo.py` repeated the `__missing__()` walkthrough; it now ties that walkthrough to the output: "so `LightOn` gets one `Creating` line though `SCHEDULE` names it twice" (checked against `SCHEDULE` and the markers).
- 315, accuracy: "`built()` compares the classes ... so its line states the result: seven classes declared, three built" -> "counts the classes ... against the names in `NAMES`, so its line reports three of the seven built" (`built()` reports two lengths; it compares nothing).
- 322, §39 self-labeling: "That is what a distinct subclass adds. Each event carries its kind as its type" -> "A distinct subclass lets each event carry its kind as its type".
- 439, one concept per paragraph: split the pickling paragraph at "`type()`-built classes fail differently." so the `exec()` case and the `type()` case each get a paragraph.
- 667, §70 metadiscourse: "rather than `func.event`, and the difference matters to the type checker" -> "rather than `func.event` to satisfy the type checker".
- 999, §34 bare intensifier: "The underscore prefix does real work." -> "The underscore prefix keeps each storage key apart from the attribute's name." (the next paragraph supplies the `RecursionError` reason).
- 1451, §44 parenthetical hedge and empty "truly": "(and, arguably, multiple inheritance) for the cases that truly need them" -> ", and arguably multiple inheritance, for the cases that need them".
- 1465, near-verbatim repeat of the bullet six lines up: "A metaclass can give the class object an `__iter__()`, the same method that lets `EnumType` make `for c in Color` work:" -> "The first case gives the class object an `__iter__()`:".
- 1641, §70 metadiscourse: "... runs none of its properties or descriptors. That safety matters when you point this tool at something unfamiliar." -> "..., which makes the tool safe to point at something unfamiliar."

## Considered and declined

- 61-62, "It is a fascinating tool and tempting to use": first-edition voice, a deliberate aside.
- 46, 812, 1334, three rhetorical questions ("What creates these 'class' objects?", "Where does the checker get its rules...?", "Can a metaclass inherit from more than one class...?"): each names the problem the following section answers (recurring keep).
- 195, 872, 881, 1176, 1542, 1694, 1742, "real"/"genuine": each sits against a named or immediate contrast (a label, the false claim, `object`, intended dynamic code, the misleading `TypeError`, `ForwardRef`).
- 1912, "Every class, even an empty one": the "even" carries the claim that bookkeeping dunders appear on every class.
- 1910, "deliberately narrowing the comparison": the next paragraph gives the reason, so the adverb points at it.
- 1324-1328, "Choose the lightest tool that solves your problem.": advice backed by the *Singleton* link, not a generic send-off.
- 1500-1504 against 1558-1567: both say a class decorator cannot give the class object behavior; the second generalizes from `__iter__()` to `__call__()` and closes the section, so it stays.
- 2178-2185, the bare-noun bullet list of dataclass dunders: genuine list content (§59 carve-out).
- 232-234, "With hundreds, the schedule uses few of the classes the comprehension builds": clear as written.
