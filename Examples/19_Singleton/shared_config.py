# shared_config.py
# A module is imported once and cached in sys.modules, so its globals
# are shared. The settings you import is config's own dict, the same
# object everywhere it is imported.
import config
from config import settings

settings["theme"] = "dark"  # Write through the imported name.
print(config.settings)  # {'theme': 'dark'}: the same dict.
print(config.settings is settings)  # True
