
********************************************************************************
Observer
********************************************************************************

Decoupling code behavior

*Observer*, and a category of callbacks called "multiple dispatching (not in
*Design Patterns*)" including the *Visitor* from *Design Patterns*. Like the
other forms of callback, this contains a hook point where you can change code.
The difference is in the observer's completely dynamic nature. It is often used
for the specific case of changes based on other object's change of state, but is
also the basis of event management. Anytime you want to decouple the source of
the call from the called code in a completely dynamic way.

The observer pattern solves a fairly common problem: What if a group of objects
needs to update themselves when some object changes state? This can be seen in
the "model-view" aspect of Smalltalk's MVC (model-view-controller), or the
almost-equivalent "Document-View Architecture." Suppose that you have some data
(the "document") and more than one view, say a plot and a textual view. When you
change the data, the two views must know to update themselves, and that's what
the observer facilitates. It's a common enough problem that its solution has
been made a part of the standard **java.util** library.

There are two types of objects used to implement the observer pattern in Python.
The **Observable** class keeps track of everybody who wants to be informed when
a change happens, whether the "state" has changed or not. When someone says "OK,
everybody should check and potentially update themselves," the **Observable**
class performs this task by calling the **notifyObservers( )** method for each
one on the list. The **notifyObservers( )** method is part of the base class
**Observable**.

There are actually two "things that change" in the observer pattern: the
quantity of observing objects and the way an update occurs. That is, the
observer pattern allows you to modify both of these without affecting the
surrounding code.

**Observer** is an "interface" class that only has one member function,
**update( )**. This function is called by the object that's being observed, when
that object decides its time to update all its observers. The arguments are
optional; you could have an **update( )** with no arguments and that would still
fit the observer pattern; however this is more general-it allows the observed
object to pass the object that caused the update (since an **Observer** may be
registered with more than one observed object) and any extra information if
that's helpful, rather than forcing the **Observer** object to hunt around to
see who is updating and to fetch any other information it needs.

The "observed object" that decides when and how to do the updating will be
called the **Observable**.

**Observable** has a flag to indicate whether it's been changed. In a simpler
design, there would be no flag; if something happened, everyone would be
notified. The flag allows you to wait, and only notify the **Observer**\s when
you decide the time is right. Notice, however, that the control of the flag's
state is **protected**, so that only an inheritor can decide what constitutes a
change, and not the end user of the resulting derived **Observer** class.

Most of the work is done in **notifyObservers( )**. If the **changed** flag has
not been set, this does nothing. Otherwise, it first clears the **changed** flag
so repeated calls to **notifyObservers( )** won't waste time. This is done
before notifying the observers in case the calls to **update( )** do anything
that causes a change back to this **Observable** object. Then it moves through
the **set** and calls back to the **update( )** member function of each
**Observer**.

At first it may appear that you can use an ordinary **Observable** object to
manage the updates. But this doesn't work; to get an effect, you *must* inherit
from **Observable** and somewhere in your derived-class code call **setChanged(
)**. This is the member function that sets the "changed" flag, which means that
when you call **notifyObservers( )** all of the observers will, in fact, get
notified. *Where* you call **setChanged( )** depends on the logic of your
program.

Observing Flowers
--------------------------------------------------------------------------------

Since Python doesn't have standard library components to support the observer
pattern (like Java does), we must first create one. The simplest thing to do is
translate the Java standard library **Observer** and **Observable** classes.
This also provides easier translation from Java code that uses these libraries.

In trying to do this, we encounter a minor snag, which is the fact that Java has
a **synchronized** keyword that provides built-in support for thread
synchronization. We could certainly accomplish the same thing by hand, using
code like this::

    # util/ToSynch.py

    import threading
    class ToSynch:
        def __init__(self):
            self.mutex = threading.RLock()
            self.val = 1
        def aSynchronizedMethod(self):
            self.mutex.acquire()
            try:
                self.val += 1
                return self.val
            finally:
                self.mutex.release()


But this rapidly becomes tedious to write and to read. Peter Norvig provided me
with a much nicer solution::

    # util/Synchronization.py
    '''Simple emulation of Java's 'synchronized'
    keyword, from Peter Norvig.'''
    import threading

    def synchronized(method):
        def f(*args):
            self = args[0]
            self.mutex.acquire();
            # print(method.__name__, 'acquired')
            try:
                return apply(method, args)
            finally:
                self.mutex.release();
                # print(method.__name__, 'released')
        return f

    def synchronize(klass, names=None):
        """Synchronize methods in the given class.
        Only synchronize the methods whose names are
        given, or all methods if names=None."""
        if type(names)==type(''): names = names.split()
        for (name, val) in klass.__dict__.items():
            if callable(val) and name != '__init__' and \
              (names == None or name in names):
                # print("synchronizing", name)
                klass.__dict__[name] = synchronized(val)

    # You can create your own self.mutex, or inherit
    # from this class:
    class Synchronization:
        def __init__(self):
            self.mutex = threading.RLock()


The **synchronized( )** function takes a method and wraps it in a function that
adds the mutex functionality. The method is called inside this function::

    return apply(method, args)

and as the **return** statement passes through the **finally** clause, the mutex
is released.

This is in some ways the *Decorator* design pattern, but much simpler to create
and use. All you have to say is::

    myMethod = synchronized(myMethod)

To surround your method with a mutex.

**synchronize( )** is a convenience function that applies **synchronized( )** to
an entire class, either all the methods in the class (the default) or selected
methods which are named in a string as the second argument.

Finally, for **synchronized( )** to work there must be a **self.mutex** created
in every class that uses **synchronized( )**. This can be created by hand by the
class author, but it's more consistent to use inheritance, so the base class
**Synchronization** is provided.

Here's a simple test of the **Synchronization** module::

    # util/TestSynchronization.py
    from Synchronization import *

    # To use for a method:
    class C(Synchronization):
        def __init__(self):
            Synchronization.__init__(self)
            self.data = 1
        def m(self):
            self.data += 1
            return self.data
        m = synchronized(m)
        def f(self): return 47
        def g(self): return 'spam'

    # So m is synchronized, f and g are not.
    c = C()

    # On the class level:
    class D(C):
        def __init__(self):
            C.__init__(self)
        # You must override an un-synchronized method
        # in order to synchronize it (just like Java):
        def f(self): C.f(self)

    # Synchronize every (defined) method in the class:
    synchronize(D)
    d = D()
    d.f() # Synchronized
    d.g() # Not synchronized
    d.m() # Synchronized (in the base class)

    class E(C):
        def __init__(self):
            C.__init__(self)
        def m(self): C.m(self)
        def g(self): C.g(self)
        def f(self): C.f(self)
    # Only synchronizes m and g. Note that m ends up
    # being doubly-wrapped in synchronization, which
    # doesn't hurt anything but is inefficient:
    synchronize(E, 'm g')
    e = E()
    e.f()
    e.g()
    e.m()


You must call the base class constructor for **Synchronization**, but that's
all. In class **C** you can see the use of **synchronized( )** for **m**,
leaving **f** and **g** alone. Class **D** has all its methods synchronized en
masse, and class **E** uses the convenience function to synchronize **m** and
**g**. Note that since **m** ends up being synchronized twice, it will be
entered and left twice for every call, which isn't very desirable [there may be
a fix for this]::

    # util/Observer.py
    # Class support for "observer" pattern.
    from Synchronization import *

    class Observer:
        def update(observable, arg):
            '''Called when the observed object is
            modified. You call an Observable object's
            notifyObservers method to notify all the
            object's observers of the change.'''
            pass

    class Observable(Synchronization):
        def __init__(self):
            self.obs = []
            self.changed = 0
            Synchronization.__init__(self)

        def addObserver(self, observer):
            if observer not in self.obs:
                self.obs.append(observer)

        def deleteObserver(self, observer):
            self.obs.remove(observer)

        def notifyObservers(self, arg = None):
            '''If 'changed' indicates that this object
            has changed, notify all its observers, then
            call clearChanged(). Each observer has its
            update() called with two arguments: this
            observable object and the generic 'arg'.'''

            self.mutex.acquire()
            try:
                if not self.changed: return
                # Make a local copy in case of synchronous
                # additions of observers:
                localArray = self.obs[:]
                self.clearChanged()
            finally:
                self.mutex.release()
            # Updating is not required to be synchronized:
            for observer in localArray:
                observer.update(self, arg)

        def deleteObservers(self): self.obs = []
        def setChanged(self): self.changed = 1
        def clearChanged(self): self.changed = 0
        def hasChanged(self): return self.changed
        def countObservers(self): return len(self.obs)

    synchronize(Observable,
      "addObserver deleteObserver deleteObservers " +
      "setChanged clearChanged hasChanged " +
      "countObservers")


Using this library, here is an example of the observer pattern::

    # observer/ObservedFlower.py
    # Demonstration of "observer" pattern.
    import sys
    sys.path += ['../util']
    from Observer import Observer, Observable

    class Flower:
        def __init__(self):
            self.isOpen = 0
            self.openNotifier = Flower.OpenNotifier(self)
            self.closeNotifier= Flower.CloseNotifier(self)
        def open(self): # Opens its petals
            self.isOpen = 1
            self.openNotifier.notifyObservers()
            self.closeNotifier.open()
        def close(self): # Closes its petals
            self.isOpen = 0
            self.closeNotifier.notifyObservers()
            self.openNotifier.close()
        def closing(self): return self.closeNotifier

        class OpenNotifier(Observable):
            def __init__(self, outer):
                Observable.__init__(self)
                self.outer = outer
                self.alreadyOpen = 0
            def notifyObservers(self):
                if self.outer.isOpen and \
                not self.alreadyOpen:
                    self.setChanged()
                    Observable.notifyObservers(self)
                    self.alreadyOpen = 1
            def close(self):
                self.alreadyOpen = 0

        class CloseNotifier(Observable):
            def __init__(self, outer):
                Observable.__init__(self)
                self.outer = outer
                self.alreadyClosed = 0
            def notifyObservers(self):
                if not self.outer.isOpen and \
                not self.alreadyClosed:
                    self.setChanged()
                    Observable.notifyObservers(self)
                    self.alreadyClosed = 1
            def open(self):
                alreadyClosed = 0

    class Bee:
        def __init__(self, name):
            self.name = name
            self.openObserver = Bee.OpenObserver(self)
            self.closeObserver = Bee.CloseObserver(self)
        # An inner class for observing openings:
        class OpenObserver(Observer):
            def __init__(self, outer):
                self.outer = outer
            def update(self, observable, arg):
                print("Bee " + self.outer.name + \)
                  "'s breakfast time!"
        # Another inner class for closings:
        class CloseObserver(Observer):
            def __init__(self, outer):
                self.outer = outer
            def update(self, observable, arg):
                print("Bee " + self.outer.name + \)
                  "'s bed time!"

    class Hummingbird:
        def __init__(self, name):
            self.name = name
            self.openObserver = \
              Hummingbird.OpenObserver(self)
            self.closeObserver = \
              Hummingbird.CloseObserver(self)
        class OpenObserver(Observer):
            def __init__(self, outer):
                self.outer = outer
            def update(self, observable, arg):
                print("Hummingbird " + self.outer.name + \
                  "'s breakfast time!")
        class CloseObserver(Observer):
            def __init__(self, outer):
                self.outer = outer
            def update(self, observable, arg):
                print("Hummingbird " + self.outer.name + \
                  "'s bed time!")

    f = Flower()
    ba = Bee("Eric")
    bb = Bee("Eric 0.5")
    ha = Hummingbird("A")
    hb = Hummingbird("B")
    f.openNotifier.addObserver(ha.openObserver)
    f.openNotifier.addObserver(hb.openObserver)
    f.openNotifier.addObserver(ba.openObserver)
    f.openNotifier.addObserver(bb.openObserver)
    f.closeNotifier.addObserver(ha.closeObserver)
    f.closeNotifier.addObserver(hb.closeObserver)
    f.closeNotifier.addObserver(ba.closeObserver)
    f.closeNotifier.addObserver(bb.closeObserver)
    # Hummingbird 2 decides to sleep in:
    f.openNotifier.deleteObserver(hb.openObserver)
    # A change that interests observers:
    f.open()
    f.open() # It's already open, no change.
    # Bee 1 doesn't want to go to bed:
    f.closeNotifier.deleteObserver(ba.closeObserver)
    f.close()
    f.close() # It's already closed; no change
    f.openNotifier.deleteObservers()
    f.open()
    f.close()

The events of interest are that a **Flower** can open or close. Because of the
use of the inner class idiom, both these events can be separately observable
phenomena. **OpenNotifier** and **CloseNotifier** both inherit **Observable**,
so they have access to **setChanged( )** and can be handed to anything that
needs an **Observable**.

The inner class idiom also comes in handy to define more than one kind of
**Observer**, in **Bee** and **Hummingbird**, since both those classes may want
to independently observe **Flower** openings and closings. Notice how the inner
class idiom provides something that has most of the benefits of inheritance (the
ability to access the **private** data in the outer class, for example) without
the same restrictions.

In **main( )**, you can see one of the prime benefits of the observer pattern:
the ability to change behavior at run time by dynamically registering and un-
registering **Observer**\s with **Observable**\s.

If you study the code above you'll see that **OpenNotifier** and
**CloseNotifier** use the basic **Observable** interface. This means that you
could inherit other completely different **Observer** classes; the only
connection the **Observer**\s have with **Flower**\s is the **Observer**
interface.

A Visual Example of Observers
=======================================================================

The following example is similar to the **ColorBoxes** example from *Thinking in
Java*. Boxes are placed in a grid on the screen and each one is initialized to a
random color. In addition, each box **implements** the **Observer** interface
and is registered with an **Observable** object. When you click on a box, all of
the other boxes are notified that a change has been made because the
**Observable** object automatically calls each **Observer** object's **update(
)** method. Inside this method, the box checks to see if it's adjacent to the
one that was clicked, and if so it changes its color to match the clicked box.
(NOTE: this example has not been converted. See further down for a version that
has the GUI but not the Observers, in PythonCard.)::

    # observer/BoxObserver.py
    # Demonstration of Observer pattern using
    # Java's built-in observer classes.

    # You must inherit a type of Observable:
    class BoxObservable(Observable):
        def notifyObservers(self, Object b):
            # Otherwise it won't propagate changes:
            setChanged()
            super.notifyObservers(b)

    class BoxObserver(JFrame):
        Observable notifier = BoxObservable()
        def __init__(self, grid):
            setTitle("Demonstrates Observer pattern")
            Container cp = getContentPane()
            cp.setLayout(GridLayout(grid, grid))
            for(int x = 0 x < grid x++)
                for(int y = 0 y < grid y++)
                    cp.add(OCBox(x, y, notifier))

        def main(self, String[] args):
            grid = 8
                if(args.length > 0)
                    grid = Integer.parseInt(args[0])
                JFrame f = BoxObserver(grid)
                f.setSize(500, 400)
                f.setVisible(1)
                # JDK 1.3:
                f.setDefaultCloseOperation(EXIT_ON_CLOSE)
                # Add a WindowAdapter if you have JDK 1.2

    class OCBox(JPanel) implements Observer:
        Color cColor = newColor()
        colors = [
          Color.black, Color.blue, Color.cyan,
          Color.darkGray, Color.gray, Color.green,
          Color.lightGray, Color.magenta,
          Color.orange, Color.pink, Color.red,
          Color.white, Color.yellow
        ]
        def newColor():
            return colors[
              (int)(Math.random() * colors.length)
            ]

        def __init__(self, x, y, Observable notifier):
            self.x = x
            self.y = y
            notifier.addObserver(self)
            self.notifier = notifier
            addMouseListener(ML())

        def paintComponent(self, Graphics g):
            super.paintComponent(g)
            g.setColor(cColor)
            Dimension s = getSize()
            g.fillRect(0, 0, s.width, s.height)

        class ML(MouseAdapter):
            def mousePressed(self, MouseEvent e):
                notifier.notifyObservers(OCBox.self)

        def update(self, Observable o, Object arg):
            OCBox clicked = (OCBox)arg
            if(nextTo(clicked)):
                cColor = clicked.cColor
                repaint()

        def nextTo(OCBox b):
            return Math.abs(x - b.x) <= 1 &&
                Math.abs(y - b.y) <= 1


When you first look at the online documentation for **Observable**, it's a bit
confusing because it appears that you can use an ordinary **Observable** object
to manage the updates. But this doesn't work; try it-inside **BoxObserver**,
create an **Observable** object instead of a **BoxObservable** object and see
what happens: nothing. To get an effect, you *must* inherit from **Observable**
and somewhere in your derived-class code call **setChanged( )**. This is the
method that sets the "changed" flag, which means that when you call
**notifyObservers( )** all of the observers will, in fact, get notified. In the
example above **setChanged( )** is simply called within **notifyObservers( )**,
but you could use any criterion you want to decide when to call **setChanged(
)**.

**BoxObserver** contains a single **Observable** object called **notifier**, and
every time an **OCBox** object is created, it is tied to **notifier**. In
**OCBox**, whenever you click the mouse the **notifyObservers( )** method is
called, passing the clicked object in as an argument so that all the boxes
receiving the message (in their **update( )** method) know who was clicked and
can decide whether to change themselves or not. Using a combination of code in
**notifyObservers( )** and **update( )** you can work out some fairly complex
schemes.

It might appear that the way the observers are notified must be frozen at
compile time in the **notifyObservers( )** method. However, if you look more
closely at the code above you'll see that the only place in **BoxObserver** or
**OCBox** where you're aware that you're working with a **BoxObservable** is at
the point of creation of the **Observable** object-from then on everything uses
the basic **Observable** interface. This means that you could inherit other
**Observable** classes and swap them at run time if you want to change
notification behavior then.

Here is a version of the above that doesn't use the Observer pattern, written by
Kevin Altis using PythonCard, and placed here as a starting point for a
translation that does include Observer::

    # observer/BoxObserver.py
    """ Written by Kevin Altis as a first-cut for
    converting BoxObserver to Python. The Observer
    hasn't been integrated yet.
    To run this program, you must:
    Install WxPython from
    http://www.wxpython.org/download.php
    Install PythonCard. See:
    http://pythoncard.sourceforge.net
    """
    from PythonCardPrototype import log, model
    import random

    GRID = 8

    class ColorBoxesTest(model.Background):
        def on_openBackground(self, event):
            self.document = []
            for row in range(GRID):
                line = []
                for column in range(GRID):
                    line.append(self.createBox(row, column))
                self.document.append(line[:])
        def createBox(self, row, column):
            colors = ['black', 'blue', 'cyan',
            'darkGray', 'gray', 'green',
            'lightGray', 'magenta',
            'orange', 'pink', 'red',
            'white', 'yellow']
            width, height = self.panel.GetSizeTuple()
            boxWidth = width / GRID
            boxHeight = height / GRID
            log.info("width:" + str(width) +
              " height:" + str(height))
            log.info("boxWidth:" + str(boxWidth) +
              " boxHeight:" + str(boxHeight))
            # use an empty image, though some other
            # widgets would work just as well
            boxDesc = {'type':'Image',
              'size':(boxWidth, boxHeight), 'file':''}
            name = 'box-%d-%d' % (row, column)
            # There is probably a 1 off error in the
            # calculation below since the boxes should
            # probably have a slightly different offset
            # to prevent overlaps
            boxDesc['position'] = \
              (column * boxWidth, row * boxHeight)
            boxDesc['name'] = name
            boxDesc['backgroundColor'] = \
              random.choice(colors)
            self.components[name] =  boxDesc
            return self.components[name]

        def changeNeighbors(self, row, column, color):

            # This algorithm will result in changing the
            # color of some boxes more than once, so an
            # OOP solution where only neighbors are asked
            # to change or boxes check to see if they are
            # neighbors before changing would be better
            # per the original example does the whole grid
            # need to change its state at once like in a
            # Life program? should the color change
            # in the propogation of another notification
            # event?

            for r in range(max(0, row - 1),
                           min(GRID, row + 2)):
                for c in range(max(0, column - 1),
                               min(GRID, column + 2)):
                    self.document[r][c].backgroundColor=color

        # this is a background handler, so it isn't
        # specific to a single widget. Image widgets
        # don't have a mouseClick event (wxCommandEvent
        # in wxPython)
        def on_mouseUp(self, event):
            target = event.target
            prefix, row, column = target.name.split('-')
            self.changeNeighbors(int(row), int(column),
                                 target.backgroundColor)

    if __name__ == '__main__':
        app = model.PythonCardApp(ColorBoxesTest)
        app.MainLoop()


This is the resource file for running the program (see PythonCard for details)::

    # observer/BoxObserver.rsrc.py
    {'stack':{'type':'Stack',
              'name':'BoxObserver',
        'backgrounds': [
          { 'type':'Background',
            'name':'bgBoxObserver',
            'title':'Demonstrates Observer pattern',
            'position':(5, 5),
            'size':(500, 400),
            'components': [

    ] # end components
    } # end background
    ] # end backgrounds
    } }


Exercises
=======================================================================

#.  Using the approach in **Synchronization.py**, create a tool that will
    automatically wrap all the methods in a class to provide an execution trace,
    so that you can see the name of the method and when it is entered and
    exited.

#.  Create a minimal Observer-Observable design in two classes. Just create the
    bare minimum in the two classes, then demonstrate your design by creating
    one **Observable** and many **Observer**\s, and cause the **Observable** to
    update the **Observer**\s.

#.  Modify **BoxObserver.py** to turn it into a simple game. If any of the
    squares surrounding the one you clicked is part of a contiguous patch of the
    same color, then all the squares in that patch are changed to the color you
    clicked on. You can configure the game for competition between players or to
    keep track of the number of clicks that a single player uses to turn the
    field into a single color. You may also want to restrict a player's color to
    the first one that was chosen.



