# aliased_snapshot.py

todo = ["eggs", "milk"]
saved = todo
todo.append("bread")
print(saved, saved is todo)
#: ['eggs', 'milk', 'bread'] True
copied = list(todo)
todo.append("jam")
print(copied)
#: ['eggs', 'milk', 'bread']
