# chain_map.py
from collections import ChainMap

defaults = {"theme": "light", "zoom": 100}
user = {"zoom": 125}
prefs = ChainMap(user, defaults)
print(prefs["zoom"], prefs["theme"])
#: 125 light
user["theme"] = "dark"
print(prefs["theme"])  # It reads the live dicts
#: dark
prefs["zoom"] = 150  # Writes go to the first dict
print(user["zoom"], defaults["zoom"])
#: 150 100
