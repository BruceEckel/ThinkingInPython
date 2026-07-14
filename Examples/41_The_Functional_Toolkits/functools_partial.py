# functools_partial.py
from functools import partial

shout = partial(print, end="!\n")
shout("hello")
#: hello!
