# list_as_deque.py

lst = [1, 2, 3]
lst.append(4)  # Add at the end
lst.insert(0, 0)  # Add at the start
print(lst)
#: [0, 1, 2, 3, 4]
print(lst.pop(0))  # Remove from the start
#: 0
print(lst.pop())  # Remove from the end
#: 4
print(lst)
#: [1, 2, 3]
