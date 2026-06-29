# break_continue.py

for n in range(10):
    if n == 3:
        continue   # Skip the rest of this iteration
    if n == 6:
        break      # Leave the loop entirely
    print(n, end=" ")
#: 0 1 2 4 5
