# break_continue.py

for n in range(10):
    if n == 3:
        continue  # Skip the rest of this iteration
    if n == 6:
        break  # Leave the loop
    print(n, end=" ")
print()  # The newline that end=" " left off
#: 0 1 2 4 5
