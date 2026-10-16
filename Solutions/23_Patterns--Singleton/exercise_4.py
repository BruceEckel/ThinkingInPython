# exercise_4.py
import config
from config import settings

#: config body runs
settings = {"theme": "dark"}  # noqa: F811
print(settings)  # [1]
#: {'theme': 'dark'}
print(config.settings)  # [2]
#: {}
