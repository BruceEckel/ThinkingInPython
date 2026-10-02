# exercise_2.py
from exceptions import expect

MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    try:
        return data[key]
    except KeyError:
        if default is MISSING:
            raise
        return default

prefs = {"volume": 3, "mute": None}
expect(KeyError, get, prefs, "theme")
#: [KeyError] 'theme'
print(get(prefs, "theme", None))
#: None
