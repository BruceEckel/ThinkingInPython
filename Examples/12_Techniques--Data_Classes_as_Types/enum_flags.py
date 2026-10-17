# enum_flags.py
from enum import Flag, IntFlag, auto

class Perm(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()

rw = Perm.READ | Perm.WRITE
print(repr(rw))
#: <Perm.READ|WRITE: 3>
print(Perm.WRITE in rw, Perm.EXECUTE in rw)
#: True False
print(list(rw))
#: [<Perm.READ: 1>, <Perm.WRITE: 2>]

class Mode(IntFlag):
    R = 4
    W = 2
    X = 1

print(repr(Mode(6)), Mode(6) == 6, Mode.W in Mode(6))
#: <Mode.R|W: 6> True True
print(repr(Mode(9)))
#: <Mode.X|8: 9>
