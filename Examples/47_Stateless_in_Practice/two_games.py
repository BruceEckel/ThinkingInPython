# two_games.py
from dataclasses import dataclass, field
from casts import (
    Kitty,
    Wasteland,
    Weapon,
    Yarn,
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
#: Kitty crosses the garden path
#: and bats at the puzzle
#: and wins a ball of yarn
warriors_and_weapons(Loud())
#: Warrior crosses the cracked wasteland
#: and battles the nasty weapon
#: and wins a chest of gold
play(Loud(), Kitty(), Weapon(), Wasteland(), Yarn())
#: Kitty crosses the cracked wasteland
#: and bats at the nasty weapon
#: and wins a ball of yarn
script = Script()
kitties_and_puzzles(script)
print(len(script.lines), script.lines[1])
#: 3 and bats at the puzzle
