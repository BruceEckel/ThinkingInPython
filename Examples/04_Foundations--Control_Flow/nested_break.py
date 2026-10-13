# nested_break.py

grid = [[1, 2], [3, 4]]

def locate(target):
    for row in grid:
        for cell in row:
            if cell == target:
                print(f"found {cell}")
                break  # [1]
        else:  # [2]
            continue
        break  # [3]
    else:  # [4]
        print("not found")
    print(f"searched for {target}")  # [5]

locate(3)
#: found 3
#: searched for 3
locate(9)
#: not found
#: searched for 9
