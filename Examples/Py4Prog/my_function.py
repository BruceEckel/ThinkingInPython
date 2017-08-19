# Py4Prog/my_function.py
def my_function(response):
    val = 0
    if response == "yes":
        print("affirmative")
        val = 1
    print("continuing...")
    return val

print(my_function("no"))
print(my_function("yes"))
