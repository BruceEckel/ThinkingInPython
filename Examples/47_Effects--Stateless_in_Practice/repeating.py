# repeating.py
from datetime import timedelta
from flaky import Database, save_user
from stateless import repeat, run, supply
from stateless.schedule import recurs, spaced
from stateless.time import Time

three = recurs(3, spaced(timedelta(milliseconds=1)))
repeated = repeat(three)(save_user)
env = supply(Database(failures=0), Time())
print(run(env(repeated)("Morty")))
#: attempt 1
#: attempt 2
#: attempt 3
#: ('Morty saved', 'Morty saved', 'Morty saved')
