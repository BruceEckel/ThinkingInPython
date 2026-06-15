
Incorporate
https://www.bruceeckel.com/2018/09/16/json-encoding-python-dataclasses/
Into the "Data Classes as Types" chapter

---


Incorporate these articles into the "Decorators" chapter:
https://www.artima.com/weblogs/viewpost.jsp?thread=240808
https://www.artima.com/weblogs/viewpost.jsp?thread=240845
https://www.artima.com/weblogs/viewpost.jsp?thread=241209

---

Incorporate https://github.com/BruceEckel/LazyGuide, but not as a single chapter. Distribute the information appropriately into existing chapters, making new chapters only if it makes sense.

----

GIL presentation?

---

More testing?

---

Ask for suggestions

---

In 21 the following appears to be duplicated in two different examples:
# An enumeration type:
class Outcome:
    def __init__(self, value, name):
        self.value = value
        self.name = name
    def __str__(self): return self.name
    def __eq__(self, other):
        return self.value == other.value

Outcome.WIN = Outcome(0, "win")
Outcome.LOSE = Outcome(1, "lose")
Outcome.DRAW = Outcome(2, "draw")

Extract that into a file imported by both examples, and use the `enum` library to make Outcome an Enum.

---

Look for other places where enumerations might be better.
Look for other places where code is duplicated and could be lifted into a file to be imported.
