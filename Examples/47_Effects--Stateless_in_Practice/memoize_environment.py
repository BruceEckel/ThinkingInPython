# memoize_environment.py
from flaky import Database, save_user
from stateless import memoize, run, supply

db1 = Database(failures=0)
db2 = Database(failures=0)
m = memoize(save_user)
print(run(supply(db1)(m)("Morty")))
#: attempt 1: saving Morty
#: Morty saved
print(run(supply(db2)(m)("Morty")))
#: Morty saved
print(db1.attempts, db2.attempts)
#: 1 0
