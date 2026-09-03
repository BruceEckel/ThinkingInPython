# finally_swallows.py

def risky():
    try:
        raise ValueError("boom")
    finally:
        return "swallowed"

print(risky())
#: swallowed
