# spent.py
from flaky import Database, save_user
from stateless import run, supply

effect = supply(Database(failures=0))(save_user)("Morty")
print(repr(run(effect)))
#: attempt 1: saving Morty
#: 'Morty saved'
print(repr(run(effect)))
#: None
