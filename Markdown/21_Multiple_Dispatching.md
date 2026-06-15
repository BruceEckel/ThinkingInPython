# Multiple Dispatching

When dealing with multiple types which are interacting, a program can
get particularly messy. For example, consider a system that parses and
executes mathematical expressions. You want to be able to say `Number +
Number`, `Number \* Number`, etc., where `Number` is the base class
for a family of numerical objects. But when you say `a + b`, and you
don't know the exact type of either `a` or `b`, so how can you get
them to interact properly?

The answer starts with something you probably don't think about: Python
performs only single dispatching. That is, if you are performing an
operation on more than one object whose type is unknown, Python can
invoke the dynamic binding mechanism on only one of those types. This
doesn't solve the problem, so you end up detecting some types manually
and effectively producing your own dynamic binding behavior.

The solution is called *multiple dispatching*. Remember that
polymorphism can occur only via member function calls, so if you want
double dispatching to occur, there must be two member function calls:
the first to determine the first unknown type, and the second to
determine the second unknown type. With multiple dispatching, you must
have a polymorphic method call to determine each of the types.
Generally, you'll set up a configuration such that a single member
function call produces more than one dynamic member function call and
thus determines more than one type in the process. To get this effect,
you need to work with more than one polymorphic method call: you'll need
one call for each dispatch. The methods in the following example are
called `compete()` and `eval()`, and are both members of the same
type. (In this case there will be only two dispatches, which is referred
to as *double dispatching*). If you are working with two different type
hierarchies that are interacting, then you'll have to have a polymorphic
method call in each hierarchy.

Both versions below share one result type: an enumeration of the three outcomes,
win, lose, and draw. Rather than duplicate it, put it in its own module that both
examples import. Python's `enum` library makes the type directly, and each member
is a singleton you can compare and print:

```python
# outcome.py
# The win/lose/draw result of one Item competing with another.
from enum import Enum


class Outcome(Enum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

    def __str__(self):
        return self.value
```

Both versions also share two small helpers: one to generate random pairs of
items, and one to play a pair off and print the result. Those go in a module too,
so each example below shows only its dispatch mechanism:

```python
# arena.py
# Helpers shared by both versions: generate random pairs of Items, and
# play one pair off against the other.
import random


def item_pair_gen(base, n):
    items = base.__subclasses__()
    for _ in range(n):
        yield random.choice(items)(), random.choice(items)()


def match(item1, item2):
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
```

Here's an example of multiple dispatching:

```python
# paper_scissors_rock.py
# Demonstration of multiple dispatching.
from arena import item_pair_gen, match
from outcome import Outcome


class Item:
    def __str__(self):
        return self.__class__.__name__

class Paper(Item):
    def compete(self, item):
        # First dispatch: self was Paper
        return item.eval_paper(self)
    def eval_paper(self, item):
        # Item was Paper, we're in Paper
        return Outcome.DRAW
    def eval_scissors(self, item):
        # Item was Scissors, we're in Paper
        return Outcome.WIN
    def eval_rock(self, item):
        # Item was Rock, we're in Paper
        return Outcome.LOSE

class Scissors(Item):
    def compete(self, item):
        # First dispatch: self was Scissors
        return item.eval_scissors(self)
    def eval_paper(self, item):
        # Item was Paper, we're in Scissors
        return Outcome.LOSE
    def eval_scissors(self, item):
        # Item was Scissors, we're in Scissors
        return Outcome.DRAW
    def eval_rock(self, item):
        # Item was Rock, we're in Scissors
        return Outcome.WIN

class Rock(Item):
    def compete(self, item):
        # First dispatch: self was Rock
        return item.eval_rock(self)
    def eval_paper(self, item):
        # Item was Paper, we're in Rock
        return Outcome.WIN
    def eval_scissors(self, item):
        # Item was Scissors, we're in Rock
        return Outcome.LOSE
    def eval_rock(self, item):
        # Item was Rock, we're in Rock
        return Outcome.DRAW

for item1, item2 in item_pair_gen(Item, 20):
    match(item1, item2)
```

One of the things you might notice is that the information about the various
combinations is encoded into each type of `Item`. It actually ends up
being a kind of table, except that it is spread out through all the
classes. This is not very easy to maintain if you expect to modify
the behavior or to add a new `Item` class. Instead, it can be more
sensible to make the table explicit, like this:

```python
# paper_scissors_rock2.py
# Multiple dispatching using a table
from arena import item_pair_gen, match
from outcome import Outcome


class Item:
    def compete(self, item):
        # Use a tuple for table lookup:
        return outcome[self.__class__, item.__class__]
    def __str__(self):
        return self.__class__.__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass

outcome = {
  (Paper, Rock): Outcome.WIN,
  (Paper, Scissors): Outcome.LOSE,
  (Paper, Paper): Outcome.DRAW,
  (Scissors, Paper): Outcome.WIN,
  (Scissors, Rock): Outcome.LOSE,
  (Scissors, Scissors): Outcome.DRAW,
  (Rock, Scissors): Outcome.WIN,
  (Rock, Paper): Outcome.LOSE,
  (Rock, Rock): Outcome.DRAW,
}

for item1, item2 in item_pair_gen(Item, 20):
    match(item1, item2)
```

It's a tribute to the flexibility of dictionaries that a tuple can be
used as a key just as easily as a single object.

## One Type or Many

Python dispatches on a single type at a time. For dispatch on *one* argument's
type, `functools.singledispatch` (see [the Visitor chapter](22_Visitor.md)) gives you open,
per-type functions. For dispatch on *two or more* types at once, the table above
is the idiomatic answer: a `dict` keyed by a tuple of types. Adding a new `Item`
is then a matter of adding rows to the table, with no methods to edit across the
classes.

The double-dispatch version, where each class implements `eval_paper`,
`eval_scissors`, and `eval_rock`, is a workaround for languages that cannot store
types in a table and look a behavior up by them. Python can, so the table is
both shorter and easier to maintain. Reach for the spread-out method version
only when a combination needs substantial, type-specific code that will not fit
in a table cell.
