.. index::
   messenger (data transfer object)
   data transfer object (messenger)

********************************************************************************
Messenger/Data Transfer Object
********************************************************************************

The *Messenger* or *Data Transfer Object* is a way to pass a clump of
information around. The most typical place for this is in return values from
functions, where tuples or dictionaries are often used. However, those rely on
indexing; in the case of tuples this requires the consumer to keep track of
numerical order, and in the case of a **dict** you must use the ``d["name"]``
syntax which can be slightly less desireable.

A Messenger is simply an object with attributes corresponding to the names of
the data you want to pass around or return::

    # messenger/MessengerIdiom.py

    class Messenger:
        def __init__(self, **kwargs):
            self.__dict__ = kwargs

    m = Messenger(info="some information", b=['a', 'list'])
    m.more = 11
    print m.info, m.b, m.more

The trick here is that the ``__dict__`` for the object is just assigned to the
**dict** that is automatically created by the ``**kwargs`` argument.

Although one could easily create a ``Messenger`` class and put it into a library
and import it, there are so few lines to describe it that it usually makes more
sense to just define it in-place whenever you need it -- it is probably easier
for the reader to follow, as well.
    