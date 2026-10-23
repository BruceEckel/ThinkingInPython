# function_scope.py

count = 0

def read_only():
    print(count)

def reads_later():
    print(limit)

def rebinds():
    # A local, unrelated to the module-level count
    count = 99
    print(count)

def writes_global():
    global count
    count += 1

limit = 10
read_only()
#: 0
reads_later()
#: 10
rebinds()
#: 99
print(count)
#: 0
writes_global()
print(count)
#: 1
