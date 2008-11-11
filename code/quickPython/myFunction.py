# quickPython/myFunction.py
def myFunction(response):
    val = 0
    if response == "yes":
        print("affirmative")
        val = 1
    print("continuing...")
    return val

print(myFunction("no"))
print(myFunction("yes"))