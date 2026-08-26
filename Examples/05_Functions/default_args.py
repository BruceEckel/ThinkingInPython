# default_args.py

def connect(host, port=5432, timeout=30):
    return f"{host}:{port} (timeout {timeout}s)"

print(connect("db.example.com"))  # Uses both defaults
#: db.example.com:5432 (timeout 30s)
# Skip to a keyword
print(connect("db.example.com", timeout=5))
#: db.example.com:5432 (timeout 5s)
# Any order by name
print(connect(port=80, host="web.example.com"))
#: web.example.com:80 (timeout 30s)
