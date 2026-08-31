# mutating_while_looping.py

scores = [1, 2, 2, 3]
for s in scores:
    if s == 2:
        scores.remove(s)
print(scores)
#: [1, 2, 3]
print([s for s in [1, 2, 2, 3] if s != 2])
#: [1, 3]
ages = {"a": 1, "b": 2}
try:
    for name in ages:
        ages[name + "!"] = 0
except RuntimeError as e:
    print(e)
#: dictionary changed size during iteration
