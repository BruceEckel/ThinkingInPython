# exercise_5.py
def run(command):
    match command.split():
        case ["go", direction, distance]:
            return f"moving {direction} for {distance}"
        case ["go", direction]:
            return f"moving {direction}"
        case ["quit"]:
            return "goodbye"
        case _:
            return "unknown command"

print(run("go north 3"))
#: moving north for 3
print(run("go north"))
#: moving north
