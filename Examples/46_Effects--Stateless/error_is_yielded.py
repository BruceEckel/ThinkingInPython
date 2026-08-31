# error_is_yielded.py
from scores import score

effect = score("Carol")
print(repr(next(effect)))
#: KeyError('Carol')
