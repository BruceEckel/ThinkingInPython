
*******************************************************************************
Building Application Frameworks
*******************************************************************************

An application framework allows you to inherit from a class or set of classes
and create a new application, reusing most of the code in the existing classes
and overriding one or more methods in order to customize the application to your
needs. A fundamental concept in the application framework is the *Template
Method* which is typically hidden beneath the covers and drives the application
by calling the various methods in the base class (some of which you have
overridden in order to create the application).

For example, whenever you create an applet you're using an application
framework: you inherit from **JApplet** and then override **init( )**. The
applet mechanism (which is a *Template Method*) does the rest by drawing the
screen, handling the event loop, resizing, etc.

Template Method
=======================================================================

An important characteristic of the *Template Method* is that it is defined in
the base class and cannot be changed. It's sometimes a **private** method but
it's virtually always **final**. It calls other base-class methods (the ones you
override) in order to do its job, but it is usually called only as part of an
initialization process (and thus the client programmer isn't necessarily able to
call it directly)::

    # AppFrameworks/TemplateMethod.py
    # Simple demonstration of Template Method.

    class ApplicationFramework:
        def __init__(self):
            self.__templateMethod()
        def __templateMethod(self):
            for i in range(5):
                self.customize1()
                self.customize2()

    # Create an "application":
    class MyApp(ApplicationFramework):
        def customize1(self):
            print("Nudge, nudge, wink, wink! ",)
        def customize2(self):
            print("Say no more, Say no more!")

    MyApp()



The base-class constructor is responsible for performing the necessary
initialization and then starting the "engine" (the template method) that runs
the application (in a GUI application, this "engine" would be the main event
loop). The client programmer simply provides definitions for **customize1( )**
and **customize2( )** and the "application" is ready to run.

We'll see *Template Method* numerous other times throughout the book.

Exercises
=======================================================================

#.  Create a framework that takes a list of file names on the command line. It
    opens each file except the last for reading, and the last for writing. The
    framework will process each input file using an undetermined policy and
    write the output to the last file. Inherit to customize this framework to
    create two separate applications:

        #. Converts all the letters in each file to uppercase.
        #. Searches the files for words given in the first file.



