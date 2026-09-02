# exercise_2.py
MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    try:
        return data[key]
    except KeyError:
        if default is MISSING:
            return MISSING  # Normally re-raises here
        return default

prefs = {"volume": 3, "mute": None, "volume2": None}
print(get(prefs, "volume2"))
#: None
