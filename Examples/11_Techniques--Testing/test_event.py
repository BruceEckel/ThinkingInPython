# test_event.py
from datetime import datetime
import event
import time_machine

@time_machine.travel("2030-06-15", tick=False)
def test_current_year_is_frozen() -> None:
    assert event.current_year() == 2030
    # tick=False: successive readings are identical
    assert datetime.now() == datetime.now()
