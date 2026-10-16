# singleton_cached_race.py
from functools import cache
from race_settings import Settings, distinct_objects

@cache
def settings() -> Settings:
    return Settings()

print(distinct_objects(settings) > 1)
#: True
