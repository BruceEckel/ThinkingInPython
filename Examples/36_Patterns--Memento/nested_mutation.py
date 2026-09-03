# nested_mutation.py
import copy

todo = [["eggs", "milk"], ["bread"]]
shallow = list(todo)
todo[0].append("cheese")
print(shallow)
#: [['eggs', 'milk', 'cheese'], ['bread']]

deep = copy.deepcopy(todo)
todo[0].append("jam")
print(todo)
#: [['eggs', 'milk', 'cheese', 'jam'], ['bread']]
print(deep)
#: [['eggs', 'milk', 'cheese'], ['bread']]
