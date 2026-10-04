# Cleanup: Solutions

## 1. Rebinding `counters` instead of clearing it

> In `weak_value.py`, replace the final `counters.clear()` with `counters = []`
> (rebinding the name) and confirm `live_count()` still reaches `0`.
> The two do different things to the list object.
> Say what each one does,
> then say what a second name bound to the same list sees after each.

<details>
<summary>Where to look</summary>

[Watching Objects Without Holding Them](../../Chapters/10_Foundations--Cleanup.md#watching-objects-without-holding-them) ends with `counters.clear()` dropping the list's references.
Rebinding a name and mutating the object that name references are different operations.
To see the difference, bind a second name to the same list before you try each form,
then print that second name.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import ClassVar
from weakref import WeakValueDictionary

class Counter:
    _instances: ClassVar[
        WeakValueDictionary[int, Counter]
    ] = WeakValueDictionary()

    def __init__(self, name: str) -> None:
        ...

    @classmethod
    def live_count(cls) -> int:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from typing import ClassVar
from weakref import WeakValueDictionary

class Counter:
    _instances: ClassVar[
        WeakValueDictionary[int, Counter]
    ] = WeakValueDictionary()

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_count(cls) -> int:
        return len(cls._instances)

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))

print(Counter.live_count())
#: 3
counters = []  # Rebind the name instead of calling .clear()
print(Counter.live_count())
#: 0
```

**Abandon the old list.** `counters.clear()` empties the existing list in place, dropping its
references to all three `Counter` objects. `counters = []` does
something different: it points the name `counters` at a brand-new,
empty list and abandons the old one. Here nothing else refers to that
old list, so it (and every reference it held) becomes collectible
immediately, and both forms reach `live_count() == 0`.

The two forms stop agreeing once a second name refers to the list:

```python
# exercise_1_alias.py
counters = [1, 2, 3]
other = counters  # A second name for the same list
counters = []  # Rebinding: 'other' still sees the old list
print(other)
#: [1, 2, 3]
counters = [1, 2, 3]
other = counters
counters.clear()  # Clearing: 'other' sees the emptied list
print(other)
#: []
```

**Look through a second name.** `clear()` changes the object every
name can see. Rebinding points this one name at a different object,
and every other name keeps the old one. The two coincide in
`weak_value.py` because that list has exactly one reference. With two references, rebinding leaves the
`Counter` objects alive and `live_count()` stuck at `3`.

</details>
</details>
</details>

## 2. Listing the names of every live instance

> In `weak_value.py`, add a classmethod `live_names()` to `Counter` that returns a sorted list of the `.name` of every live instance,
> by reading `cls._instances.values()`.

<details>
<summary>Where to look</summary>

In [Watching Objects Without Holding Them](../../Chapters/10_Foundations--Cleanup.md#watching-objects-without-holding-them), a `WeakValueDictionary` reads like a `dict`.
Iterate `cls._instances.values()` in a `@classmethod`, take each `.name`,
and wrap the result in `sorted()` so the order does not depend on insertion.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from typing import ClassVar
from weakref import WeakValueDictionary

class Counter:
    _instances: ClassVar[
        WeakValueDictionary[int, Counter]
    ] = WeakValueDictionary()

    def __init__(self, name: str) -> None:
        ...

    @classmethod
    def live_names(cls) -> list[str]:
        ...
```

<details>
<summary>Solution</summary>

If you return `[c.name for c in cls._instances.values()]` without `sorted()`,
the demo prints `['Charlie', 'Alpha', 'Bravo']`, the order in which the demo created the instances.
The type checker accepts that version, since the result is still a `list[str]`,
so the output alone shows the mistake.
The solution sorts, so the list depends on which names are live and not on when the program created each instance.

```python
# exercise_2.py
from typing import ClassVar
from weakref import WeakValueDictionary

class Counter:
    _instances: ClassVar[
        WeakValueDictionary[int, Counter]
    ] = WeakValueDictionary()

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_names(cls) -> list[str]:
        return sorted(c.name
                      for c in cls._instances.values())

counters = [Counter(name)
            for name in ("Charlie", "Alpha", "Bravo")]
print(Counter.live_names())
#: ['Alpha', 'Bravo', 'Charlie']
```

**Gather the live names.** `cls._instances.values()` iterates the live `Counter` objects
currently tracked, since a `WeakValueDictionary` reads like a normal
`dict`. The generator expression pulls out each one's `.name`. Sorting
makes the result independent of creation order, since a dictionary's
iteration order here follows insertion, not name order.

</details>
</details>
</details>

## 3. Building the `list` with a comprehension instead of a loop

> In `cleanup.py`, change the loop to build `counters` with a list comprehension instead of `append()` in a `for` loop,
> and confirm the output stays the same:
> no object goes away before `End of delete loop` prints.

<details>
<summary>Where to look</summary>

[Why `__del__()` Is Not Cleanup](../../Chapters/10_Foundations--Cleanup.md#why-del-is-not-cleanup) explains why `del c` does not destroy an object while the list still references it.
A list comprehension builds the same list, so ask what still holds each `Counter` during the loop.
Compare the order of the output lines with the original listing.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import ClassVar

class Counter:
    count: ClassVar[int] = 0

    def __init__(self, name: str) -> None:
        ...

    def __del__(self) -> None:
        ...

    def __repr__(self) -> str:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_3.py
from typing import ClassVar

class Counter:
    count: ClassVar[int] = 0

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "created")
        Counter.count += 1

    def __del__(self) -> None:
        print(self.name, "deleted")
        Counter.count -= 1
        if Counter.count == 0:
            print("Last Counter object deleted")
        else:
            print(Counter.count,
                  "Counter objects remaining")

    def __repr__(self) -> str:
        return f"Counter({self.name!r} {self.count})"

counters = [Counter(name)
            for name in ["First", "Second", "Third"]]
#: First created
#: Second created
#: Third created

for c in counters:
    print(c)
    del c
#: Counter('First' 3)
#: Counter('Second' 3)
#: Counter('Third' 3)
print("End of delete loop")
#: End of delete loop
```

**Build the same list.** The output is identical to the original `for`-loop-with-`append()`
version. A comprehension calls `Counter(name)` once per name, in
order, and the resulting list is again the only thing holding
references to those three objects.

**Drop the loop variable's reference.** `del c` inside the loop unbinds the
name `c` and leaves the list alone. How you build the list does
not change when Python destroys its contents, so the `deleted` messages
appear, as before, at interpreter shutdown, after `End of delete loop`
has printed.

</details>
</details>
</details>

## 4. A strong registry that never lets go

> In `weak_value.py`, change `_instances` from a `WeakValueDictionary` to a `dict[int, Counter]` and run the file again.
> Report what `live_count()` prints after each `pop()`,
> and explain the difference in terms of what each container holds.

<details>
<summary>Where to look</summary>

[Watching Objects Without Holding Them](../../Chapters/10_Foundations--Cleanup.md#watching-objects-without-holding-them) uses a `WeakValueDictionary` so the registry does not count as a reference.
A plain `dict` stores strong references.
After each `pop()`, ask how many references to the `Counter` remain and who owns them.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from typing import ClassVar

class Counter:
    _instances: ClassVar[dict[int, Counter]] = {}

    def __init__(self, name: str) -> None:
        ...

    @classmethod
    def live_count(cls) -> int:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from typing import ClassVar

class Counter:
    _instances: ClassVar[dict[int, Counter]] = {}

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self

    @classmethod
    def live_count(cls) -> int:
        return len(cls._instances)

counters = [Counter(name)
            for name in ("First", "Second", "Third")]
print(Counter.live_count())
#: 3
counters.pop()
print(Counter.live_count())
#: 3
counters.pop()
print(Counter.live_count())
#: 3
counters.clear()
print(Counter.live_count())
#: 3
```

**Register each instance strongly.** The count stays at three. A `dict` holds a strong reference to each
value, so `_instances` alone keeps every `Counter` alive no matter
what `counters` does. `pop()` removes one reference and the registry
keeps another, so the object's reference count stays above zero and
the object survives.

The registry has become the leak it exists to catch: `live_count()`
now reports how many `Counter` objects the program has created,
because the registry keeps them all alive. A
`WeakValueDictionary` holds its values weakly, so it can answer the
question without changing the answer.

</details>
</details>
</details>

## 5. `finalize(self, self.close)` and what it keeps alive

> In `finalizer.py`, change the `finalize()` call to `finalize(self, self.close)`,
> make `close()` print `self.name, "closed"` instead of invoking the finalizer,
> and call `a.closer()` where the file now calls `a.close()`.
> Run it again.
> Report when `B closed` now prints relative to `End of program`,
> and say what keeps the `Connection` alive.

<details>
<summary>Where to look</summary>

[The `self.close` Trap](../../Chapters/10_Foundations--Cleanup.md#the-self-close-trap) shows why a callback must not lead back to the object whose death triggers it.
`self.close` is a bound method, so ask what a bound method stores.
Then ask who holds the callback, and what that means for the reference count when you `del b`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        ...

    def close(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.closer = finalize(self, self.close)

    def close(self) -> None:
        print(self.name, "closed")

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.closer()
#: A closed
a.closer()
print(a.closer.alive, b.closer.alive)
#: False True
del b
print("End of program")
#: End of program
```

Run directly, the whole output is:

```text
A opened
B opened
A closed
False True
End of program
B closed
```

`B closed` now prints *after* `End of program`, where the chapter's
version prints it at the `del b`. The listing has no marker for it
because the line arrives during interpreter shutdown, after the book's
output checker has stopped capturing. That late arrival demonstrates
the point in its own right. The rest of the output matches the
chapter's, so the mistake is hard to see: the callback still
runs, at a different time and for a different reason.

**Register the cleanup callback.** The callback keeps the `Connection` alive. `self.close`
is a bound method, and a bound method holds a strong reference to
its instance. `finalize()` stores the callback, so the finalizer
registry now holds a reference to the `Connection` for whose death
the finalizer waits. `del b` drops the last reference the program
has, but not the last reference that exists, so the object survives.

`B closed` prints only because `finalize()`'s `atexit` backstop runs
every still-alive finalizer as the interpreter shuts down. That
backstop is the fallback the chapter describes, doing its job
on an object that `del b` should have destroyed.

The chapter's `finalize(self, print, name, "closed")` avoids the trap
by passing the pieces the callback needs rather than the object that
has them. `name` is a `str` the `Connection` also holds. The
finalizer's reference to `name` keeps a string alive, not a connection.
The rule generalizes: a finalizer may capture anything except a path
back to its own object.

</details>
</details>
</details>

## 6. A two-object cycle, with and without the collector

> In `cycle.py`, change `self_link()` to build a two-object cycle
> (`a.peer = b` and `b.peer = a`) instead of a self-reference.
> Confirm both finalizers run at `gc.collect()`,
> then remove the `gc.disable()`/`gc.enable()` pair and explain why the language no longer guarantees when the two `finalized` lines appear,
> although this small program still prints them in the same place every run.

<details>
<summary>Where to look</summary>

[Reference Cycles Delay Destruction](../../Chapters/10_Foundations--Cleanup.md#reference-cycles-delay-destruction) shows `__del__()` running only when `gc.collect()` reclaims a cycle.
Give each of two `Node` objects a `peer` attribute pointing at the other.
For the second part, consider what triggers the cycle collector when you do not call it, and what your explicit call to `gc.collect()` still fixes.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
import gc

class Node:
    peer: Node

    def __init__(self, name: str) -> None:
        ...

    def __del__(self) -> None:
        ...

def self_link() -> None:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_6.py
import gc

class Node:
    peer: Node

    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        print(self.name, "finalized")

def self_link() -> None:
    a, b = Node("a"), Node("b")
    a.peer = b
    b.peer = a

gc.disable()
self_link()
print("unreachable, but still alive")
#: unreachable, but still alive
gc.collect()
#: a finalized
#: b finalized
gc.enable()
print("after collect")
#: after collect
```

**Form a two-object cycle.** Both finalizers run at `gc.collect()`, in creation order. The
principle is the same as in `cycle.py`. Reference counting cannot reclaim
either object, because each holds the other. The cycle collector
reclaims both together when it runs. A cycle through two objects
behaves like a cycle through one. The self-reference in
`cycle.py` is the smallest case.

**Pause the automatic collector.** Removing the `gc.disable()`/`gc.enable()` pair takes away the
guarantee about when the finalizers run. The collector is then free to
run on its own schedule, triggered by allocation counts rather than by
your call, so an automatic pass could in principle reclaim the cycle at
any allocation after `self_link()` returns. This small program still
prints the same transcript every run, because the explicit
`gc.collect()` stays in the listing and sets the moment of collection.
While that call is there, the two `finalized` lines cannot drift past
it or wait until the interpreter shuts down. The loss is in the
guarantee, not in what this run prints.

`gc.disable()` is in the chapter's listing only to keep the output
predictable. It is not advice. It produces a deterministic transcript
for a demonstration whose entire subject is the absence of
determinism, so the listing turns the collector back on immediately
afterward.

</details>
</details>
</details>

## 7. An `__enter__()` that fails, unguarded and guarded

> In `faulty_init.py`,
> move the `print()` and the `raise` from `__init__()` into `__enter__()`,
> in place of its `return self`.
> Run it and report whether `C closed` prints.
> Then wrap the `raise` in a `try`/`except` that prints the `closed` line before re-raising the exception,
> and confirm `C opened` now has its matching `closed`.

<details>
<summary>Where to look</summary>

[An `__init__()` That Fails Leaks the Resource](../../Chapters/10_Foundations--Cleanup.md#raising-init-leaks) shows a failure before the object is usable, and [An Explicit `close()` and a `with` Block](../../Chapters/10_Foundations--Cleanup.md#an-explicit-close-and-a-with-block) describes when `with` calls `__exit__()`.
The `with` statement calls `__exit__()` only after `__enter__()` returns.
To release the resource without `__exit__()`, catch the exception inside `__enter__()`, release there, and use a bare `raise` to re-raise it.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
class Faulty:
    def __init__(self, name: str) -> None:
        ...

    def __enter__(self) -> Faulty:
        ...

    def __exit__(self, *exc: object) -> None:
        ...

class Guarded:
    def __init__(self, name: str) -> None:
        ...

    def __enter__(self) -> Guarded:
        ...

    def __exit__(self, *exc: object) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you leave out the bare `raise`, the `except` clause swallows the exception,
and the `Guarded` demo prints `C closed` twice and no `caught boom`.
`__enter__()` returns `None` instead of failing,
so the `with` block runs as though the acquisition succeeded,
and `__exit__()` releases the resource a second time.
`ty` reports that version as `invalid-return-type`,
since the method now always implicitly returns `None` where its annotation declares `Guarded`.
The solution re-raises the exception, so the caller sees `boom` and the `closed` line prints once.

```python
# exercise_7.py

class Faulty:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> Faulty:
        print(self.name, "opened")
        raise RuntimeError("boom")

    def __exit__(self, *exc: object) -> None:
        print(self.name, "closed")

class Guarded:
    def __init__(self, name: str) -> None:
        self.name = name

    def __enter__(self) -> Guarded:
        print(self.name, "opened")
        try:
            raise RuntimeError("boom")
        except RuntimeError:
            print(self.name, "closed")
            raise

    def __exit__(self, *exc: object) -> None:
        print(self.name, "closed")

try:
    with Faulty("C"):
        pass
except RuntimeError as e:
    print("caught", e)
#: C opened
#: caught boom
try:
    with Guarded("C"):
        pass
except RuntimeError as e:
    print("caught", e)
#: C opened
#: C closed
#: caught boom
```

**Acquire the resource on entry.** `C closed` does not print for `Faulty`. Moving the acquisition from
`__init__()` to `__enter__()` moves the leak with it. The `with`
statement calls `__exit__()` only for a block it has entered, and it
enters the block only after `__enter__()` returns. An `__enter__()`
that fails has not returned, so `__exit__()` does not run.

**Release before re-raising.** `Guarded` releases the resource in the method that acquired it. Its
`except` clause prints the `closed` line and then re-raises the
exception with a bare `raise`, so the caller still sees `boom`.
`__exit__()` runs in neither class, yet `Guarded` releases the
resource.

Acquiring in `__enter__()` still helps: a `Guarded` whose `__init__()`
fails for some other reason holds no resource at that point. That move
does not remove the need for the guard. Whichever method acquires a
resource, a step that can fail after the acquisition releases the
resource before it lets the exception go.

</details>
</details>
</details>
