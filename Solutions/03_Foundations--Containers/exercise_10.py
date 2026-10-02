# exercise_10.py

pairs = [("host", "localhost"), ("port", 8080)]
config = frozendict(pairs)
print(config)
#: frozendict({'host': 'localhost', 'port': 8080})
connections = {config: "primary"}
same = frozendict(port=8080, host="localhost")
print(connections[same])
#: primary
try:
    config["port"] = 9090  # type: ignore
except TypeError as e:
    print(e)
#: 'frozendict' object does not support item assignment

nested = frozendict(tags=["a", "b"])
try:
    hash(nested)
except TypeError as e:
    print(e)
#: unhashable type: 'list'
