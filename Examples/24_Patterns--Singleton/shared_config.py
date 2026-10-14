# shared_config.py
import config
from config import settings

#: config body runs
settings["theme"] = "dark"
print(settings)
#: {'theme': 'dark'}
print(config.settings)
#: {'theme': 'dark'}
