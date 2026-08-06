# Deep review: 12_Data_Classes_as_Types.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Say that `frozen=True` is shallow, in the chapter that makes the frozen argument

**Kind:** teaching
**Where:** section "Immutability" (line ~237), with follow-on at "More Data Class Tools" (line ~831) and "When a Data Class Is the Wrong Tool" (line ~587)
**Problem:** This is the chapter that establishes the whole guarantee: "If an object cannot change after it is built, then validating it at construction makes it valid for its lifetime," and "Immutability guarantees no one can damage the value after construction." Both sentences are unqualified, and both are false for any field holding a mutable object. The chapter then supplies two live counterexamples of its own without comment:

- `month_dataclass.py`: `@dataclass(frozen=True) class Months` with `months: list[Month]`
- `dataclass_features.py`: `@dataclass(frozen=True) class Line` with `points: list[Point]`

Verified: `Line([Point(2, 7)]).points.append(Point(0, 0))` succeeds and the object's `__repr__` changes. The reader who has just been told the guarantee holds for a lifetime meets two objects for which it does not, and nothing marks them.

The same paragraph also overstates hashability. "As a bonus, a frozen instance is hashable, so you can use it as a dictionary key or put it in a set" is true of `Messenger` and false of `Line` and `Months`: `hash(Line([Point(2, 7)]))` raises `TypeError: unhashable type: 'list'`. A frozen data class is hashable when all of its fields are.

`frozen_leaky.py` in [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution) demonstrates the leak, but that is eight chapters later, and 20 links *back* here for "the fuller case for frozen data classes." Chapter 40 also calls it "the shallow-freezing lesson of Rethinking Objects." The origin point of the argument should not be the one place that omits the caveat.

**Proposal:** Add two sentences to the "Immutability" section, after the `frozen_messenger.py` listing and before "If an object cannot change after it is built":

> `frozen=True` guards the binding, not the object behind it.
> A field holding a `list` can still be mutated in place,
> and a frozen instance is hashable only when every field it holds is,
> a leak [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution) demonstrates.
> The types in this chapter hold `int`s and `str`s, so the guarantee is total for them.

Then qualify the closing claim of "A Type Is a Set of Values": "Immutability guarantees no one can damage the value after construction" becomes "Immutability guarantees no one can rebind the fields after construction, and when the fields are immutable too, no one can damage the value at all."

*Alternative, heavier:* pull a two-line version of `frozen_leaky.py` into this chapter and let 20 refer to it rather than the reverse. That duplicates a listing and moves a cross-chapter thread's origin, so I do not recommend it.

**Cost:** Touches the cross-chapter frozen-is-shallow thread (12 → 20 → 22 → 35/36 → 40). Adds a forward link from 12 to 20, alongside 20's existing back link to 12. No listing changes.

---

## 2. Warn that `__post_init__()` cannot assign to a frozen field

**Kind:** teaching
**Where:** section "A Type Is a Set of Values" (line ~284)
**Problem:** The chapter teaches `__post_init__()` purely as a checker. The first thing a reader tries next is normalizing a value there: lowercase the email, strip the whitespace, round the float. On a frozen data class that raises `FrozenInstanceError`, verified:

```python
@dataclass(frozen=True)
class Email:
    text: str
    def __post_init__(self) -> None:
        self.text = self.text.lower()   # FrozenInstanceError
```

This is the chapter's most likely near-miss, and it is invisible from what is shown, because every `__post_init__()` in the chapter only reads. The escape hatch (`object.__setattr__(self, "text", self.text.lower())`) looks like a hack unless someone explains that `frozen=True` works by installing a rejecting `__setattr__`, which is the same mechanism `frozen_messenger.py` already demonstrated.

**Proposal:** Add a short paragraph plus a listing after the `stars.py` discussion (after "The validation lives in one place: the constructor."):

> `__post_init__()` can check a field but cannot change one.
> `frozen=True` installs a `__setattr__` that rejects every assignment,
> including the ones coming from inside the class,
> so normalizing a value there raises `FrozenInstanceError`.
> Going around it with `object.__setattr__()` works and says what it is doing,
> but the cleaner answer is usually to reject the unnormalized value
> and normalize before construction.

Listing (`post_init_normalize.py`) showing the failing version under `try`, then the `object.__setattr__` version, with `#:` markers.

*Alternative:* prose only, with no listing, if the chapter is already long enough.

**Cost:** One new listing and a marker to keep in sync. Introduces `object.__setattr__` as a named escape; check whether 20 or 36 already introduce it and link instead if so.

---

## 3. Contrast `copy.replace()` with the copies that skip the constructor

**Kind:** teaching
**Where:** section "The General Form of `replace()`" (line ~885)
**Problem:** The section ends on exactly the right observation: "A copy that skipped the constructor would be a hole in the guarantee." It never says that such copies exist, are in the same module, and are what a reader is more likely to use. Verified on `Stars`:

| call | runs `__post_init__()`? |
|---|---|
| `copy.replace(s, number=2)` | yes |
| `copy.copy(s)` | no |
| `copy.deepcopy(s)` | no |
| `pickle.loads(pickle.dumps(s))` | no |

`copy.replace()` and `copy.copy()` sit next to each other in one module and behave differently on the exact property the chapter is arguing for. That is the chapter's sharpest lookalike pair and it is not taught. [Memento](36_Memento.md) already relies on the pickle half ("The same shortcut skips `__post_init__`"), so the fact is load-carrying elsewhere.

**Proposal:** Replace the closing paragraph's last sentence with a short listing (`replace_vs_copy.py`) printing whether `__post_init__()` ran for each of the three calls, followed by:

> `copy.replace()` rebuilds through the constructor.
> `copy.copy()`, `copy.deepcopy()`, and `pickle` restore an object's state directly
> and never call `__init__()` or `__post_init__()`,
> so they can produce a `Stars` holding a number no check ever saw.
> A validated type stays validated across a replacement but not across a naive copy,
> which [Memento](36_Memento.md) revisits when a saved object outlives the class that saved it.

**Cost:** One new listing. Adds a 12 → 36 forward link to match 36's existing back link.

---

## 4. Split "When a Data Class Is the Wrong Tool" into the three things it holds

**Kind:** structure
**Where:** section "When a Data Class Is the Wrong Tool" (lines ~545-722)
**Problem:** One section carries three unrelated arguments:

1. `Month` as a data class instead of an `Enum` (the section's actual subject, ~50 lines).
2. `default_factory`, mutable defaults, and whether to subscript the factory (~55 lines, `factory_checking.py`). This is a data class *feature*, not a wrong-tool argument, and it arrives because `Months` happens to need one. A reader following "should this be an `Enum`?" is dropped into a digression on type-checking factory callables and picked back up 55 lines later at "Choose the tool that makes the legal set easiest to express."
3. A subsection titled "A `NamedTuple` Cannot Take That Responsibility," which argues the data class is the *right* tool, nested under a heading saying it is the wrong one.

**Proposal:** Three edits.

- Promote the `default_factory` material to its own `##` section, "Defaults That Are Built, Not Shared," placed with the other feature sections (after "More Data Class Tools"). Leave one sentence behind in `month_dataclass.py`'s discussion: "The `months` field needs a `field(default_factory=...)`, covered in [Defaults That Are Built, Not Shared](#...)."
- Promote the `NamedTuple` subsection to its own `##` section, "A `NamedTuple` Cannot Validate Itself," keeping the `{#namedtuple-cannot-validate}` anchor so the two inbound links (from "Immutability" in this chapter, and any from 22) survive.
- Retitle the remainder "When an `Enum` Beats a Data Class," which is what the surviving 50 lines argue.

**Cost:** Anchor `#when-a-data-class-is-the-wrong-tool` disappears. Grepped: the only inbound reference was the one in "Immutability," which I have already retargeted to `#namedtuple-cannot-validate` (see "Already fixed"). No other chapter or Solutions file links to it. Two new anchors need `heading_links.py` to pass.

---

## 5. Move the A/B/C/D comparison next to "Data Classes"

**Kind:** structure
**Where:** section "Comparing Ordinary Classes and Data Classes" (lines ~1043-1247)
**Problem:** This 200-line section answers "what does `@dataclass` actually do with those annotations?" It is the mechanism behind the chapter's central tool. It sits 900 lines after the section that raises the question, behind Enums, NamedTuples, inheritance, `asdict`, `replace`, and JSON. By the time a reader arrives, they have been using dataclasses for eleven sections on faith.

The question arises at line ~138 ("The `@dataclass` decorator generates `__init__()`, `__repr__()`, and `__eq__()` from the fields you declare") and is answered at line ~1171 ("`@dataclass` reads them, through `dataclasses.fields()`, to learn what fields exist"). That is the widest question-to-answer gap in the chapter.

**Proposal:** Move the whole section (including `comparison.py`, `A`, `B`, `C`, `D`) to sit immediately after "Data Classes" and before "Immutability". `display_object()` is already introduced in "Data Classes," so nothing it needs moves with it.

*Alternative, cheaper:* leave it where it is and add a forward pointer at the end of "Data Classes": "[Comparing Ordinary Classes and Data Classes](#comparing-ordinary-classes-and-data-classes) shows what `@dataclass` reads and what it generates, field by field."

*Alternative, most aggressive:* the chapter is really two chapters, a thesis (intro through the `NamedTuple` section) and a data-class reference (inheritance, tools, `replace`, JSON, A/B/C/D). Splitting them would give both room, at the cost of renumbering everything from 13 on and invalidating ~20 inbound cross-references. Not recommended, but worth naming, since it is why the second half reads as a list rather than an argument.

**Cost:** The move relocates the `#comparing-ordinary-classes-and-data-classes` anchor within the file (links keep working). It puts `display_object()`'s `REDEFINED_DUNDERS` mode before `INTERESTING_DUNDERS` is used a second time; check the two paragraphs that reference "demonstrated for `Messenger`" still read in order. Chapter 09 links to `#data-classes` only, so it is unaffected.

---

## 6. Make the base class in `dataclass_super_init.py` do something the fix can prove

**Kind:** code
**Where:** section "Inheritance and the Generated `__init__`" (line ~759)
**Problem:** The first listing lands its point: `Connection.__init__` never runs, `hasattr(c, "host")` is `False`. The fix listing then declares `host: str` as a data class field *and* calls `super().__init__(self.host)`, which assigns `self.host = host` a second time. The base initializer accomplishes nothing observable, so the output (`localhost db`) would be identical with the `__post_init__()` deleted. The listing shows the syntax of the fix without demonstrating that it fixed anything.

**Proposal:** Give `Connection.__init__` a derived attribute the data class cannot produce, so its absence is visible:

```python
class Connection:
    def __init__(self, host: str) -> None:
        self.host = host
        self.url = f"tcp://{host}:5432"
```

Then `print(c.url, c.name)` prints `tcp://localhost:5432 db`, and deleting `__post_init__()` makes it fail. Optionally add the same `url` to the first listing so the two read as one before/after.

**Cost:** Two `#:` markers change. `dataclass_inherits_plain.py` may want the same base for symmetry, which changes a third marker.

---

## 7. `@dataclass` rejects unhashable defaults, not mutable ones

**Kind:** teaching
**Where:** section "When a Data Class Is the Wrong Tool" (line ~604)
**Problem:** "Every instance shares a single default object, the trap shown in Functions, so data classes reject mutable defaults outright." The rejection is real but the rule stated is not the rule implemented. `@dataclass` refuses a default whose class is unhashable, which catches `list`, `dict`, and `set` and misses every mutable object of your own. Verified:

```python
class Bag:
    def __init__(self) -> None:
        self.items: list[int] = []
SHARED = Bag()

@dataclass
class B:
    bag: Bag = SHARED       # accepted with no complaint

b1, b2 = B(), B()
b1.bag.items.append(1)
print(b2.bag.items, b1.bag is b2.bag)   # [1] True
```

A reader who takes "data classes reject mutable defaults outright" at face value will believe the language has closed the hole, and the exact bug from chapter 05 walks straight back in through a custom class.

**Proposal:** Rewrite the sentence and add one:

> `@dataclass` refuses a default it can tell is shared storage,
> which covers `list`, `dict`, and `set`.
> The test is hashability, not mutability,
> so a mutable object of your own class passes as a default and is shared by every instance,
> the trap shown in [Functions](05_Functions.md#default-and-keyword-arguments).
> Use `default_factory` for anything that is not obviously a constant.

**Cost:** None. No listing changes, though a two-line demo of the `Bag` case would strengthen it if you want one.

---

## 8. Explain `eq=False` after `@dataclass` has been introduced, not 90 lines before

**Kind:** structure
**Where:** chapter opening (lines ~46-50)
**Problem:** `validation.py` is the third listing in the chapter, and the paragraph explaining it says "A data class that defines `__eq__()` sets `__hash__` to `None`." The section that explains what `@dataclass` generates ("Data Classes") is 90 lines later, and the `__hash__ = None` behavior is shown there, in `display_messenger_class.py`. A reader who arrives from chapter 09's one-paragraph introduction has never been told that `@dataclass` generates an `__eq__` at all, so the sentence is an assertion about machinery they have not met, used to justify an argument they cannot yet check.

**Proposal:** Keep `validation.py` where it is (the chapter needs `check()` early) and add a pointer clause to the `eq=False` paragraph:

> `eq=False` turns off the generated `__eq__()`, for two reasons.
> A data class that defines `__eq__()` sets `__hash__` to `None`
> (shown for `Messenger` in [Data Classes](#data-classes)),
> and an unhashable exception is a trap if you put it in a set.

*Alternative:* move both `eq=False` paragraphs to a short note at the end of the "Data Classes" section and leave the opening listing unexplained until then. Cleaner ordering, but it separates the explanation from the code by three sections, which is worse.

**Cost:** None. `#data-classes` already exists and is linked from four other chapters.

---

## 9. Say why each `Month` value is a pair

**Kind:** teaching
**Where:** section "Enums Are Types Too" (line ~473)
**Problem:** `JANUARY = (1, 31)` carries a month number that no code in the listing reads: `max_days` returns `self.value[1]` and `of()` uses `list(Month)[month_number - 1]`. A reader looking for what `value[0]` is for finds nothing, and the obvious simplification (`JANUARY = 31`) silently breaks the type: `APRIL`, `JUNE`, `SEPTEMBER`, and `NOVEMBER` would all be `30` and `Enum` would collapse the last three into aliases of `APRIL`, leaving nine members where twelve are needed. That is a genuinely instructive `Enum` rule and the listing is one sentence away from teaching it.

**Proposal:** Add after "The `Enum` creates the constrained set of `Month`s":

> Each value is a pair rather than a bare day count because `Enum` treats members with equal values as aliases of one another.
> `APRIL = 30` and `JUNE = 30` would make `JUNE` a second name for `APRIL`,
> and `list(Month)` would return nine members instead of twelve.
> Pairing each month with its number keeps all twelve values distinct.

**Cost:** None.

---

## 10. Give the before/after `f1()` the same shape

**Kind:** teaching
**Where:** sections "A Class Is Not a Type" (line ~113) and "A Type Is a Set of Values" (line ~299)
**Problem:** The chapter's central before/after rests on two functions with the same name that do different jobs. `stars_class.py` has `f1(self, n: int) -> int`, which ignores the current rating, stores `n + 5`, and returns an `int`. `stars.py` has `f1(s: Stars) -> Stars`, which reads `s.number`, adds 5, and returns a `Stars`. The reader is asked to see that the precondition and postcondition disappeared, but the signature, the argument's meaning, and the return type all changed at once, so the disappearance is not isolated. Exercise 3 asks the reader to perform this transformation, which is harder when the two poles do not line up.

**Proposal:** Change `stars_class.py`'s method to take no extra argument and add 5 to its own value, matching `stars.py`'s `f1()`:

```python
    def f1(self) -> int:
        self._number = self._number + 5
        self._validate()  # Postcondition
        return self._number
```

That drops the precondition too, which weakens the DbC point. Better: keep the precondition by having it operate on a second rating, and make `stars.py`'s `f1()` take the same pair. Either way, the point is that exactly one thing should differ between the two listings.

*Alternative:* leave the code and add one sentence to "A Type Is a Set of Values" naming the change: "`f1()` now takes and returns a `Stars` rather than an `int`, which is where the checks went."

**Cost:** `stars_class.py`'s marker changes (`8` becomes `9` under the shown variant). `test_stars.py` asserts `f1(Stars(2)) == Stars(7)` and `test_transformation_can_produce_illegal_value` depends on `f2`, so only the `stars_class.py` side moves. Exercise 3's wording may need a matching tweak.

---

## 11. Fix the `# Nested dict` / `# Nested tuple` comments

**Kind:** code
**Where:** section "More Data Class Tools" (lines ~826-828)
**Problem:** `p` is `Point(10, 20)`, so `asdict(p)` is `{'x': 10, 'y': 20}` and `astuple(p)` is `(10, 20)`. Neither is nested. The comments say "Nested dict" and "Nested tuple," which is what the *third* call (`asdict(line)`) demonstrates, and it already carries an accurate comment ("Recurses into the list of Points"). A reader checking the comment against the output finds they disagree.

**Proposal:** Drop both comments. The recursion point is made by the `Line` call three lines down, and the surrounding prose already says "recursing into nested data classes."

**Cost:** None. Comment-only edit, no marker change.

---

## 12. Explain the `setattr()` in `frozen_messenger.py`

**Kind:** teaching
**Where:** section "Immutability" (line ~257)
**Problem:** The prose says "Attempting to assign to a field raises `FrozenInstanceError`" and the listing then writes `setattr(m, "name", "bar")` rather than `m.name = "bar"`. The reason is that the type checker rejects the direct form at analysis time, so the runtime demonstration would never run. Nothing says so, and a reader may conclude that `setattr()` is somehow special or that direct assignment is allowed. Chapter 20 makes the opposite choice in `frozen_leaky.py` (`fl.numbers = []  # type: ignore`), so the two chapters model two different workarounds for the same problem with no explanation in either.

**Proposal:** Add one sentence after the listing:

> The listing goes through `setattr()` because the type checker rejects `m.name = "bar"` before the program runs,
> which is the earlier of the two defenses.
> `frozen=True` is the one that holds at runtime, against code the checker never saw.

**Cost:** None to this chapter. Consider matching 20's `frozen_leaky.py` comment if you want the two to agree; that is 20's call.

---

## 13. Spread the exercises across the chapter's claims

**Kind:** exercise
**Where:** section "Exercises" (line ~1248)
**Problem:** Four exercises cover the `Enum` (1), composition and validation (2, partly), the frozen rewrite (3), and JSON-plus-validation (4). Three of the four are variations on "write a `__post_init__()` check." Nothing exercises `replace()`/`__replace__()`, the inheritance trap, `default_factory`, or the `ClassVar` distinction the last 200 lines develop. The A/B/C/D section is the longest in the chapter and has no exercise at all.

**Proposal:** Add two, and consider dropping or merging exercise 2 (which is the same skill as exercise 1):

> 5.  Give `Stars` a `__replace__()`-based variant helper without using a data class:
>     write a plain class holding the rating, define `__replace__()`,
>     and confirm that `copy.replace()` still runs your validation.
> 6.  Add a `ClassVar[int]` counter to `Stars` that records how many have been built.
>     Predict whether it appears in the generated `__init__()`'s parameter list before you run it,
>     then check with `display_object()`.

Exercise 6 has a second edge worth keeping: incrementing a `ClassVar` from `__post_init__()` on a frozen class works, because it assigns to the class rather than the instance. That is a small surprise the chapter's `frozen`/`ClassVar` material earns.

**Cost:** Solutions file for chapter 12 needs the two new answers. Exercise 6 depends on proposal 2's material only if the reader tries the instance-attribute version first.

---

## 14. Close the chapter

**Kind:** structure
**Where:** end of chapter, before "Exercises" (line ~1247)
**Problem:** The chapter ends on "Only assigning it a value does," the last sentence of a `ClassVar` mechanics discussion, then goes straight to exercises. The thesis stated on the first page (a type is a set of values, parse once, hold the proof) is never returned to, and the second half of the chapter has drifted far enough from it that the reader's last impression is `D.__annotations__`. Naming the capability the reader gained is the load a conclusion carries, and there is no conclusion.

**Proposal:** Add a short `##` section before "Exercises," titled for its content rather than "Summary." Something that adds an insight instead of rehashing: that the checks did not disappear, they moved to a place where they run exactly once and cannot be skipped, and that the cost of the guarantee is one constructor call at every boundary where data enters (JSON, a database row, a form field), which is where the `from_json()` example puts it.

**Cost:** None. Consider whether the neighboring chapters' style (09 and 10 also end straight into Exercises) makes this a book-wide decision rather than a chapter-12 one.

---

## 15. Drop the docstring from `Color`

**Kind:** code
**Where:** section "The General Form of `replace()`" (line ~904)
**Problem:** `class Color:` carries `"Three channels packed into one int, so no data class fits."` as a docstring. House style puts a listing's explanation in the surrounding prose, and the prose two paragraphs down already says it: "`Color` stores no separate fields, so `dataclasses.replace()` has nothing to work with." Only five chapter listings in the book carry a docstring, and three of them exist because the docstring is what the example inspects. This one is a duplicate of adjacent prose.

**Proposal:** Delete the docstring line. The manual `__init__` still has its stated reason, one paragraph below the listing.

*Alternative:* keep it, on the grounds that it is what justifies the hand-written `__init__` at the point a reader meets it, before the prose arrives. If so, `Tickets` in 19 is the same case and the two should stay consistent.

**Cost:** None. No output change.

---

## 16. Show a forgotten check in `stars_unchecked.py`

**Kind:** teaching
**Where:** section "A Value That Must Be Checked Everywhere" (line ~59)
**Problem:** The section's argument is that the duplicated check is easy to forget, and the listing shows two functions that both remember. Nothing illegal is ever passed, nothing fails, and the output is three correct numbers. The reader is told about the cost rather than shown it, in the one section whose job is to motivate everything after it.

**Proposal:** Add a third function that omits the check and let it return a nonsense rating:

```python
def f3(stars: int) -> int:  # The check is missing here
    return stars * 100

print(f3(11))
#: 1100
```

with a sentence noting that `11` was never a legal rating and nothing objected.

*Alternative:* keep the two functions and pass an illegal value to `f1()` under `try`, printing the `TypeFailure`. That shows the check working rather than the check missing, which is the weaker of the two lessons here.

**Cost:** One marker added. `stars_unchecked.py` is not imported by any test.

---

## Already fixed directly (no decision needed)

- line ~275: the forward reference in "Immutability" pointed at `#when-a-data-class-is-the-wrong-tool`, a section about `Enum` versus data class. The `NamedTuple` difference it advertises is in that section's subsection, which has its own anchor. Retargeted to `[A `NamedTuple` Cannot Take That Responsibility](#namedtuple-cannot-validate)`. `heading_links.py` passes.
