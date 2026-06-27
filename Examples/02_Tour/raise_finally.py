# raise_finally.py
def check_age(age):
    if age < 0:
        raise ValueError(f"age cannot be negative: {age}")
    return age

try:
    check_age(-1)
except ValueError as error:
    print("Rejected:", error)
finally:
    print("Validation done")
#: Rejected: age cannot be negative: -1
#: Validation done
