# memoizing.py
from flaky import Database, save_user
from stateless import memoize, run, supply

db = Database(failures=0)
bound = supply(db)(memoize(save_user))
print(run(bound("Morty")))
print(run(bound("Morty")))
print(f"attempts: {db.attempts}")
#: attempt 1: saving Morty
#: Morty saved
#: Morty saved
#: attempts: 1
