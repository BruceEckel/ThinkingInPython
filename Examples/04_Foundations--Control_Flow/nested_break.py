# nested_break.py

grid = [[1, 2], [3, 4]]

def locate(target):
    for row in grid:
        for cell in row:
            if cell == target:
                print(f"found {cell}")
                break
        else:
            continue
        break
    else:
        print("not found")

locate(3)
#: found 3
locate(9)
#: not found
