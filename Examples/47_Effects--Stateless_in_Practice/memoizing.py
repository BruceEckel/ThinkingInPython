# memoizing.py
from flaky import Database, save_user
from stateless import memoize, run, supply

db = Database(failures=0)
bound = supply(db)(memoize(save_user))
print(run(bound("Morty")))
#: attempt 1: saving Morty
#: Morty saved
print(run(bound("Morty")))
#: Morty saved
print(f"attempts: {db.attempts}")
#: attempts: 1
