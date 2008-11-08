# builder.py
import sys, os, stat
"""
Adds build rules atop Python, to replace make, etc.
by Bruce Eckel
License: Creative Commons with Attribution.
"""

def reportError(msg):
    print >> sys.stderr, "Error:", msg
    sys.exit(1)

class Dependency(object):
    "Created by the decorator to represent a single dependency relation"

    changed = True
    unchanged = False

    @staticmethod
    def show(flag):
        if flag: return "Updated"
        return "Unchanged"

    def __init__(self, target, dependency):
        self.target = target
        self.dependency = dependency

    def __str__(self):
        return "target: %s, dependency: %s" % (self.target, self.dependency)

    @staticmethod
    def create(target, dependency): # Simple Factory
        if target == None:
            return NoTarget(dependency)
        if type(target) == str: # String means file name
            if dependency == None:
                return FileToNone(target, None)
            if type(dependency) == str:
                return FileToFile(target, dependency)
            if type(dependency) == Dependency:
                return FileToDependency(target, dependency)
        reportError("No match found in create() for target: %s, dependency: %s"
            % (target,  dependency))

    def updated(self):
        """
        Call to determine whether this is up to date.
        Returns 'changed' if it had to update itself.
        """
        assert False, "Must override Dependency.updated() in derived class"

class NoTarget(Dependency): # Always call updated() on dependency
    def __init__(self, dependency):
        Dependency.__init__(self, None, dependency)
    def updated(self):
        if not self.dependency:
            return Dependency.changed # (None, None) -> always run rule
        return self.dependency.updated() # Must be a Dependency or subclass

class FileToNone(Dependency): # Run rule if file doesn't exist
    def updated(self):
        if not os.path.exists(self.target):
            return Dependency.changed
        return Dependency.unchanged

class FileToFile(Dependency): # Compare file datestamps
    def updated(self):
        if not os.path.exists(self.dependency):
            reportError("%s does not exist" % self.dependency)
        if not os.path.exists(self.target):
            return Dependency.changed # If it doesn't exist it needs to be made
        if os.path.getmtime(self.dependency) > os.path.getmtime(self.target):
            return Dependency.changed
        return Dependency.unchanged

class FileToDependency(Dependency): # Update if dependency object has changed
    def updated(self):
        if self.dependency.updated():
            return Dependency.changed
        if not os.path.exists(self.target):
            return Dependency.changed # If it doesn't exist it needs to be made
        return Dependency.unchanged

class rule(object):
    """
    Decorator that turns a function into a build rule. First file or object in
    decorator arglist is the target, remainder are dependencies.
    """
    rules = []
    default = None

    class _Rule(object):
        """
        Command pattern. name, dependencies, ruleUpdater and description are
        all injected by class rule.
        """

        def updated(self):
            if Dependency.changed in [d.updated() for d in self.dependencies]:
                self.ruleUpdater()
                return Dependency.changed
            return Dependency.unchanged

        def __str__(self): return self.description

    def __init__(self, *decoratorArgs):
        """
        This constructor is called first when the decorated function is
        defined, and captures the arguments passed to the decorator itself.
        (Note Builder pattern)
        """
        self._rule = rule._Rule()
        decoratorArgs = list(decoratorArgs)
        if decoratorArgs:
            if len(decoratorArgs) == 1:
                decoratorArgs.append(None)
            target = decoratorArgs.pop(0)
            if type(target) != list:
                target = [target]
            self._rule.dependencies = [Dependency.create(targ, dep)
                for targ in target for dep in decoratorArgs]
        else: # No arguments
            self._rule.dependencies = [Dependency.create(None, None)]

    def __call__(self, func):
        """
        This is called right after the constructor, and is passed the function
        object being decorated. The returned _rule object replaces the original
        function.
        """
        if func.__name__ in [r.name for r in rule.rules]:
            reportError("@rule name %s must be unique" % func.__name__)
        self._rule.name = func.__name__
        self._rule.description = func.__doc__ or ""
        self._rule.ruleUpdater = func
        rule.rules.append(self._rule)
        return self._rule # This is substituted as the decorated function

    @staticmethod
    def update(x):
        if x == 0:
            if rule.default:
                return rule.default.updated()
            else:
                return rule.rules[0].updated()
        # Look up by name
        for r in rule.rules:
            if x == r.name:
                return r.updated()
        raise KeyError

    @staticmethod
    def main():
        """
        Produce command-line behavior
        """
        if len(sys.argv) == 1:
            print Dependency.show(rule.update(0))
        try:
            for arg in sys.argv[1:]:
                print Dependency.show(rule.update(arg))
        except KeyError:
            print "Available rules are:\n"
            for r in rule.rules:
                if r == rule.default:
                    newline = " (Default if no rule is specified)\n"
                else:
                    newline = "\n"
                print "%s:%s\t%s\n" % (r.name, newline, r)
            print "(Multiple targets will be updated in order)"
        # Create "build" commands for Windows and Unix:
        if not os.path.exists("build.bat"):
            file("build.bat", 'w').write("python build.py %1 %2 %3 %4 %5 %6 %7")
        if not os.path.exists("build"):
            # Unless you can detect cygwin independently of Windows
            file("build", 'w').write("python build.py $*")
            os.chmod("build", stat.S_IEXEC)

############### Test/Usage Examples ###############

if __name__ == "__main__":
    if not os.path.exists("build.py"):
        file("build.py", 'w').write('''\
# Use cases: both test code and usage examples
from builder import rule
import os

@rule("file1.txt")
def file1():
    "File doesn't exist; run rule"
    file("file1.txt", 'w')

def touchOrCreate(f): # Ordinary function
    "Bring file up to date; creates it if it doesn't exist"
    if os.path.exists(f):
        os.utime(f, None)
    else:
        file(f, 'w')

dependencies = ["dependency1.txt", "dependency2.txt",
                "dependency3.txt", "dependency4.txt"]

targets = ["file1.txt", "target1.txt", "target2.txt"]

allFiles = targets + dependencies

@rule(allFiles)
def multipleTargets():
    "Multiple files don't exist; run rule"
    [file(f, 'w') for f in allFiles if not os.path.exists(f)]

@rule(["target1.txt", "target2.txt"], "dependency1.txt", "dependency2.txt")
def multipleBoth():
    "Multiple targets and dependencies"
    [touchOrCreate(f) for f in ["target1.txt", "target2.txt"]]

@rule("target1.txt","dependency1.txt","dependency2.txt","dependency3.txt")
def target1():
    "Brings target1.txt up to date with its dependencies"
    touchOrCreate("target1.txt")

@rule()
def updateDependency():
    "Updates the timestamp on all dependency.* files"
    [touchOrCreate(f) for f in allFiles if f.startswith("dependency")]

@rule()
def clean():
    "Remove all created files"
    [os.remove(f) for f in allFiles if os.path.exists(f)]

@rule()
def cleanTargets():
    "Remove all target files"
    [os.remove(f) for f in targets if os.path.exists(f)]

@rule("target2.txt", "dependency2.txt", "dependency4.txt")
def target2():
    "Brings target2.txt up to date with its dependencies, or creates it"
    touchOrCreate("target2.txt")

@rule(None, target1, target2)
def target3():
    "Always brings target1 and target2 up to date"
    print target3

@rule(None, clean, file1, multipleTargets, multipleBoth, target1,
      updateDependency, target2, target3)
def all():
    "Brings everything up to date"
    print all

rule.default = all
rule.main() # Does the build, handles command-line arguments
''')