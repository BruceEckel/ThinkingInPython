.. index::
   Metaclasses
   class decorators

********************************************************************************
Metaclasses
********************************************************************************

Introduction.

Example of self-registration of subclasses.

Version 1: metaclass approach.

(following is cribbed from comp lang python, posting by Nick
Craig-Wood January 8, 2009). He noted it was untested, will require rewriting::

    class Field(object):
        registry = []
        class __metaclass__(type):
            def __init__(cls, name, bases, dict):
		cls.registry.append(cls)
	def __new__(cls, a):
	    if cls != Field:
		return object.__new__(cls, a)
	    for subcls in cls.registry:
		if subcls == Field:
		    continue
		try:
		    return subcls(a)
		except ValueError:
		    pass
	    raise ValueError("Couldn't find subclass")
	def __init__(self, input):
	    super(Field, self).__init__(input)
	    self.data = input

    # Raise a ValueError in init if not suitable args for this subtype

    class IntegerField(Field):
	def __init__(self, s):
	    s = int(s)
	    super(IntegerField, self).__init__(s)
	    self.s = s

    class ListField(Field):
	def __init__(self, s):
	    if ',' not in s:
		raise ValueError("Not a list")
	    super(ListField, self).__init__(s)
	    self.s = s.split(',')

    class StringField(Field):
	pass 


Further Reading
================================================================================

    TBD
        
