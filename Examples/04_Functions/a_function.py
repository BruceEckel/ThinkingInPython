# a_function.py

def a_function(response):
    val = 0
    if response == "yes":
        print("affirmative")
        val = 1
    print("continuing...")
    return val

print(a_function("no"))
print(a_function("yes"))
