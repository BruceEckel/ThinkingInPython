# exercise_3.py
scores = [("Bob", 85), ("Amy", 92), ("Cid", 85), ("Amy", 70)]
by_score_then_name = sorted(scores, key=lambda t: (t[1], t[0]))
print(by_score_then_name)
#: [('Amy', 70), ('Bob', 85), ('Cid', 85), ('Amy', 92)]
