# dict_sorter.py
from collections import defaultdict
from trash import Bins, Trash

def sort_by_type(pieces: list[Trash]) -> Bins:
    bins: Bins = defaultdict(list)
    for piece in pieces:
        # Piece picks its bin
        bins[type(piece)].append(piece)
    return bins
