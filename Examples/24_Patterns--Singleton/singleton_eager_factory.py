# singleton_eager_factory.py
from functools import cache
from race_settings import Settings, distinct_objects

@cache
def settings() -> Settings:
    return Settings()

settings()  # Build it before any thread can race for it
print(distinct_objects(settings))
#: 1
