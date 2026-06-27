# functions.py

def greet(name):
    return f"Hello, {name}"

def banner(text, width=20):  # width has a default value
    line = "*" * width
    return f"{line}\n{text}\n{line}"

print(greet("Alice"))
#: Hello, Alice
print(banner("Hi", width=4))  # pass an argument by name
#: ****
#: Hi
#: ****
