# Singleton/SingletonMetaClass.py
class SingletonMetaClass(type):
    def __init__(cls,name,bases,dict):
        super(SingletonMetaClass,cls)\
          .__init__(name,bases,dict)
        original_new = cls.__new__
        def my_new(cls,*args,**kwds):
            if cls.instance == None:
                cls.instance = \
                  original_new(cls,*args,**kwds)
            return cls.instance
        cls.instance = None
        cls.__new__ = staticmethod(my_new)

class bar(object):
    __metaclass__ = SingletonMetaClass
    def __init__(self,val):
        self.val = val
    def __str__(self):
        return `self` + self.val

x=bar('sausage')
y=bar('eggs')
z=bar('spam')
print(x)
print(y)
print(z)
print(x is y is z)