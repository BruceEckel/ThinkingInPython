# trap_generators.py
from collections.abc import Generator
from enum import StrEnum

class Mouse(StrEnum):
    APPEARS = "mouse appears"
    RUNS_AWAY = "mouse runs away"
    ENTERS = "mouse enters trap"
    ESCAPES = "mouse escapes"
    TRAPPED = "mouse trapped"
    REMOVED = "mouse removed"

type Machine = Generator[str, Mouse, Machine | None]

def waiting() -> Machine:
    print("Broadcasting cheese smell")
    while True:
        match (yield "Waiting"):
            case Mouse.APPEARS:
                return luring()

def luring() -> Machine:
    print("Presenting Cheese, door open")
    while True:
        match (yield "Luring"):
            case Mouse.RUNS_AWAY:
                return waiting()
            case Mouse.ENTERS:
                return trapping()

def trapping() -> Machine:
    print("Closing door")
    while True:
        match (yield "Trapping"):
            case Mouse.ESCAPES:
                return waiting()
            case Mouse.TRAPPED:
                return holding()

def holding() -> Machine:
    print("Mouse caught")
    print("*ding*")
    while True:
        match (yield "Holding"):
            case Mouse.REMOVED:
                return waiting()
