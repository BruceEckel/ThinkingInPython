# livelock.py
def step(name: str, other_wants: bool) -> bool:
    if other_wants:
        print(f"{name}: yields")
        return True  # Still wants the resource
    print(f"{name}: proceeds")
    return False

a_wants = True
b_wants = True
for _ in range(3):
    a_wants, b_wants = step("a", b_wants), step("b", a_wants)
print(f"resolved: {not (a_wants or b_wants)}")
#: a: yields
#: b: yields
#: a: yields
#: b: yields
#: a: yields
#: b: yields
#: resolved: False
