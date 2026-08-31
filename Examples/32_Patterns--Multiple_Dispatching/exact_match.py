# exact_match.py
from paper_scissors_rock_table import OUTCOME, Paper, Rock

class Origami(Paper):
    pass

print(OUTCOME[Paper, Rock])
#: win
try:
    Origami().compete(Rock())
except KeyError as e:
    missing = e.args[0]  # The tuple key that was not found
    print(type(e).__name__, [c.__name__ for c in missing])
#: KeyError ['Origami', 'Rock']
