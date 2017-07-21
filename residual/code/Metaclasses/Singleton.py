# Metaclasses/Singleton.py

class Singleton(type):
    instance = None
    def __call__(cls, *args, **kw):
        if not cls.instance:
             cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

class ASingleton(object):
    __metaclass__ = Singleton

a = ASingleton()
b = ASingleton()
assert a is b
print(a.__class__.__name__, b.__class__.__name__)

class BSingleton(object):
    __metaclass__ = Singleton

c = BSingleton()
d = BSingleton()
assert c is d
print(c.__class__.__name__, d.__class__.__name__)
assert c is not a

""" Output:
('ASingleton', 'ASingleton')
('BSingleton', 'BSingleton')
"""
