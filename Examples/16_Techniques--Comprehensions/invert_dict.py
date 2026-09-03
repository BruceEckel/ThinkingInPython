# invert_dict.py
seat_of = {"Arthur": 1, "Galahad": 2, "Robin": 1}

name_at = {seat: name for name, seat in seat_of.items()}
print(name_at)
#: {1: 'Robin', 2: 'Galahad'}
