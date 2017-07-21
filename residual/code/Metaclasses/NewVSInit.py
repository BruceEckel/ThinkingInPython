# Metaclasses/NewVSInit.py
from pprint import pprint

class Tag1: pass
class Tag2: pass
class Tag3:
    def tag3_method(self): pass

class MetaBase(type):
    def __new__(mcl, name, bases, nmspc):
        print('MetaBase.__new__\n')
        return super(MetaBase, mcl).__new__(mcl, name, bases, nmspc)

    def __init__(cls, name, bases, nmspc):
        print('MetaBase.__init__\n')
        super(MetaBase, cls).__init__(name, bases, nmspc)

class MetaNewVSInit(MetaBase):
    def __new__(mcl, name, bases, nmspc):
        # First argument is the metaclass ``MetaNewVSInit``
        print('MetaNewVSInit.__new__')
	for x in (mcl, name, bases, nmspc): pprint(x)
        print('')
        # These all work because the class hasn't been created yet:
        if 'foo' in nmspc: nmspc.pop('foo')
        name += '_x'
        bases += (Tag1,)
        nmspc['baz'] = 42
        return super(MetaNewVSInit, mcl).__new__(mcl, name, bases, nmspc)

    def __init__(cls, name, bases, nmspc):
        # First argument is the class being initialized
        print('MetaNewVSInit.__init__')
	for x in (cls, name, bases, nmspc): pprint(x)
        print('')
        if 'bar' in nmspc: nmspc.pop('bar') # No effect
        name += '_y' # No effect
        bases += (Tag2,) # No effect
        nmspc['pi'] = 3.14159 # No effect
        super(MetaNewVSInit, cls).__init__(name, bases, nmspc)
        # These do work because they operate on the class object:
        cls.__name__ += '_z'
        cls.__bases__ += (Tag3,)
        cls.e = 2.718

class Test(object):
    __metaclass__ = MetaNewVSInit
    def __init__(self):
        print('Test.__init__')
    def foo(self): print('foo still here')
    def bar(self): print('bar still here')

t = Test()
print('class name: ' + Test.__name__)
print('base classes: ', [c.__name__ for c in Test.__bases__])
print([m for m in dir(t) if not m.startswith("__")])
t.bar()
print(t.e)

""" Output:
MetaNewVSInit.__new__
<class '__main__.MetaNewVSInit'>
'Test'
(<type 'object'>,)
{'__init__': <function __init__ at 0x7ecf0>,
 '__metaclass__': <class '__main__.MetaNewVSInit'>,
 '__module__': '__main__',
 'bar': <function bar at 0x7ed70>,
 'foo': <function foo at 0x7ed30>}

MetaBase.__new__

MetaNewVSInit.__init__
<class '__main__.Test_x'>
'Test'
(<type 'object'>,)
{'__init__': <function __init__ at 0x7ecf0>,
 '__metaclass__': <class '__main__.MetaNewVSInit'>,
 '__module__': '__main__',
 'bar': <function bar at 0x7ed70>,
 'baz': 42}

MetaBase.__init__

Test.__init__
class name: Test_x_z
('base classes: ', ['object', 'Tag1', 'Tag3'])
['bar', 'baz', 'e', 'tag3_method']
bar still here
2.718
"""
