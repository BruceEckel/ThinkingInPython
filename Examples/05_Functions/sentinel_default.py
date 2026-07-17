# sentinel_default.py

MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    if key in data:
        return data[key]
    if default is MISSING:
        return MISSING  # Normally raise exception here
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
