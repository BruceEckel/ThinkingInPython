********************************************************************************
Iterators: Decoupling Algorithms from Containers
********************************************************************************

.. note:: This chapter has not had any significant translation yet.

Alexander Stepanov thought for years about the problem of generic programming
techniques before creating the STL (along with Dave Musser). He came to the
conclusion that all algorithms are defined on algebraic structures - what we
would call containers.

In the process, he realized that iterators are central to the use of algorithms,
because they decouple the algorithms from the specific type of container that
the algorithm might currently be working with. This means that you can describe
the algorithm without worrying about the particular sequence it is operating on.
More generally, *any* code that you write using iterators is decoupled from the
data structure that the code is manipulating, and thus your code is more general
and reusable.

The use of iterators also extends your code into the realm of *functional
programming*, whose objective is to describe *what* a program is doing at every
step rather than *how* it is doing it. That is, you say "sort" rather than
describing the sort. The objective of the C++ STL was to provide this *generic
programming* approach for C++ (how successful this approach will actually be
remains to be seen).

If you've used containers in Java (and it's hard to write code without using
them), you've used iterators - in the form of the **Enumeration** in Java
1.0/1.1 and the **Iterator** in Java 2. So you should already be familiar with
their general use. If not, see Chapter 9, *Holding Your Objects*, under
*Iterators* in *Thinking in Java, 3rd edition* (freely downloadable from
*www.BruceEckel.com*).

Because the Java 2 containers rely heavily on iterators they become excellent
candidates for generic/functional programming techniques. This chapter will
explore these techniques by converting the STL algorithms to Java, for use with
the Java 2 container library.

Type-Safe Iterators
=======================================================================

In *Thinking in Java*, I show the creation of a type-safe container that will
only accept a particular type of object. A reader, Linda Pazzaglia, asked for
the other obvious type-safe component, an iterator that would work with the
basic **java.util** containers, but impose the constraint that the type of
objects that it iterates over be of a particular type.

If Java ever includes a template mechanism, this kind of iterator will have the
added advantage of being able to return a specific type of object, but without
templates you are forced to return generic **Object**\s, or to require a bit of
hand-coding for every type that you want to iterate through. I will take the
former approach.

A second design decision involves the time that the type of object is
determined. One approach is to take the type of the first object that the
iterator encounters, but this is problematic because the containers may
rearrange the objects according to an internal ordering mechanism (such as a
hash table) and thus you may get different results from one iteration to the
next. The safe approach is to require the user to establish the type during
construction of the iterator.

Lastly, how do we build the iterator? We cannot rewrite the existing Java
library classes that already produce **Enumeration**\s and **Iterator**\s.
However, we can use the *Decorator* design pattern, and create a class that
simply wraps the **Enumeration** or **Iterator** that is produced, generating a
new object that has the iteration behavior that we want (which is, in this case,
to throw a **RuntimeException** if an incorrect type is encountered) but with
the same interface as the original **Enumeration** or **Iterator**, so that it
can be used in the same places (you may argue that this is actually a *Proxy*
pattern, but it's more likely *Decorator* because of its intent). Here is the
code::

    # util/TypedIterator.py

    class TypedIterator(Iterator):
        def __init__(self, it, type):
            self.imp = it
            self.type = type

        def hasNext(self):
            return imp.hasNext()

        def remove(self): imp.remove()
        def next(self):
            obj = imp.next()
            if(!type.isInstance(obj))
                throw ClassCastException(
                  "TypedIterator for type " + type +
                  " encountered type: " + obj.getClass())
            return obj





