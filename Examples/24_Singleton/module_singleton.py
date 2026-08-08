# module_singleton.py
import config
import config as again

print(config is again, config.settings is again.settings)
#: config body runs
#: True True
