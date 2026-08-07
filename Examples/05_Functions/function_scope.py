# function_scope.py

count = 0

def read_only():
    print(count)

def rebinds():
    count = 99  # A local, unrelated to the module-level count
    print(count)

def writes_global():
    global count
    count += 1

read_only()
#: 0
rebinds()
#: 99
writes_global()
print(count)
#: 1
