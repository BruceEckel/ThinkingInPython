# module_singleton.py
import config  # [1]
import config as again  # [2]

#: config body runs
print(config is again, config.settings is again.settings)
#: True True
