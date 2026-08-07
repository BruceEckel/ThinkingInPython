# frozendict_demo.py

prefs = frozendict(theme="dark", zoom=125)
print(prefs["zoom"])
#: 125
# Equal contents compare equal; entry order is ignored:
print(prefs == frozendict(zoom=125, theme="dark"))
#: True
cache = {prefs: "rendered"}  # Usable as a dict key
print(cache[frozendict(zoom=125, theme="dark")])
#: rendered
try:
    prefs["zoom"] = 150  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
