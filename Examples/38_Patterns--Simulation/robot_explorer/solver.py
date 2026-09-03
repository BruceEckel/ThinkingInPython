# robot_explorer/solver.py
from collections import deque
from typing import Final
from game import GameBuilder
from items import Edge, EndGame, Teleport, Urge, Wall
from world import Room

MOVES: Final[dict[Urge, str]] = {
    Urge.NORTH: "n", Urge.SOUTH: "s",
    Urge.EAST: "e", Urge.WEST: "w"}

def landing(room: Room, urge: Urge) -> Room | None:
    # Where a door leads, or None when it is blocked
    beyond = room.doors.open(urge)
    if isinstance(beyond.occupant, Wall | Edge):
        return None
    if isinstance(beyond.occupant, Teleport):
        return beyond.occupant.target_room
    return beyond

def solve(game: GameBuilder) -> str:
    start = game.robot.room
    queue: deque[tuple[Room, str]] = deque([(start, "")])
    seen: set[Room] = {start}
    while queue:
        room, path = queue.popleft()
        if isinstance(room.occupant, EndGame):
            return path
        for urge, char in MOVES.items():
            beyond = landing(room, urge)
            if beyond is None or beyond in seen:
                continue
            seen.add(beyond)
            queue.append((beyond, path + char))
    raise ValueError("No path to the EndGame room")
