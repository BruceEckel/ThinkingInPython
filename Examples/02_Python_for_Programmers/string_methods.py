# string_methods.py

s = "  Hello, World  "
print(s.strip())              # 'Hello, World'
print(s.strip().lower())      # 'hello, world'
print("World" in s)           # True
print("a,b,c".split(","))     # ['a', 'b', 'c']
print("-".join(["2024", "06", "15"]))  # '2024-06-15'
print("ababab".replace("a", "X"))      # 'XbXbXb'
print(s.strip()[0:5])         # 'Hello': slicing
