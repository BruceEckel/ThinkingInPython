# shared_config.py
# A module's globals are shared.
from config import settings

settings["theme"] = "dark"
print(settings)
#: {'theme': 'dark'}
