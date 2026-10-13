# mapping_proxy.py
from types import MappingProxyType

settings = {"debug": False, "level": 3}
config = MappingProxyType(settings)
print(config["level"])
#: 3
settings["level"] = 4
print(config["level"])
#: 4
try:
    config["level"] = 9  # type: ignore
except TypeError as e:
    print(e)
#: 'mappingproxy' object does not support item assignment
