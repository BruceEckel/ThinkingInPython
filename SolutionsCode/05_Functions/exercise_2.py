# exercise_2.py
MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    if key in data:
        return data[key]
    if default is MISSING:
        raise KeyError(key)
    return default

prefs = {"volume": 3, "mute": None, "volume2": None}
print(get(prefs, "volume2"))
#: None
