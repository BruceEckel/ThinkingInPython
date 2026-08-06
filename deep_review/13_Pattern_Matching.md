[[Reviewed]]
# Deep review: 13_Pattern_Matching.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Teach the value pattern: a bare name captures, a dotted name compares

**Kind:** teaching
**Where:** section "Alternatives and Capture" (line ~46), new subsection or a second half of that section
**Problem:** The chapter teaches literal patterns and capture patterns but never teaches the *value pattern*, the dotted name (`Color.RED`, `Signal.GO`, `module.CONST`) that compares instead of binding. This is the single most common `match` mistake: a reader who has a named constant writes `case DEFAULT:` expecting a comparison and gets an unconditional capture that shadows the constant inside the function. The chapter's own advice at line ~403 ("Note that `Enum` is also worth considering here") points straight at the construct it never shows.

This is also a broken assumption downstream. [State Machines](31_State_Machines.md) dispatches entirely on `case MouseAction.APPEARS:` / `case MouseAction.ESCAPES:` and so on, and nothing in chapter 13 tells the reader why the dotted form works there while a bare name would not.

**Proposal:** Add to "Alternatives and Capture", after the `step.py` listing, roughly:

> A bare name always binds. It never compares against a variable of that name, so a named constant in a `case` silently captures instead. A *value pattern* is a dotted name, and it does compare:

```python
# value_patterns.py
from enum import Enum
from typing import Final

class Signal(Enum):
    STOP = "stop"
    GO = "go"

DEFAULT: Final[Signal] = Signal.STOP

def act(s: Signal) -> str:
    match s:
        case Signal.GO:
            return "accelerate"
        case Signal.STOP:
            return "brake"

def broken(s: Signal) -> str:
    match s:
        case DEFAULT:
            return f"DEFAULT is now {DEFAULT}"
    return "unreachable"

print(act(Signal.GO), act(Signal.STOP))
#: accelerate brake
print(broken(Signal.GO))
#: DEFAULT is now Signal.GO
print(DEFAULT)
#: Signal.STOP
```

> `case Signal.GO` compares. `case DEFAULT` binds: it matches `Signal.GO`, rebinds `DEFAULT` as a local name inside `broken()`, and leaves the module-level constant untouched. Python catches the mistake when a later `case` follows a bare-name capture, refusing to compile with `SyntaxError: name capture 'DEFAULT' makes remaining patterns unreachable`. When the capture is the last `case`, as here, nothing warns you.
>
> `act()` also shows why an enum is worth the trouble: `Signal` is a closed set, so the checker sees that both members are covered and does not complain about the missing return.

Verified: this listing runs and produces those markers, and passes `ty` with the current toolchain (including `act()` having no `case _`). The `SyntaxError` text is verbatim from CPython.

**Cost:** New listing plus about six lines of prose in an otherwise short section. Adds `Enum` to the chapter's vocabulary before "When Not to Match" mentions it, which is an improvement rather than a cost. Nothing downstream defines a conflicting term.

*Alternative:* give the value pattern its own `## Value Patterns` section between "Alternatives and Capture" and "Sequence Patterns". Cleaner headings, but it splits capture and value patterns apart when the whole lesson is that they look identical.

---

## 2. Say that a class pattern is an `isinstance()` test, and show `case int(n)` / `case str()`

**Kind:** teaching
**Where:** section "Class Patterns" (line ~121 and ~205)
**Problem:** Two gaps in the same paragraph.

First, the chapter never says a class pattern is an `isinstance()` check, so subclasses match and case order matters. A reader who has just met `case Point()` cannot predict that `case int(n)` catches `True`, or that a base-class case placed first swallows every subclass. This directly contradicts what the reader is told later: [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many) and [State Machines](31_State_Machines.md#the-engine) stress that `dict`-keyed-by-`type(x)` dispatch is on classes *exactly*, so a subclass finds no row. That contrast between exact dict dispatch and `isinstance` pattern dispatch is a real design distinction, and chapter 13 is where the second half of it belongs.

Second, the chapter never shows the builtin self-match form. About ten builtins (`int`, `str`, `float`, `bool`, `bytes`, `bytearray`, `list`, `dict`, `set`, `frozenset`, `tuple`) accept one positional sub-pattern that binds the *whole subject* rather than an attribute. [Functional Error Handling](42_Functional_Error_Handling.md) uses `case int(answer):` / `case str(error):` and cross-references back to [Pattern Matching](13_Pattern_Matching.md#matching-values), which teaches literal patterns. A reader following that link finds nothing about `int(answer)`.

**Proposal:** Extend the paragraph at line ~205 (the one ending "works as a type-only check or a final catch-all") with a listing and prose:

```python
# type_patterns.py

def describe(value: object) -> str:
    match value:
        case bool(b):
            return f"bool {b}"
        case int(n):
            return f"int {n}"
        case str(s):
            return f"str of length {len(s)}"
        case _:
            return "something else"

print(describe(True))
#: bool True
print(describe(7))
#: int 7
print(describe("hello"))
#: str of length 5
print(describe(3.5))
#: something else
```

> A class pattern tests with `isinstance()`, so a subclass matches its base's pattern and the order of the cases decides which one wins. `bool` is a subclass of `int`, so moving `case bool(b)` below `case int(n)` makes it unreachable: `describe(True)` would answer `int True`.
>
> The single positional argument in `int(n)` does not name an attribute. A handful of builtins (`bool`, `int`, `float`, `str`, `bytes`, `bytearray`, `list`, `tuple`, `dict`, `set`, `frozenset`) are special-cased so that one positional sub-pattern binds the whole value, which is why `case str(s)` reads as "a string, call it `s`."
>
> Matching on `isinstance()` is the opposite of the exact-type dispatch used by a `dict` keyed on `type(value)`, which [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many) relies on. There a subclass finds no entry at all.

Verified: the listing runs with those markers and passes `ty`.

**Cost:** One new listing. Chapter 42's link at its line ~93 should be retargeted from `#matching-values` to `#class-patterns` once this lands; that is a one-word edit in another chapter, out of scope for this review.

---

## 3. Show one nested pattern and state the alternation binding rule

**Kind:** teaching
**Where:** after "Mapping Patterns" (line ~305) or at the end of "Class Patterns"
**Problem:** Every pattern kind is shown flat and alone. Nothing in the chapter, or anywhere in the book, shows one pattern nested inside another, yet nesting is what makes `match` worth using and it is what the later chapters do. [Composite and Interpreter](34_Composite_and_Interpreter.md) opens straight into `case (Num(0), other) | (other, Num(0)):`, a tuple pattern holding class patterns holding literals, combined under `|`. Exercise 3 of this chapter asks the reader to write a nested mapping pattern that the chapter never demonstrates.

The alternation rule is also unstated and is compiler-enforced: every alternative in a `|` must bind the same set of names, or the file will not compile (`SyntaxError: alternative patterns bind different names`). A reader who learns `|` from `case "up" | "u":`, where nothing binds, has no way to anticipate this.

**Proposal:** A short section titled "Patterns Nest" holding one listing that composes a sequence pattern, class patterns, and an alternation with a shared binding, plus prose stating: sub-patterns are patterns, so anything shown so far can sit in any position; and every branch of a `|` must bind the same names, which the compiler checks. Confirmed: `case (1, x) | (x, 1) | (2, 2):` is a `SyntaxError`, while `case (1, x) | (x, 1):` compiles and binds `x`.

**Cost:** One new section and listing. It makes exercise 3 answerable from the chapter, and gives chapter 34 something to point back at. Placing it after "Mapping Patterns" means it can nest all four pattern kinds; placing it inside "Class Patterns" keeps the chapter's section count down but limits the example.

---

## 4. Warn that a sequence pattern never matches a string

**Kind:** teaching
**Where:** section "Sequence Patterns" (line ~103, after "This shows the structural part...")
**Problem:** `str` and `bytes` are sequences everywhere else in Python but are deliberately excluded from sequence patterns. A reader who has just learned `case [first, *rest]` and tries it on a string gets a silent non-match with no error to explain it. This is the chapter's clearest near-miss: the code a reader would plausibly write behaves differently from what the section teaches, and nothing warns them.

**Proposal:** Add after the paragraph at line ~103:

> A sequence pattern deliberately excludes `str` and `bytes`. `match "abc"` against `case [a, b, c]` does not match, even though a string is a sequence in every other context. Iterating a string a character at a time is almost never what a pattern means, so the language rules it out. A tuple does match: `case [a, b, c]` accepts `(1, 2, 3)` as readily as `[1, 2, 3]`, because the pattern describes a shape, not a concrete type.

Verified both behaviors.

**Cost:** none.

---

## 5. Contrast `case []` with `case {}`

**Kind:** teaching
**Where:** section "Mapping Patterns" (line ~268)
**Problem:** The chapter teaches `case []` as "matches the empty list" and then, two sections later, mapping patterns "ignore keys you do not mention." Put those together and the reader concludes `case {}` matches an empty dict. It matches *every* mapping, including a full one, because "mention no keys" and "require no keys" are the same pattern. This is a lookalike pair the chapter sets up and does not resolve, and getting it wrong means an accidental catch-all sitting above the cases that should have run.

**Proposal:** Add to "Mapping Patterns", after "It ignores keys you do not mention":

> That makes `case {}` a catch-all for any mapping rather than a test for an empty one, the opposite of `case []`, which matches only an empty sequence. Test for an empty dictionary with a guard, `case {} if not event:`.

**Cost:** none.

---

## 6. Flag the guard in `keyword_patterns.py` before Guards is taught

**Kind:** structure
**Where:** section "Class Patterns", `keyword_patterns.py` (line ~186)
**Problem:** `case Point(x=x, y=y) if x == y:` uses a guard one full section before "Guards" introduces the construct. A first-time reader stops on the `if` with nothing to tell them whether it is part of the pattern syntax or something else.

**Proposal:** Add one sentence to the prose after the listing: "The `if x == y` on the third case is a *guard*, covered in the next section." Reordering is not the fix, since "Guards" depends on `Point` from this section.

*Alternative:* rewrite the third case so it needs no guard (for instance `case Point(x=1, y=1)`), which keeps the sections independent but loses a good illustration of a keyword pattern that binds and then constrains.

**Cost:** none.

---

## 7. Make `notifications_oo.py` use dataclasses like the rest of the book

**Kind:** code
**Where:** section "Dynamic Binding vs. Pattern Matching" (line ~425)
**Problem:** `Email`, `Sms`, and `Push` each carry a hand-written `__init__` that only assigns one parameter to one field, which the house style says should be a `@dataclass`, with no reason given in the prose. [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance) does the same comparison and writes `class Shape(ABC)` with `@dataclass(frozen=True) class Rectangle(Shape)`, so this chapter's version reads as drift rather than a choice. It also muddies the comparison: the two versions currently differ both in where behavior lives *and* in how the data is declared, when only the first difference is the lesson.

**Proposal:** Keep `Notification(ABC)` and its two `@abstractmethod` declarations unchanged, and make each channel `@dataclass(frozen=True)` with a single field, dropping the three `__init__` methods:

```python
@dataclass(frozen=True)
class Email(Notification):
    subject: str
    @override
    def render(self, recipient: str) -> str:
        return f"Email to {recipient}: {self.subject}"
    @override
    def cost(self) -> float:
        return 0.001
```

Verified: output is byte-identical, so no `#:` marker changes, and `ty` passes. `test_notifications.py` needs no edit.

Add `from dataclasses import dataclass` to the imports. Reject this if the stark old-school `__init__` is deliberately doing rhetorical work in the OO-versus-data contrast; in that case the prose should say so in a sentence.

**Cost:** Prose at line ~478 ("`Notification` names the shape every channel must have...") stays accurate. Nothing else references these classes.

---

## 8. Add the `as` pattern

**Kind:** teaching
**Where:** wherever proposal 3 lands, or at the end of "Class Patterns"
**Problem:** `as` is one of the pattern forms in PEP 634 and appears nowhere in this chapter or in the book. It is how you match a shape and keep the whole object at the same time (`case Circle(radius) as c:`), which is the natural thing to want once patterns nest. Without it, a reader who needs both the parts and the whole falls back to a `case _` plus `isinstance()`.

**Proposal:** Two sentences and one case arm: an `as` pattern binds the value that its sub-pattern matched, so `case [Point(0, 0) as origin, *rest]:` gives you the point object and its position at once. Best folded into proposal 3's listing rather than given its own listing.

**Cost:** none, unless proposal 3 is rejected, in which case this needs its own home.

---

## 9. Say what the `Enum` parenthetical means

**Kind:** prose
**Where:** section "When Not to Match" (line ~403)
**Problem:** "(Note that `Enum` is also worth considering here.)" is the chapter's only mention of `Enum` and it says neither what to consider it *for* nor what it replaces. Considered against what, the dictionary, the `match`, or the open type set? The reader has to guess.

**Proposal:** Replace with a sentence that names the case: when the closed set is a set of constants rather than a set of shapes, make it an `Enum` and `match` on its members. The enum gives the checker the closed set for free, so `assert_never()` works without a `type` union. If proposal 1 is accepted, this can point back at `value_patterns.py` instead of re-explaining.

**Cost:** none.

---

## 10. Two small prose fixes

**Kind:** prose
**Where:** lines ~14 and ~315
**Problem:**

- Line ~14: "Each `case` body runs only when its pattern matches, and the first match wins" says the same thing twice; "the first match wins" already implies the first half.
- Line ~315: "This error is caught during type checking rather than silently falling through." The error is not what falls through, the unhandled value is.

**Proposal:**

- Line ~14: "Patterns are tried top to bottom and the first match wins."
- Line ~315: "The type checker reports it before the program runs, instead of the value falling through at runtime."

**Cost:** none.

---

## 11. Exercises skip guards and alternation

**Kind:** exercise
**Where:** section "Exercises" (line ~580)
**Problem:** The four exercises cover sequence and class patterns (1), exhaustiveness (2), mapping patterns (3), and the notifications comparison (4). Guards, alternation with `|`, and capture patterns are never exercised, and guards are the construct most likely to be misused, since a guard that could have been part of the pattern hides the pattern's shape.

**Proposal:** Add one exercise: rewrite `guards.py`'s `quadrant()` so that the third and fourth quadrants are handled too, then rewrite it a second time using one `case` per sign combination with `|` alternations and no guards, and say which version reads better. This exercises guards, alternation, and the judgment call between them in one question.

**Cost:** Fifth exercise on a chapter that currently has four.

---

## Already fixed directly (no decision needed)

- line ~202: The claim "A positional pattern cannot do this: it must supply a sub-pattern for every position that `__match_args__` defines" is wrong. A positional pattern may supply *fewer* sub-patterns than `__match_args__` names, and the unmentioned trailing fields go unchecked: `Point(0)` matches `Point(0, 5)`. Supplying *more* than `__match_args__` names is the error (`TypeError: Point() accepts 2 positional sub-patterns (3 given)`), which the chapter already states correctly at line ~167. A wildcard also skips a leading field, so `Point(_, 0)` does what `Point(y=0)` does. Rewrote the passage to state the real behavior and to give the actual reason to prefer the keyword form (it names the attribute and survives a change to the field order, which would silently redefine every position). Verified at runtime.
- line ~315: "static-typing applied to control flow" to "static typing applied to control flow" (the hyphen is wrong on a noun phrase used as a subject).
- line ~398: "inheritance and dynamic binding works better than `match`" to "work better" (compound subject).

No code, no `#:` marker, and no cross-reference was changed, so the built tree still matches the chapter's listings. Confirmed before editing: `ty`, `ruff`, and `pytest` all pass on `build/examples/13_Pattern_Matching`, all eleven listings' stdout matches their `#:` markers exactly, and `heading_links.py` and `banned_phrases.py` pass after the edits.
