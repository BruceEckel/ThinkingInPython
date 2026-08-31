# sentinel_default.py

MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    try:
        return data[key]
    except KeyError:
        if default is MISSING:
            return MISSING  # Normally re-raises here
        return default

prefs = {"volume": 3, "mute": None}
print(get(prefs, "volume"))
#: 3
print(get(prefs, "mute"))  # None is a real stored value
#: None
print(get(prefs, "theme"))
#: MISSING
print(get(prefs, "theme", "dark"))
#: dark
