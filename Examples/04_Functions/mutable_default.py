# mutable_default.py

def bad_append(item, target=[]):  # The same list every call
    target.append(item)
    return target

print(bad_append(1))  # [1]
print(bad_append(2))  # [1, 2]: Surprise, the default kept the 1

def good_append(item, target=None):
    if target is None:
        target = []               # A fresh list each call
    target.append(item)
    return target

print(good_append(1))  # [1]
print(good_append(2))  # [2]
