# module_singleton.py
import config
import config as again

#: config body runs
print(config is again, config.settings is again.settings)
#: True True
