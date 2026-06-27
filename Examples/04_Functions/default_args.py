# default_args.py

def connect(host, port=5432, timeout=30):
    return f"{host}:{port} (timeout {timeout}s)"

print(connect("db.example.com"))                 # Uses both defaults
#: db.example.com:5432 (timeout 30s)
print(connect("db.example.com", timeout=5))      # Skip to a keyword
#: db.example.com:5432 (timeout 5s)
print(connect(port=80, host="web.example.com"))  # Any order by name
#: web.example.com:80 (timeout 30s)
