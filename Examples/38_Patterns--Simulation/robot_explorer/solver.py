# robot_explorer/solver.py
from collections import deque
from game import GameBuilder, Moves
from items import EndGame, Teleport, Urge, Wall
from world import Room

def landing(room: Room, urge: Urge) -> Room | None:
    # Where a door leads, or None when it is blocked
    beyond = room.doors.open(urge)
    if isinstance(beyond.occupant, Wall):
        return None
    if isinstance(beyond.occupant, Teleport):
        return beyond.occupant.target_room
    return beyond

def solve(game: GameBuilder) -> Moves:
    start = game.robot.room
    queue: deque[tuple[Room, Moves]] = deque([(start, "")])
    seen: set[Room] = {start}
    while queue:
        room, path = queue.popleft()
        if isinstance(room.occupant, EndGame):
            return path
        for urge in Urge:
            beyond = landing(room, urge)
            if beyond is None or beyond in seen:
                continue
            seen.add(beyond)
            queue.append((beyond, path + urge.value))
    raise ValueError("No path to the EndGame room")
