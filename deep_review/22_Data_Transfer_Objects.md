# Deep review: 22_Data_Transfer_Objects.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Connect `typing.NamedTuple` to the `namedtuple()` taught in chapter 3

**Kind:** teaching
**Where:** section "The Standard-Library Versions", at the `NamedTuple` introduction (line ~89)

**Problem:** [Containers](03_Containers.md#namedtuple) teaches `collections.namedtuple` with the functional call form (`Person = namedtuple("Person", ["name", "age", "height"])`) and closes by steering the reader to data classes for annotations, never mentioning that `typing.NamedTuple` exists. Chapter 22 then introduces `class Color(NamedTuple)` as if it were a new construct. A book-wide grep confirms the two forms are never contrasted anywhere. A reader who remembers chapter 3 either thinks these are unrelated types or writes the functional form here and loses the field types; a reader who does not remember it meets `NamedTuple` twice under two names.

**Proposal:** Add two sentences after "A `NamedTuple` declares its fields the same way but produces an immutable record." (line ~89), before the "Because it is a tuple underneath" sentence:

> `typing.NamedTuple` is the class form of the `namedtuple()` in [Containers](03_Containers.md#namedtuple).
> Both build a subclass of `tuple` whose positions also have names,
> but the class form declares a type for each field,
> so a checker knows `Color.r` is an `int` while the functional form leaves it unknown.

Verified: `class Color(NamedTuple)` has `__bases__ == (tuple,)`, the same as the functional form's result.

**Cost:** none. Adds one cross-reference; `03_Containers.md#namedtuple` follows the same backtick-heading slug pattern as the working `03_Containers.md#deque` link in chapter 18.

---

## 2. Say that this immutability is shallow

**Kind:** teaching
**Where:** section "The Standard-Library Versions" (line ~114), or the closing selection rule (line ~120)

**Problem:** The chapter calls a `NamedTuple` "an immutable record" and says "the fields cannot be mutated," with no qualifier. Its own first listing puts a list in a message bag (`b=["x", "y"]`), so a reader has every reason to put one in a `NamedTuple` next. `Bag(NamedTuple).items.append(999)` works, and the record is also silently unhashable, which contradicts what a reader takes "immutable" to mean. [Rethinking Objects](20_Rethinking_Objects.md) demonstrates the identical leak for `frozen=True` in `frozen_leaky.py`, but nothing here points at it, so the chapter relies on a lesson the reader may not connect.

**Proposal:** Add after "Since the fields cannot be mutated, `_replace()` produces an updated copy." (line ~114):

> The guarantee reaches the fields, not the objects they refer to.
> A `NamedTuple` holding a list still lets that list be changed,
> and the record is then unhashable, the same leak
> [`frozen=True` has](20_Rethinking_Objects.md#the-immutability-solution).
> An immutable record needs immutable fields.

Verified: `Bag(items=[1, 2])` accepts `bag.items.append(999)`; `hash(bag)` raises `TypeError: unhashable type: 'list'`; rebinding `bag.items` raises `AttributeError: can't set attribute`. The anchor points at chapter 20's "The Immutability Solution" section, which is where `frozen_leaky.py` sits.

Alternative: demonstrate it with a four-line listing instead of asserting it. That teaches harder but costs a new extracted file in a chapter whose point is the selection rule, not immutability mechanics.

**Cost:** one new outbound cross-reference. Ties the 20 → 22 frozen-is-shallow thread together explicitly, which it currently is not.

---

## 3. Show what `SimpleNamespace` gives you that the hand-rolled `Messenger` does not

**Kind:** teaching
**Where:** section "The Standard-Library Versions", listing `display_namespace.py` (line ~53)

**Problem:** The listing is deliberately built to mirror `messenger_idiom.py`, printing `vars(m)` both times, so the two look interchangeable. Then the chapter tells the reader to "write the hand-rolled `Messenger` only to show how `SimpleNamespace` works underneath" without ever showing what the stdlib version buys. It buys two things the listing hides: `print(m)` on a `SimpleNamespace` gives `namespace(info='Spam', b=['x', 'y'], more=11)`, while the hand-rolled one gives `<Messenger object at 0x...>`, and two namespaces with the same attributes compare equal, while two `Messenger`s never do. Those are the reasons to prefer it, and the reader is asked to take them on faith.

**Proposal:** Replace the second `print(vars(m))` with a repr print and add an equality line, then explain in prose. Verified output:

```python
# display_namespace.py
from types import SimpleNamespace

m = SimpleNamespace(info="Spam", b=["x", "y"])
print(vars(m))
#: {'info': 'Spam', 'b': ['x', 'y']}
m.more = 11
print(m)
#: namespace(info='Spam', b=['x', 'y'], more=11)
print(m == SimpleNamespace(info="Spam", b=["x", "y"], more=11))
#: True
```

Prose to add after it, before "A `SimpleNamespace` also accepts any name you invent":

> The first `print()` shows the same instance `__dict__` the hand-rolled version had.
> The rest is what `SimpleNamespace` adds:
> a readable `repr()` and equality by contents.
> `Messenger` prints as `<Messenger object at 0x...>`,
> and two `Messenger`s with identical attributes compare unequal,
> because it inherits `object`'s identity-based equality.

**Cost:** the listing's second `#:` marker changes, so this needs the usual sync and marker refresh. Exercise 4 works on this listing and still does; its solution builds its own namespaces and is unaffected.

---

## 4. Explain why the `SimpleNamespace` listing needs no `m: Any`

**Kind:** teaching
**Where:** section "The Standard-Library Versions" (line ~65)

**Problem:** The chapter spends five careful lines on why `messenger_idiom.py` cannot type-check without `m: Any`, then shows a listing that does the same three unchecked things with no annotation at all and passes the gate. A reader who noticed the first explanation will read the second listing as contradicting it. The answer is that the typeshed stub for `SimpleNamespace` types every attribute as `Any`, so the checker is off there too, just without a visible annotation. Verified with `ty`: `reveal_type(m.info)` and `reveal_type(m.nope)` both report `Any`, and reading a name that was never set draws no diagnostic.

**Proposal:** Extend the existing sentence at line ~65:

> A `SimpleNamespace` also accepts any name you invent,
> so no checker can know which names to expect.
> Its type declaration says so: reading any attribute yields `Any`,
> which is why this listing needs no annotation to type-check
> and why `m.inof` goes unreported here as well.

**Cost:** none. This is the chapter's end of the load-bearing-`Any` bargain that [Visitor](33_Visitor.md) cites, and stating it twice makes the bargain the reader is being sold explicit.

---

## 5. Warn that a dataclass return value does not unpack

**Kind:** teaching
**Where:** section "Returning Multiple Values" (line ~149)

**Problem:** The section's payoff line is "because a `NamedTuple` is a tuple, you can unpack it," and the listing's comment says "Unpacks like a tuple." A reader who prefers the `@dataclass` shown two pages earlier will write `mean, count = summarize(...)` against it and get `TypeError: cannot unpack non-iterable Stats object`. The chapter's own closing rule ("Choose `NamedTuple` when tuple behavior is the goal: unpacking") states the criterion but never shows the failure it protects against, so a reader has no reason to believe the choice matters.

**Proposal:** Add after "and because a `NamedTuple` is a tuple, you can unpack it." (line ~153):

> A data class cannot do that last part.
> `mean, count = summarize(data)` against a `@dataclass` version of `Stats`
> raises a `TypeError`, since a data class is not iterable.
> `dataclasses.astuple()` converts one when you need the positional form.

Verified: the `TypeError` message is "cannot unpack non-iterable Point object"; `astuple(P(1.0, 2.0))` gives `(1.0, 2.0)`.

**Cost:** none. It introduces `astuple()`, which the book does not otherwise mention; drop that sentence if you would rather not.

---

## 6. Point `_replace()` at the general `copy.replace()`

**Kind:** teaching
**Where:** section "The Standard-Library Versions" (line ~114)

**Problem:** The chapter shows `_replace()` as the way to get an updated copy of an immutable record, then closes by recommending a frozen data class for records that should be a distinct type. A reader following that recommendation has no copy-with-changes method: `_replace()` is a `NamedTuple` member. [Data Classes as Types](12_Data_Classes_as_Types.md#the-general-form-of-replace) already teaches `copy.replace()` and shows it working on a frozen data class, a `NamedTuple`, and a `datetime`, so the answer exists eleven chapters earlier and is not connected here.

**Proposal:** Append to the `_replace()` sentence at line ~114:

> `copy.replace()` from [The General Form of `replace()`](12_Data_Classes_as_Types.md#the-general-form-of-replace)
> does the same job for any immutable record, including a frozen data class.

**Cost:** none. Adds a third outbound link to chapter 12.

---

## 7. Name `TypedDict` where the chapter dismisses dictionaries

**Kind:** teaching
**Where:** intro (line ~7)

**Problem:** The chapter opens by rejecting `dict` on syntax grounds ("the clumsier `d["name"]` syntax") and never returns to it. A reader whose data has to stay a dict, which is the normal case at a JSON or API boundary, is left thinking the book has nothing for them. `TypedDict` names the keys and their value types for a checker while the object stays a real dict at run time. It appears in the book once, as a row in chapter 8's reference table, with no chapter to send the reader to.

**Proposal:** Add to the closing selection rule (line ~120), after the three-way recommendation:

> When the data must stay a dict, because it arrives as JSON or goes back out as JSON,
> a `TypedDict` from [Static Typing](08_Static_Typing.md#dictionary-and-record-shapes)
> names the keys and their types for the checker while the value stays a real dict.

**Cost:** the anchor resolves: `heading_links.py` strips the raw `<a href>` tags before slugging, so chapter 8's "Dictionary and record shapes" heading yields `#dictionary-and-record-shapes`. The real cost is scope, since this widens the chapter by one construct it otherwise never mentions. Reject it if the chapter should stay about objects with attributes.

---

## 8. Two prose fixes

**Kind:** prose
**Where:** lines ~31 and ~152

**Problem and proposal:**

- Line ~31, "and its output shows the attributes and the keyword arguments are one dict" garden-paths: on a first pass "shows the attributes" reads as a complete verb phrase and the sentence has to be restarted. Insert the complementizer: "and its output shows that the attributes and the keyword arguments are one dict".
- Line ~152, "`Stats` names the slots and documents itself at each call site." In Python, "slots" points at `__slots__`, and a `NamedTuple` has no instance `__dict__`, which makes the collision live rather than theoretical. The chapter says "fields" everywhere else. Change to "`Stats` names the fields and documents itself at each call site."

**Cost:** none.

---

## 9. Tighten exercise 4 so the ordering claim cannot fail

**Kind:** exercise
**Where:** section "Exercises", exercise 4 (line ~218)

**Problem:** The exercise says to "add a fourth attribute to `m` by passing it to the constructor, then add it by assignment instead" and confirm `vars(m)` reports the four attributes "in the same order, either way." That holds only when the new attribute is added last on both routes. A reader who passes it to the constructor (giving `info, b, extra, more`, since `m.more = 11` comes after) and then assigns it at the end of the listing instead (giving `info, b, more, extra`) gets two different orders and concludes the exercise is wrong. Verified both orders. The published solution silently picks the reading that works and even notes that dict equality ignores order, so the solution needs no change.

**Proposal:** Replace "then add it by assignment instead" with "then add it by assignment after the existing `m.more = 11` instead", and leave the rest as it stands.

**Cost:** none. `Solutions/22_Data_Transfer_Objects.md` already matches the tightened reading.

---

## 10. Reword the hand-rolled-`Messenger` recommendation

**Kind:** prose
**Where:** section "The Standard-Library Versions" (line ~123)

**Problem:** "Write the hand-rolled `Messenger` only to show how `SimpleNamespace` works underneath" is an imperative telling the reader to write something the chapter has just spent four listings replacing. Read at speed it looks like advice to write it, and only the "only" turns it into advice not to.

**Proposal:** "The hand-rolled `Messenger` is worth writing only to show how `SimpleNamespace` works underneath."

**Cost:** none.

---

## Already fixed directly (no decision needed)

- Nothing. No technical error, failing listing, stale marker, banned phrase, or broken cross-reference turned up in this chapter.

## Verified clean (no action)

- Every `#:` marker matches real stdout: all six extracted scripts run and were compared line by line.
- `ty check 22_Data_Transfer_Objects`, `ruff check`, `heading_links.py`, `banned_phrases.py`, and `reflow_prose.py --diff 22` all pass. The chapter contains no em-dash and no watch-list "don't use" word.
- The four technical claims worth doubting all hold on the pinned 3.15 build: `Messenger("Spam")` raises `TypeError`; `def __init__(self, *, **kwargs)` is a `SyntaxError` ("named parameters must follow bare *"); `self.__dict__ = kwargs` stores that very dict object, so "one dict" is literal, not a figure of speech; and without `m: Any`, `ty` reports four `unresolved-attribute` errors on `messenger_idiom.py`, exactly as the prose states.
- `messenger_idiom.py`'s hand-written `__init__` is not house-style drift. The style guide's carve-out names the `__dict__` trick specifically, and the prose explains it.
- "A record is free to declare a field called `replace` or `fields`" is correct; both work as field names. (A field named `count` or `index` would shadow a real `tuple` method, but the chapter does not claim otherwise and the aside would not earn its line.)
- The inbound links from chapters 8, 12 (×2), 19, 33, and 39 target `#the-standard-library-versions`, `#a-namedtuple-is-still-a-tuple`, and `#returning-multiple-values`, so none of the three section titles can be changed without touching those chapters.
- Exercise 6's predictions are right: `Color(1, 2, 3) == Point3(1, 2, 3)` is `True`, `FrozenColor(1, 2, 3) == (1, 2, 3)` is `False`.
- The chapter opening with a hand-rolled version of a stdlib type inverts the usual "smallest thing first" ordering, but it is the book's historical Messenger idiom, the prose flags it as a teaching device, and the first review pass left it. Recorded as noticed, not proposed.
