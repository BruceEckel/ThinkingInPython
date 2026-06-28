# move.py
# `|` lists alternatives in one case. A bare name captures the value.

def step(command: str) -> str:
    match command:
        case "up" | "u":
            return "y -= 1"
        case "down" | "d":
            return "y += 1"
        case other:
            return f"unknown command: {other}"

print(step("up"))
print(step("d"))
print(step("jump"))
