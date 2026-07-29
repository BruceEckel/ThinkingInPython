# error_is_yielded.py
from scores import score

effect = score("carol")
print(repr(next(effect)))
#: KeyError('carol')
