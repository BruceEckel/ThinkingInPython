# Cleanup: Solutions

## 1. Rebinding `counters` instead of clearing it

> In `weak_value.py`, replace the final `counters.clear()` with `counters = []`
> (rebinding the name) and confirm `live_count()` still reaches `0`.
> The two do different things to the list object.
> Say what each one does,
> then say what a second name bound to the same list sees after each.

<details>
<summary>Where to look</summary>

[Watching Objects Without Holding Them](../../Chapters/10_Foundations--Cleanup.md#watching-objects-without-holding-them)
ends with `counters.clear()` dropping the list's references.
Rebinding a name and mutating the object that name references are different operations.
To see the difference,
bind a second name to the same list before you try each form,
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
<summary>Done when</summary>

your edited `weak_value.py` prints `3`, `2`, `1`, `0`,
and a short script that binds a second name to the list prints `[1, 2, 3]` through that name after rebinding and `[]` after `clear()`.
You can then say why `live_count()` would stay at `1` if that second name existed.

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
counters.pop()  # Release "Third"
print(Counter.live_count())
#: 2
counters.pop()  # Release "Second"
print(Counter.live_count())
#: 1
counters = []  # Rebind the name instead of calling .clear()
print(Counter.live_count())
#: 0
```

**Abandon the old list.**
`counters.clear()` empties the existing list in place,
dropping its reference to the last `Counter` object.
`counters = []` points the name `counters` at a new,
empty list and drops the name's reference to the old one.
Here the name `counters` held the old list's sole reference,
so CPython frees that list at once.
Freeing the list drops its reference to the one remaining `Counter`.
Both forms reach `live_count() == 0`.

The two forms give different results when a second name refers to the list:

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

**Look through a second name.**
`clear()` changes the object to which every name refers.
Rebinding points `counters` at a different object,
and every other name still refers to the old list.
The two forms give the same result in `weak_value.py` because that list has a single reference.
With two references, rebinding leaves the last `Counter` object alive,
and `live_count()` still returns `1`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Listing the names of every live instance

> In `weak_value.py`, add a classmethod `live_names()` to `Counter` that returns a sorted list of the `.name` of every live instance,
> by reading `cls._instances.values()`.

<details>
<summary>Where to look</summary>

In [Watching Objects Without Holding Them](../../Chapters/10_Foundations--Cleanup.md#watching-objects-without-holding-them),
a `WeakValueDictionary` reads like a `dict`.
Iterate over `cls._instances.values()` in a `@classmethod`, take each `.name`,
and wrap the result in `sorted()` so the order follows the names, not insertion.

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
<summary>Done when</summary>

creating `Counter` objects named `"Charlie"`, `"Alpha"`, and `"Bravo"`,
in that order, and printing `Counter.live_names()` gives `['Alpha', 'Bravo', 'Charlie']`,
not the creation order, and `uv run ty check` passes on your file.

<details>
<summary>Solution</summary>

If you return `[c.name for c in cls._instances.values()]` without `sorted()`,
the demo prints `['Charlie', 'Alpha', 'Bravo']`,
the order in which the demo created the instances.
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

**Gather the live names.**
A `WeakValueDictionary` reads like a `dict`,
so `cls._instances.values()` yields the live `Counter` objects it currently tracks.
Iterating over a dictionary follows insertion order,
which is the creation order,
so the names need `sorted()` to come out in alphabetical order.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. Building the `list` with a comprehension instead of a loop

> In `cleanup.py`, change the loop to build `counters` with a list comprehension instead of `append()` in a `for` loop,
> and confirm the output stays the same:
> no object goes away before `End of delete loop` prints.

<details>
<summary>Where to look</summary>

[Why `__del__()` Is Not Cleanup](../../Chapters/10_Foundations--Cleanup.md#why-del-is-not-cleanup)
explains why an object survives `del c` while the list still references it.
A list comprehension builds the same list,
so ask what still holds each `Counter` during the loop.
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
```

<details>
<summary>Done when</summary>

your `cleanup.py` prints the same five lines the chapter's version prints,
ending with `3` and `End of delete loop`,
and the three `deleted` lines appear only after `End of delete loop`,
when you run the file as a script.

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
        Counter.count -= 1
        print(self.name, "deleted,", Counter.count, "left")

counters = [Counter(name)
            for name in ["First", "Second", "Third"]]
#: First created
#: Second created
#: Third created

for c in counters:
    del c
print(Counter.count)
#: 3
print("End of delete loop")
#: End of delete loop
```

**Build the same list.**
The output is identical to the original version,
which calls `append()` in a `for` loop.
The resulting list again holds the only references to those three objects.

**Drop the loop variable's reference.**
`del c` inside the loop unbinds the name `c` and leaves the list alone.
However you build the list,
it keeps its contents alive until interpreter shutdown.
The `deleted` messages therefore appear there, as before,
after `End of delete loop` has printed.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. A strong registry that never lets go

> In `weak_value.py`, change `_instances` from a `WeakValueDictionary` to a `dict[int, Counter]` and run the file again.
> Report what `live_count()` prints after each `pop()`,
> and explain the difference in terms of what each container holds.

<details>
<summary>Where to look</summary>

[Watching Objects Without Holding Them](../../Chapters/10_Foundations--Cleanup.md#watching-objects-without-holding-them)
uses a `WeakValueDictionary` so the registry holds its values weakly.
A plain `dict` stores strong references.
After each `pop()`, ask how many references to the `Counter` remain and what holds them.

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
<summary>Done when</summary>

your edited `weak_value.py` prints `3` four times,
after each `pop()` and after `clear()`,
and you can say which container holds the reference that keeps each `Counter` alive.

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

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))

print(Counter.live_count())
#: 3
counters.pop()  # Release "Third"
print(Counter.live_count())
#: 3
counters.pop()  # Release "Second"
print(Counter.live_count())
#: 3
counters.clear()  # Release "First"
print(Counter.live_count())
#: 3
```

**Register each instance strongly.**
A `dict` holds a strong reference to each value,
so `_instances` alone keeps every `Counter` alive, whatever `counters` does.
`pop()` removes the list's reference.
The registry keeps its own,
so the `Counter`'s reference count stays above zero and the `Counter` survives.

The registry now leaks every `Counter` it tracks.
`live_count()` reports how many `Counter` objects the program has created,
because the registry keeps them all alive.
A `WeakValueDictionary` holds its values weakly,
so it counts the objects and leaves their lifetimes as they were.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. `finalize(self, self.close)` and what it keeps alive

> In `finalizer.py`, change the `finalize()` call to `finalize(self, self.close)`,
> make `close()` print `self.name, "closed"` instead of invoking the finalizer,
> and call `a.finalizer()` where the file now calls `a.close()`.
> Run it again.
> Report when `B closed` now prints relative to `End of program`,
> and say what keeps the `Connection` alive.

<details>
<summary>Where to look</summary>

[The `self.close` Trap](../../Chapters/10_Foundations--Cleanup.md#the-self-close-trap)
shows why a callback must carry what it needs, such as a name,
rather than the object whose collection triggers it.
`self.close` is a bound method, so ask what a bound method stores.
Then ask what holds the callback,
and what that means for the reference count when you `del b`.

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
<summary>Done when</summary>

running your file as a script prints `End of program` and then `B closed` as its last line,
where the chapter's `finalizer.py` prints `B closed` at the `del b`.
You can name the object that still references the `Connection` after `del b`,
and the mechanism that runs the callback at shutdown.

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.finalizer = finalize(self, self.close)

    def close(self) -> None:
        print(self.name, "closed")

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.finalizer()
#: A closed
a.finalizer()
print(a.finalizer.alive, b.finalizer.alive)
#: False True
del b
print("End of program")
#: End of program
```

Run as a standalone script, the program prints:

```text
A opened
B opened
A closed
False True
End of program
B closed
```

The listing's markers end at `End of program` because `B closed` prints during interpreter shutdown,
after the book's output checker has finished capturing.

`B closed` now prints after `End of program`,
where the chapter's version prints it at the `del b`.
The rest of the output matches the chapter's output,
so the mistake is hard to see.
The callback still runs, at a different time and for a different reason.

**Register the cleanup callback.**
The callback keeps the `Connection` alive.
`self.close` is a bound method,
and a bound method holds a strong reference to its instance.
`finalize()` stores the callback,
so the finalizer registry now holds a reference to the `Connection` whose collection triggers the finalizer.
`del b` drops the program's last reference, but the registry still holds one,
so the `Connection` survives.

`B closed` prints only because `finalize()`'s `atexit` backstop runs every still-alive finalizer as the interpreter shuts down,
the backstop the chapter describes.
Here it runs the callback for an object that `del b` should have destroyed.

The chapter's `finalize(self, print, name, "closed")` avoids the trap by passing the pieces the callback needs rather than the `Connection`.
`name` is a `str` the `Connection` also holds.
The finalizer's reference to `name` keeps a string alive, not a connection.
The rule holds for any finalizer:
its callback and arguments may reference any object except the finalizer's own object,
directly or through a chain of references.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. A two-object cycle, with and without the collector

> In `cycle.py`, change `self_link()` to build a two-object cycle
> (`a.peer = b` and `b.peer = a`) instead of a self-reference.
> Confirm both `__del__()` methods run at `gc.collect()`,
> then remove the `gc.disable()`/`gc.enable()` pair and explain why the language no longer guarantees when the two `finalized` lines appear,
> although this small program still prints them in the same place every run.

<details>
<summary>Where to look</summary>

[Reference Cycles Delay Destruction](../../Chapters/10_Foundations--Cleanup.md#reference-cycles-delay-destruction)
shows `__del__()` running only when `gc.collect()` reclaims a cycle.
Give each of two `Node` objects a `peer` attribute pointing at the other.
For the second part,
consider what triggers an automatic pass of the cycle collector,
and what your call to `gc.collect()` still decides.

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
<summary>Done when</summary>

your `cycle.py` prints `a finalized` and `b finalized` between `unreachable, but still alive` and `after collect`.
You can say what makes the collector run once `gc.disable()` is gone,
and why the `gc.collect()` call still keeps this run's transcript the same.

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

**Form a two-object cycle.**
A cycle through two objects behaves like the self-reference in `cycle.py`,
which is the smallest cycle.
Reference counting cannot reclaim either object, because each holds the other.
The cycle collector reclaims both together when it runs.

**Let the collector run on its own.**
Removing the `gc.disable()`/`gc.enable()` pair takes away the guarantee about when the finalizers run.
The collector then also runs on its own schedule,
triggered by allocation counts,
so an automatic pass can in principle reclaim the cycle at any allocation after `self_link()` returns.
This small program still prints the same transcript every run,
because the explicit `gc.collect()` runs before the program has allocated enough objects to start an automatic pass,
so that call sets the moment of collection.
While that call is there,
the two `finalized` lines print at that call or earlier.

The chapter's listing calls `gc.disable()` to get a deterministic transcript for a demonstration about unpredictable timing.
The call is a device for the demonstration, not advice,
so the listing turns the collector back on right after `gc.collect()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[An `__init__()` That Fails Leaks the Resource](../../Chapters/10_Foundations--Cleanup.md#raising-init-leaks)
shows a failure before the object is usable.
[An Explicit `close()` and a `with` Block](../../Chapters/10_Foundations--Cleanup.md#an-explicit-close-and-a-with-block)
describes when `with` calls `__exit__()`.
The `with` statement calls `__exit__()` only after `__enter__()` returns.
So release the resource inside `__enter__()`: catch the exception there,
release, and re-raise it with a bare `raise`.

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
<summary>Done when</summary>

the unguarded version prints `C opened` then `caught boom`,
with no `closed` line, and the guarded version prints `C opened`, `C closed`,
`caught boom`, with `C closed` printed once.
`uv run ty check` passes on your file.

<details>
<summary>Solution</summary>

If you leave out the bare `raise`, the `except` clause swallows the exception.
The `Guarded` demo then prints `C closed` twice and omits `caught boom`.
`__enter__()` returns `None` instead of failing,
so the `with` block runs as though the acquisition succeeded,
and `__exit__()` releases the resource a second time.
The type checker (`ty`) reports that version as `invalid-return-type`,
since `__enter__()` now always implicitly returns `None` where its annotation declares `Guarded`.
The solution re-raises the exception,
so the caller sees `boom` and the `closed` line prints once.

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

**Acquire the resource on entry.**
Moving the acquisition from `__init__()` to `__enter__()` moves the leak with it.
The `with` statement calls `__exit__()` only for a block it has entered,
and it enters the block only after `__enter__()` returns.
An `__enter__()` that fails has not returned, so `__exit__()` does not run.

**Release before re-raising the exception.**
`__exit__()` runs in neither class, yet `Guarded` releases the resource,
in the method that acquired it.

Acquiring in `__enter__()` still helps.
If `Guarded.__init__()` fails for some other reason,
the failure comes before `__enter__()` acquires the resource.
Moving the acquisition leaves the guard just as necessary, though.
Whichever method acquires a resource,
a step that can fail after the acquisition must release the resource before the exception propagates.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
