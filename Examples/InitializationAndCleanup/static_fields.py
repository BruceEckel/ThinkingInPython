# InitializationAndCleanup/static_fields.py
class Foo(object):
        x = "a"

Foo.x
f = Foo()
f.x
f2 = Foo()
f2.x
f2.x = 'b'
f.x
Foo.x = 'c'
f.x
f2.x
Foo.x = 'd'
f2.x
f.x
f3 = Foo()
f3.x
Foo.x = 'e'
f3.x
f2.x
