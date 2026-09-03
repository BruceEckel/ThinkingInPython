# two_games.py
from dataclasses import dataclass, field
from casts import (
    Kitty,
    Weapon,
    kitties_and_puzzles,
    play,
    warriors_and_weapons,
)

class Loud:
    def say(self, line: str) -> None: print(line)

@dataclass
class Script:
    lines: list[str] = field(default_factory=list)
    def say(self, line: str) -> None:
        self.lines.append(line)

kitties_and_puzzles(Loud())
#: Kitty arrives
#: and bats at the puzzle
warriors_and_weapons(Loud())
#: Warrior arrives
#: and battles the nasty weapon
play(Loud(), Kitty(), Weapon())
#: Kitty arrives
#: and bats at the nasty weapon
script = Script()
kitties_and_puzzles(script)
print(len(script.lines), script.lines[1])
#: 2 and bats at the puzzle
