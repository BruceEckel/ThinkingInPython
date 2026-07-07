# exercise_4.py
from dataclasses import dataclass
from enum import Enum
from functools import cache

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class Kind(Enum):
    PAWN = "P"
    ROOK = "R"
    KNIGHT = "N"
    BISHOP = "B"
    QUEEN = "Q"
    KING = "K"

@dataclass(frozen=True)
class Piece:
    color: Color
    kind: Kind

@cache
def piece(color: Color, kind: Kind) -> Piece:
    return Piece(color, kind)

type Square = tuple[str, int]

def starting_position() -> dict[Square, Piece]:
    board: dict[Square, Piece] = {}
    back_rank = [Kind.ROOK, Kind.KNIGHT, Kind.BISHOP, Kind.QUEEN,
                 Kind.KING, Kind.BISHOP, Kind.KNIGHT, Kind.ROOK]
    for file, kind in zip("abcdefgh", back_rank):
        board[(file, 1)] = piece(Color.WHITE, kind)
        board[(file, 8)] = piece(Color.BLACK, kind)
    for file in "abcdefgh":
        board[(file, 2)] = piece(Color.WHITE, Kind.PAWN)
        board[(file, 7)] = piece(Color.BLACK, Kind.PAWN)
    return board

def move(
    board: dict[Square, Piece], src: Square, dst: Square
) -> None:
    board[dst] = board.pop(src)  # Overwrites dst's old occupant

def promote(
    board: dict[Square, Piece], square: Square, kind: Kind
) -> None:
    current = board[square]
    board[square] = piece(current.color, kind)  # A shared Piece

board = starting_position()
print(len(board), len({id(p) for p in board.values()}))
#: 32 12
move(board, ("e", 2), ("e", 4))
print(("e", 2) in board, board[("e", 4)].kind)
#: False Kind.PAWN
promote(board, ("e", 4), Kind.QUEEN)
print(board[("e", 4)])
#: Piece(color=<Color.WHITE: 'white'>, kind=<Kind.QUEEN: 'Q'>)
