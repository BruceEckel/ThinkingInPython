# rtti_sorter.py
from collections import defaultdict
from trash import (Aluminum, Bins, Cardboard, Glass,
                   Paper, Trash)

def sort_by_match(pieces: list[Trash]) -> Bins:
    bins: Bins = defaultdict(list)
    for piece in pieces:
        match piece:
            case Aluminum():
                bins[Aluminum].append(piece)
            case Paper():
                bins[Paper].append(piece)
            case Glass():
                bins[Glass].append(piece)
            case Cardboard():
                bins[Cardboard].append(piece)
    return bins
