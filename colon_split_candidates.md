# Colon-splice candidates

Prose sentences with a mid-sentence colon where both halves stand as
independent clauses, so the colon can become a period. Line numbers are
the start of the containing paragraph (sentences may sit a line or two
below). Excluded: colons introducing lists, code, fragments, or
explicit announcements ("one caution:", "two worth noting:").

## 02_Tour.md

- **~47:** The `#:` comments are particular to this book: they show the console output for the example.
- **~268:** The '`r`' right before a string means "raw": backslashes are taken literally, so you don't need to double them.

## 03_Containers.md

- **~450:** A `MappingProxyType` is the one exception to watch: it blocks writes through the view, but it is a window onto the original `dict`, so changes to that underlying `dict` still show through.

## 05_Functions.md

- **~162:** The `MISSING` sentinel keeps the two cases apart: a missing key with no default raises, while a stored `None` comes back untouched.
- **~221:** A `/` ends the *positional-only* parameters: every parameter before it must be passed by position, never by name.
- **~221:** A `*` begins the *keyword-only* parameters: every parameter after it must be passed by name.
- **~251:** That matters when a subclass overrides a method: since the name is not part of the interface, the subclass can rename the parameter, and a type checker will not object.

## 06_Modules_and_Packages.md

- **~222:** Concretely, with `uv` (this book's tool of choice), that means `uv sync`, or `uv pip install -e .` for an editable install: the package resolves by name from anywhere, and edits to its source take effect immediately, without reinstalling.
- **~274:** `lazy` works with both `import` and `from ... import`, but only at module scope: using it inside a function, a class body, or a `try` block is a `SyntaxError`, and neither `lazy from module import *` nor a `lazy from __future__` import is allowed.

## 07_Classes.md

- **~92:** Python is different: you inherit an implementation, to reuse the code from the base class.
- **~162:** The `f()` function in the demo demonstrates dynamic typing: all it cares about is that `show()` can be applied to `obj`, with no other type requirements.
- **~235:** The default `@property` is *read-only*: it is only a getter.
- **~268:** A write-only property is possible but rare: a plain method is a better expression of the intent.
- **~299:** The stored value lives on the instance: `del n.total` discards it, and the next access recomputes.
- **~399:** This is a curiosity more than a technique: it works because `import` inside a class body binds like any other assignment, but composition, mixins, or a plain module-level function are almost always the clearer choice.

## 08_Static_Typing.md

- **~117:** Earlier chapters relied on *dynamic typing*: a function accepts any object, and the only requirement is that the object supports the operations performed on it.
- **~117:** Dynamic typing is often called *duck typing*: if it looks like a duck and quacks like a duck, treat it as a duck.
- **~269:** A bound constrains the parameter: `class Box[T: Shape]` accepts only `Shape` and its subclasses.
- **~312:** Alternative constructors benefit the same way: a `@classmethod` that ends with `return cls(...)` returns `Self`.

## 09_Class_Attributes.md

- **~90:** A `ClassVar` declared on a base class is inherited like any other class attribute: a subclass that doesn't declare its own copy reads straight through to the base's value, via the normal method resolution order.
- **~119:** `ClassVar` doesn't change any of this: it only tells the checker that `shared` belongs to the class, not that subclasses share storage.

## 10_Cleanup.md

- **~58:** That is why the `deleted` lines are missing from the output above: the listing ends at `End of delete loop`, the program's last statement, and each `__del__()` prints only afterward.

## 11_Testing.md

- **~3:** Tests extend the language: they state what the code is supposed to do, and check it.
- **~486:** The same approach isolates a database, a message queue, or any other service: replace the boundary function with a stand-in and assert against its result.
- **~504:** The `Account` tests are black-box: they never read a private attribute.

## 12_Data_Classes_as_Types.md

- **~160:** But notice the last two lines: a plain data class is still mutable, so `m.name = "bar"` works.
- **~270:** The check is not repeated because it cannot fail: an illegal value can never produce a `Stars` in the first place.
- **~278:** The style here is functional: instead of mutating an object and re-guarding it, you transform one legal value into a new legal value. [Static Typing](08_Static_Typing.md#type-hints) argues for letting the type carry the meaning.
- **~382:** A `BirthDate` then validates across its fields: the day must fit the month.
- **~547:** The principle is the same: make the type responsible for guaranteeing its own values.
- **~683:** Decoding goes the other way: parse the JSON into a dictionary, then hand its parts to the constructors.

## 13_Pattern_Matching.md

- **~12:** A `case _` at the end is the wildcard: it matches anything, like a default.
- **~45:** A bare name is a *capture pattern*: it always matches and binds the value to that name, which is the wildcard with a name attached:
- **~326:** When the set of types is *open* (anyone can add a new one), polymorphism is better than a `match`: each type carries its own behavior, so adding a type needs no change to a central `match`.

## 14_Functional_Error_Handling.md

- **~371:** `@safe` deserves its own check: a good input becomes a `Success`, and a raised exception becomes a `Failure` holding that exception:

## 15_Decorators.md

- **~115:** Inside the wrapper, `*args: P.args` and `**kwargs: P.kwargs` are the two halves of that captured list: `P.args` is the positional part and `P.kwargs` the keyword part.
- **~164:** The class form separates the two phases cleanly: the constructor runs once, when the function is decorated, and `__call__()` runs on every call to the decorated function.
- **~198:** `functools.update_wrapper()` does for a class instance what `functools.wraps` does for a function: it copies the wrapped function's name and docstring across.
- **~276:** `@trace` with no arguments calls `trace(add)`: the function goes straight to the constructor.
- **~276:** `@repeat(times=3)` calls `repeat(3)` first, producing an instance, then applies that instance to `greet`: the arguments go to the constructor, and the function arrives later, at `__call__()`.
- **~276:** The class form makes it visible: the function moves from `__init__()` to `__call__()` the moment the decorator gains arguments.
- **~286:** That argument-capturing class decorator scales up to small frameworks: a build tool or task runner can offer a `@rule(target, *deps)` decorator.

## 16_Context_Managers.md

- **~142:** `contextlib.contextmanager` turns a function with a single `yield` into a context manager: the code before `yield` is the setup, the yielded value is what `as` binds, and the code after `yield` is the cleanup.
- **~342:** The `finally` is the entire pattern: the crash inside the second `with` block still returns the connection, so the count is back to two.
- **~351:** Handing the same pool to several threads therefore just works: the pool becomes the throttle that limits concurrent use, which is how real database connection pools behave.
- **~391:** The last test states the pattern's purpose: the second lease hands back the very same object, not a new one.

## 17_Comprehensions.md

- **~206:** It does some redundant work: a letter present in both cases (such as `a` and `A`) has the same combined count computed twice, once for each case.
- **~292:** Python 3.15 ([PEP 798](https://peps.python.org/pep-0798/)) adds a more direct way: the unpacking operators `*` and `**` may appear in the output expression of a comprehension or generator expression, splicing each iterable or mapping into the result.

## 18_Metaprogramming.md

- **~234:** That is why `Blue` is absent from the second `Color` print: creating `PhthaloBlue` and `CeruleanBlue` removed their base `Blue`, leaving those two leaves beside `Green` and `Red`.
- **~234:** For the same reason `Round` is missing from the `Shape` registry: creating `Circle`, a subclass of `Round`, removed `Round`, leaving `Circle` and `Square`.
- **~487:** It has no runtime effect: the interpreter still lets `class C(B): pass` run.
- **~567:** Up to now we've been modifying classes: `type` builds them, and metaclasses and `__init_subclass__()` run code as they are created.
- **~727:** Both headers read `=== Fraggle ===`: for a class `display_object()` prints the class's own name, and for an instance the name of the instance's class.

## 19_Performance.md

- **~27:** If it is too slow, use Occam's Razor: try the simplest approach first.

## 20_Concurrency.md

- **~16:** Waiting can overlap on a single thread: while one task waits, the thread runs another.
- **~16:** Computing cannot: one core runs one stream of instructions at a time.
- **~23:** The pause is the point: while one coroutine waits, the *event loop* runs another.
- **~53:** The `gather()` call is where concurrency appears: all three `fetch()` coroutines are in flight at once, so the total wait is one sleep, not three.
- **~159:** Threads would not have helped: CPython runs only one thread of Python at a time, which the next section explains.

## 21_Rethinking_Objects.md

- **~37:** Objects were optional, and it brought object-oriented programming, and exceptions, into the mainstream. *Java* drew from Smalltalk: everything is an object, even when all you need is a function.
- **~56:** A subclass may add behavior, but it must honor the base class's contract: it accepts the same arguments, returns the same kinds of results, and raises no surprising exceptions.
- **~56:** This is the guarantee that makes polymorphism, and patterns like the [Template Method](25_Template_Method.md), safe: the base class calls a method and trusts every subclass to stand in for it.
- **~163:** Testing confirms the defensive copy holds: mutating the returned list leaves the original untouched:
- **~251:** The function is not worse, and it has an advantage: it does not have to live inside `Point`.
- **~338:** The alternative is composition: a type holds other types as fields.
- **~429:** Inheriting from `ABC` makes `Shape` abstract: it cannot be instantiated, and `@abstractmethod` forces every subclass to define `area()`.
- **~432:** Dynamic typing produces a different approach: any type works as long as it has the method the function calls.
- **~600:** The checker insists on the guard, and it is right to insist: without it, a `None` eventually meets `.log()` and the call fails.
- **~647:** The parameter's type improved too: `Logs` is a protocol, so any logger fits, and no caller ever sees a `| None`.
- **~679:** The test is what callers would write: if every one of them would handle absence with the same neutral behavior, centralize that behavior in a null object.
- **~705:** When a program truly needs an object, it tells you: you find yourself passing the same data into every function, or you need to bundle behavior with state.

## 22_The_Pattern_Concept.md

- **~99:** Certainly, the *Creational* patterns are fairly straightforward: how are you going to create your objects?
- **~121:** Design principles are at least as important as design structures, but for a different reason: principles ask questions about your proposed design, to apply tests for quality.

## 24_Singleton.md

- **~132:** It is *lazy*: it builds the inner object on the first call, which is why it needs the `None` sentinel and the `if` guard.
- **~231:** There are no delegating `__getattr__()` or `__setattr__()` methods here: attribute access goes straight to the one object.
- **~276:** Moving the rebinding into `__post_init__` does not help either: it runs after the fields are assigned, so it discards them.

## 25_Template_Method.md

- **~10:** The framework's runner is the template method: it calls `setUp()`, then your test, then `tearDown()`, for each test, and you never call that sequence yourself.
- **~66:** This pattern leans on the [Liskov Substitution Principle](21_Rethinking_Objects.md#liskov-substitution): a subclass must be usable wherever its base class is expected.
- **~135:** This is the same trade-off seen in [Function Objects](30_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime): a hook that holds no state is usually better as a function than as a method to override.

## 26_Surrogate.md

- **~9:** The basic idea is simple: from a base class, the surrogate is derived along with the class or classes that provide the actual implementation:
- **~17:** Structurally, the difference between *Proxy* and *State* is simple: a *Proxy* has only one implementation, while *State* has more than one.
- **~17:** The application of the patterns is considered (in *GoF Design Patterns*) to be distinct: *Proxy* is used to control access to its implementation, while *State* allows you to change the implementation dynamically.
- **~95:** The implementation needs no base class: conformance is checked by shape, statically by the type checker, and, with `@runtime_checkable`, by `isinstance()`:

## 27_State_Machines.md

- **~234:** In Python that is no obstacle: define the classes first, then fill in the tables at module level, after all the state objects exist.
- **~364:** Python functions are first-class, so those hierarchies vanish: a condition is any callable returning a `bool`, an action is any callable, and the table is an ordinary `dict`.

## 28_Iterators.md

- **~3:** Code written against an iterator does not care whether the data came from a list, a file, a database cursor, or a computation: it only asks for the next item.
- **~69:** A generator can even be *infinite*: a `while True` loop that yields forever, or `itertools.count()`, produces values on demand with no end.
- **~185:** Both take `expected: type[T]`, so the checker carries the element type through: `typed(items, int)` is an `Iterator[int]`, not an `Iterator[Any]`.

## 29_Factory.md

- **~3:** The effect is the same: adding a new type can cause problems.
- **~98:** This is where a generator is a bit strange: when you call a function that contains a `yield` statement (`yield` is what makes a function a generator), that function actually returns a generator object that has an iterator.
- **~199:** In Python a class is itself a first-class object: you can store it in a variable and call it to make an instance.
- **~240:** Adding a `Triangle` is now a single class definition: it registers itself, and `make()` builds it with no change to the factory.
- **~361:** `ShapeFactory` fills its dictionary lazily: the first request for a kind builds that kind's factory object (via `eval()`) and caches it for later requests.
- **~364:** Because classes are already first-class objects, the registry shown above does the same job: it maps a name straight to a class and constructs it.
- **~375:** The example given in *GoF Design Patterns* implements portability across various graphical user interfaces (GUIs): you create a factory object appropriate to the GUI that you're working with, and from then on when you ask it for a menu, button, slider, etc. it will automatically create the appropriate version of that item for the GUI.
- **~528:** The concrete classes inherit nothing, but the type checker still verifies that each one fits the appropriate `Protocol`: a `GameElementFactory` must supply `make_character()` and `make_obstacle()`, a `Character` must supply `interact_with()`, and an `Obstacle` must supply `action()`.
- **~752:** When construction genuinely is a process: the steps must happen in an order, later steps depend on earlier ones, and rules span the steps.
- **~752:** The standard library's `argparse.ArgumentParser` has the same shape: `add_argument()` calls accumulate a specification, and `parse_args()` is the `build()`.

## 30_Function_Objects.md

- **~7:** So these three patterns are largely unnecessary in Python: where *GoF Design Patterns* builds a hierarchy, Python uses a function.
- **~84:** The class version is four classes and a wrapper to say what one list of functions says directly. *GoF Design Patterns* calls commands "an object-oriented replacement for callbacks." In Python a callback is just a function, so the replacement is unnecessary: the object form earns its keep only when a command must also carry state or support extra operations such as undo.
- **~228:** The `key` argument to `sorted()`, `min()`, and `max()` is a strategy: you provide a function that decides how to compare.

## 31_Changing_the_Interface.md

- **~3:** Sometimes the problem you're solving is as simple as "I don't have the interface that I want." Two of the patterns in *GoF Design Patterns* solve this problem: *Adapter* takes one type and produces an interface to some other type. *Façade* creates an interface to a set of classes, providing a more comfortable way to deal with a library or bundle of resources.
- **~88:** Python is dynamically typed: `WhatIUse.op()` only calls `f()`, so it accepts any object that has an `f()`.
- **~125:** Testing verifies both halves of that behavior: the new `f()` combines the adaptee's methods, and calls to methods it doesn't override forward through to the wrapped object:

## 32_Observer.md

- **~221:** The alarm also shows an observer that can decline to act: below its threshold it returns without sending anything.

## 33_Multiple_Dispatching.md

- **~11:** The answer starts with something you probably don't think about: Python only performs single dispatching.
- **~195:** Notice the flexibility of dictionaries: a tuple can be used as a key just as easily as a single object.

## 34_Visitor.md

- **~99:** The `accept()`/`visit()` pair is the *double dispatch*: `accept()` resolves the flower's type, then `visit()` resolves the visitor's type.
- **~173:** Because each operation is a plain function, testing is direct: call it with each flower type and assert the result.

## 35_Composite_and_Interpreter.md

- **~17:** The payoff is uniformity: you ask a single file for its size the same way you ask a directory holding thousands of them.
- **~132:** The uniformity is unchanged: `disk_usage()` accepts a lone `File`, a subtree, or the whole tree.
- **~178:** The guidance from [Pattern Matching](13_Pattern_Matching.md#when-not-to-match) applies directly: match over a closed set, use polymorphism for an open one.
- **~188:** A tree whose shape follows a grammar is an *abstract syntax tree* (AST). *Interpreter* is Composite applied to language: represent each construct as a node type, and evaluation becomes a tree walk.
- **~242:** The four node classes are the grammar: an expression is a number, a variable, a sum, or a product.
- **~258:** SymPy expressions, `pandas` and Polars column arithmetic, and SQLAlchemy filter conditions all work exactly this way: overloaded operators build an expression tree, and a library interprets that tree later, symbolically, over a whole column, or as SQL.
- **~298:** The second line is the point of interpreting rather than computing: `expr` is a value, so the same tree evaluates under different variable bindings, as many times as you like.
- **~372:** `simplify()` applies algebraic identities: adding zero and multiplying by one vanish, multiplying by zero collapses, and constant subtrees fold into a single `Num`.

## 36_Flyweight.md

- **~47:** Do not write code that depends on them; do notice the technique.) Interned strings make comparison cheap: equal means identical, so `==` collapses to a pointer check.
- **~59:** The tile's position is extrinsic: it is the cell's coordinates in the grid, so the `Tile` object never stores it.
- **~113:** A cell's position never needs storing: asking "is the cell at row 1, column 5 walkable?" is `field[1][5].walkable`, with the coordinates supplied by the asker.
- **~142:** Remove `frozen=True` and the pattern turns on you: mutate the grass tile in one cell and every grass cell in the map changes.
- **~198:** `weakref.WeakValueDictionary` fixes this: it holds its values weakly, so an entry disappears as soon as no one else uses the object:
- **~267:** An `Enum` (introduced in [Data Classes as Types](12_Data_Classes_as_Types.md#enums-are-types-too)) is a flyweight pool the language maintains for you: each member is constructed once, at class creation, and every mention anywhere in the program is that one object.
- **~301:** The customization must happen in `__new__()`: the lookup table behind `Tile(".")` is keyed by the value `__new__()` establishes, so setting `_value_` later, in `__init__()`, would leave that table keyed by the tuples.
- **~301:** With it, `Tile(".")` is a lookup: name, symbol, and attribute access all land on the same shared member.
- **~301:** The trade is fixedness: `tile()` could load `SPECS` from a file, while `Tile.GRASS` is source code.
- **~320:** Column stores such as pandas and Polars offer categorical types: a column of a million country names stores small integer codes into a pool of distinct strings.

## 37_Memento.md

- **~129:** The third test guards the subtle bug: if `restore()` handed the memento's data back by reference, drawing afterward would corrupt the snapshot.
- **~166:** There is no `Memento` class, no `save()`, and no `restore()`, and nothing was copied to protect the past: `after` shares the two original stroke strings with `before`.
- **~257:** `do()` pushes the present into the past and clears the future, because acting after an undo starts a new timeline: the states you undid are no longer reachable by redo, which is how every editor behaves.
- **~299:** The alternative design stores commands instead of states: each undoable action carries its own inverse, the Command variation mentioned in [Function Objects](30_Function_Objects.md).
- **~299:** Snapshot-based undo is the one to try first, because immutable states make it nearly free: each `Sketch` above shares almost all of its strokes with its neighbors in the history.
- **~353:** Add `erase()` to both sketches: it removes the last stroke.
- **~353:** Give `History` a maximum depth: when the past grows beyond `n` states, the oldest is discarded.

## 38_Pattern_Refactoring.md

- **~79:** `sum_value()` is an ordinary function: it relies on polymorphism (`t.value`, `t.weight`) and never asks what type each piece is.
- **~240:** This satisfies the requirement, but it has a classic flaw: it tests for *every type in the system*.

## 39_Simulation.md

- **~20:** The blackboard is a classic coordination technique: independent agents read from and write to one common data structure instead of talking to each other directly.
- **~20:** They take turns instead of running at the same instant, so no lock is needed: a rat is never interrupted partway through an update.
- **~492:** It is `True` only for a type checker reading the file, which is all `Room` is needed for: every use below is an annotation (`room: Room`, `-> Room`), never a runtime lookup.
- **~513:** It searches `Item.__subclasses__()` for a matching `symbol`, so adding a new kind of item needs no change here: define the subclass with its symbol and the factory finds it.
- **~833:** Two patterns from earlier chapters carry the design: polymorphism replaces a type switch, and a factory builds objects from data.

## 40_Functional_Programming.md

- **~69:** Removing shared mutable state is the practical core of the functional style: a value that never changes cannot develop a bug from being changed somewhere you forgot about.
- **~100:** The read-only collection types in `collections.abc`, such as `Sequence` and `Mapping`, describe a value you only read: they have no `append()` or item assignment, so a checker rejects any attempt to mutate through them:
- **~154:** This is what *first-class* means: you can bind a function to a name, store it in a container, pass it as an argument, and return it from another function.
- **~229:** The idea runs the other direction, too: a function that takes a function can wrap it with operations like timing, retries, or logging.
- **~240:** For anything larger, write a `def`: a named function carries a docstring, a readable name in tracebacks, and room to grow.
- **~395:** `lru_cache` is only correct because `fib()` is pure: caching a function with side effects would skip the effects.
- **~455:** A generator is the canonical example: it yields one value at a time instead of building a whole list up front.
- **~541:** That freedom is why a SQL query, a NumPy expression, or a dataframe operation can run on an optimized or parallel engine you never see: you described the what, not a fixed sequence of moves.
- **~613:** This is the [Curry-Howard correspondence](https://en.wikipedia.org/wiki/Curry%E2%80%93Howard_correspondence): types are propositions and programs are their proofs.
- **~678:** What purity changes is the cost: with no mutable state to track, each step of the reasoning is shorter.

**Total: 151 candidates**
