# default_args.py

def connect(host, port=5432, timeout=30):
    return f"{host}:{port} (timeout {timeout}s)"

print(connect("db.example.com"))                 # uses both defaults
print(connect("db.example.com", timeout=5))      # skip to a keyword
print(connect(port=80, host="web.example.com"))  # any order by name
