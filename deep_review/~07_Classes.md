[[Reviewed]]
# Deep review: 07_Classes.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Show `__str__`, not only `__repr__`

**Kind:** teaching
**Where:** section "String Representation" (line ~323)

**Problem:** The section opens by naming two methods ("`__str__()` is the readable form for users, and `__repr__()` is the unambiguous form for developers") and then defines only `__repr__()`. The listing's comment `# Falls back to __repr__` implies a fallback the reader has never seen either half of. A book-wide grep confirms this is the only place `__str__()` is ever explained: chapters 12, 24, 31, 32, 33, 36 and 38 all *define* `__str__()` in listings with no prior teaching. So the reader meets the pair here, is shown one of them, and never gets the other.

**Proposal:** Keep `representation.py` exactly as it stands (repr only, which is what makes the fallback visible), and add one small listing after it that adds `__str__()` to the same class, plus two sentences of prose. Verified output:

```python
# representation_str.py

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

p = Point(3, 4)
print(p)  # print() prefers __str__
#: (3, 4)
print(repr(p))
#: Point(3, 4)
print([p])
#: [Point(3, 4)]
```

Prose to follow it:

> `print()` and `str()` use `__str__()` when it exists and fall back to `__repr__()` when it does not.
> The fallback runs one way only, so `repr()` never consults `__str__()`.
> A container builds its own display from the `__repr__()` of its elements,
> which is why the list prints `Point(3, 4)` rather than the shorter form.
> In an f-string, `{p}` selects `__str__()` and `{p!r}` selects `__repr__()`.

Then the existing closing line, "Define `__repr__()` on classes you debug," still lands, and can gain: "and add `__str__()` only when users see the output."

**Cost:** One new extracted file, `representation_str.py`. The basename is unused book-wide. Nothing downstream references the section by name.

Alternative: fold `__str__()` into `representation.py` instead of adding a listing. That is a smaller diff but destroys the `# Falls back to __repr__` demonstration, which is the more interesting half.

---

## 2. Explain the backing attribute, and warn about the recursive setter

**Kind:** teaching
**Where:** section "Properties", listing `property_setter.py` (line ~252)

**Problem:** The listing introduces `self._radius` with no explanation. Two things go unsaid, and a reader will hit both. First, why the getter reads a differently-named attribute at all: the property occupies the name `radius` on the class, so the value has to be stored somewhere else. Second, the classic near-miss: writing `self.radius = value` inside the setter looks like the obvious thing and recurses until the interpreter gives up. Verified: it raises a `RecursionError`, with a traceback that names the setter hundreds of times and explains nothing.

**Proposal:** Add prose after the listing:

> The property owns the name `radius` on the class,
> so the value goes into a separate attribute.
> A single leading underscore marks `_radius` as internal to the class,
> a convention rather than a language rule.
> The name matters: assigning to `self.radius` inside the setter would call the setter again,
> and again, until the interpreter raises a `RecursionError`.

**Cost:** none. The underscore convention is stated here for the first time in the book; chapter 9 assumes it without introducing it.

---

## 3. Say why `from_fahrenheit()` uses `cls` rather than the class name

**Kind:** teaching
**Where:** section "Static and Class Methods" (line ~354)

**Problem:** The prose says a `@classmethod` "receives the class as its first argument, conventionally named `cls`," which describes the parameter without giving a reason to use it. `return cls(...)` and `return Temperature(...)` behave identically in this listing, so the reader has no way to see what `cls` buys. The payoff only appears under inheritance, which the chapter has taught two sections earlier and could cash in here.

**Proposal:** Add prose after the listing:

> `from_fahrenheit()` builds its result with `cls(...)` rather than `Temperature(...)`.
> Called on a subclass, `cls` is that subclass,
> so the alternative constructor produces the right kind of object without being rewritten.
> Naming the class directly would hard-code `Temperature` into every subclass.

Verified: with `class Kelvin(Temperature): pass`, `Kelvin.from_fahrenheit(212)` returns a `Kelvin`.

**Cost:** none. If you want it demonstrated rather than asserted, the two-line subclass could go into `class_methods.py`, but that adds a second idea to a listing that currently teaches one.

---

## 4. The `@override` section leans on a type checker the reader has not met

**Kind:** teaching
**Where:** section "Marking Overrides with `@override`" (line ~180)

**Problem:** The section's whole argument is "a type checker now verifies the claim" and "the checker reports an error." Static Typing is chapter 8. At this point the reader has seen no annotations, no checker, and no `ty`. The section asserts a benefit that arrives from a tool the book has not introduced, so it reads as an instruction to trust something unnamed.

**Proposal:** Add a forward link after "A type checker now verifies the claim." (line ~208):

> Python runs the program either way.
> Verification comes from a separate tool, introduced in [Static Typing](08_Static_Typing.md).

**Cost:** none. Adds a second forward reference to chapter 8 alongside the existing ones to 12 and 17.

---

## 5. Link the class-body field warning forward to chapter 9

**Kind:** teaching
**Where:** intro section (line ~62)

**Problem:** Lines 62-69 tell the reader that C++/Java-style field declarations "implicitly become class-level fields (similar to static fields in C++/Java)" and stop there. That is the single most-reported surprise for readers from those languages, and the chapter that resolves it, `09_Class_Attributes.md`, opens with the same premise and shows the shared-storage behavior. Nothing connects them.

**Proposal:** Append one sentence to that paragraph:

> [Class Attributes](09_Class_Attributes.md) shows what that shared storage does when you assign to it.

**Cost:** none.

---

## 6. `@override` does set one attribute at run time

**Kind:** prose
**Where:** section "Marking Overrides with `@override`" (line ~213)

**Problem:** "At runtime `@override` returns the method unchanged" is right about there being no wrapper, but the decorator does mutate the function: CPython's `typing.override` sets `__override__ = True` (inside a `try`, so it is skipped silently on an object that rejects the assignment) and then returns the same object. The attribute exists for run-time introspection and is documented in PEP 698, so a reader who checks will find the sentence contradicted.

**Proposal:** Replace lines 213-214 with:

> At run time `@override` adds no wrapper.
> It sets an `__override__` attribute on the method, for anything that wants to find overrides by introspection,
> and returns the same function object.
> The type checker performs all verification before the program runs.

**Cost:** none.

---

## 7. "mixins" is used without being defined

**Kind:** prose
**Where:** section "Composing Methods with `import`" (line ~414)

**Problem:** The closing paragraph recommends "composition, mixins, or a plain module-level function" as clearer alternatives. Of the three, "mixins" is a term the book has not defined; its first real treatment is chapter 17, and chapter 39's catalog gives it a row. A reader steered toward an undefined term cannot take the advice.

**Proposal:** Drop the word, since the sentence works without it:

> but composition or a module-level function is almost always a clearer choice.

Alternative: keep it and gloss it in place, "mixins (small classes that exist to be inherited for their methods)". The drop is cleaner in a section that has just declared the whole technique a curiosity.

**Cost:** none.

---

## 8. The Inheritance section states a stronger claim than the book holds

**Kind:** teaching
**Where:** section "Inheritance" (line ~97)

**Problem:** "Because Python is dynamically typed, it doesn't really care about interfaces... You inherit an implementation, to reuse the code from the base class." That was true before `typing.Protocol`, and it conflicts with where the book goes: chapter 8 teaches `Protocol`, chapter 20 argues the point at length, and the house style prefers protocols over inheritance hierarchies. The `f()` demo below it is a duck-typing demonstration, which is a structural interface with no name yet.

**Proposal:** Keep the paragraph's shape and voice, adding one sentence at its end:

> Python does have a way to name an interface without inheritance,
> the `Protocol` in [Static Typing](08_Static_Typing.md),
> which describes the shape `f()` requires instead of demanding a base class.

Alternative: place the sentence after the `f()` discussion at line ~178 instead, where the reader has just seen the structural match work. That reads better but separates the claim from its correction by three paragraphs.

**Cost:** none. It does add a fourth forward reference to the chapter.

---

## 9. Mention `@override` before the listing that uses it

**Kind:** structure
**Where:** section "Inheritance", listing `simple2.py` (line ~111)

**Problem:** `simple2.py` opens with `from typing import override` and decorates `show()` with it. The reader is told "The next section explains the `@override` decorator" at line 167, after the listing, a full demo listing, and five paragraphs. Until then, an unexplained import and an unexplained decorator sit in the first inheritance example they see.

**Proposal:** Move the pointer to the sentence that introduces the listing (line ~109), so it reads:

> This example imports and subclasses `Simple`, from the `simple_class` module.
> Ignore the `@override` decorator for now; the section after this one explains it.

and delete the sentence at line 167.

**Cost:** none. Purely a move of one sentence.

---

## 10. An exercise for `__repr__`

**Kind:** exercise
**Where:** section "Exercises" (line ~418)

**Problem:** The four exercises cover properties (1), class methods (2), inheritance and `@override` (3), and `cached_property` (4). Nothing exercises `__repr__()`/`__str__()`, `@staticmethod`, or `display_object()`. String representation is the section a reader will use most often in their own debugging and is the only one they never practice.

**Proposal:** Add:

> 5. Give `Temperature` in `class_methods.py` a `__repr__()` that returns `Temperature(21.0)` for a temperature of 21 degrees Celsius.
>    Print a single `Temperature` and a list of two of them,
>    and confirm the list shows the same form for each element.

If proposal 1 is accepted, extend it: "then add a `__str__()` returning `21.0C` and confirm which of the two `print()` uses for each case."

**Cost:** none.

---

## 11. Trim three watch-list phrasings

**Kind:** prose
**Where:** lines ~247, ~320, ~416

**Problem:** Three sentences carry words from the watch list where the sentence reads the same without them, or reads better rebuilt.

**Proposal:**

- Line 246-248, "The default `@property` is read-only. / It is only a getter. / Assigning to it raises an `AttributeError`." The middle sentence restates the first. Cut it, leaving two sentences.
- Line 320, "A plain `@property` recomputes every time and is never wrong." Rewrite as "A plain `@property` recomputes every time, so its answer is always current." ("plain" earns its place here, drawing the contrast against `cached_property`.)
- Line 416, "You will rarely, if ever, want this in your own code." Rewrite as "You will rarely need this in your own code."

**Cost:** none.

---

## 12. `3.14159` where `math.pi` would do

**Kind:** code
**Where:** listing `properties.py` (line ~224)

**Problem:** `return 3.14159 * self.radius ** 2` hard-codes a truncated pi. The book elsewhere prefers the stdlib, and a reader copying the shape of this method copies the constant with it.

**Proposal:** Leave it. The literal keeps the output marker at a clean `314.159`; `math.pi` gives `314.1592653589793`, which is noise in a listing whose subject is the `@property` decorator. Recorded here only so the choice is deliberate rather than unnoticed. If you would rather use `math.pi`, the fix is `import math` plus rounding at the call site (`print(round(c.area, 3))`), which costs a line and a distraction.

**Cost:** none if left alone.

---

## Already fixed directly (no decision needed)

- line ~59: "At the bottom of the example you can see that the creation of an object looks like a function call" pointed at the wrong place. Object creation is the *first* statement of `demo_simple_class.py`, not the bottom of anything; the phrasing appears to date from when the class and its demo were one listing. Changed to "In the demo you can see...".

## Verified clean (no action)

- Every `#:` marker in the chapter matches real stdout, checked by running all thirteen extracted scripts (`display_simple.py` needs `build/examples/utils` on `PYTHONPATH`, which the gate supplies).
- `ty check 07_Classes`, `ruff check`, `banned_phrases.py`, `heading_links.py`, and `reflow_prose.py --diff 07` all pass.
- Exercise arithmetic checks out: `Circle(10).shrink(2)` gives 5 and `shrink(-2)` gives -5, which the setter rejects; `k - 273.15` is right for exercise 2; exercise 4's `average` does read `total` from the cache.
- The untyped listings are deliberate, not drift. Chapter 8 opens with "The examples up to this point have no type declarations."
- `representation.py`'s hand-written `__init__` is not a dataclass-style violation: the section pointing at `12_Data_Classes_as_Types.md` states the reason, and dataclasses are five chapters away.
- Blank lines between methods are inconsistent within the chapter (`simple_class.py` and `simple2.py` run methods together, `properties.py` and the rest separate them), but a survey of `build/examples` shows the book is split roughly 50/50, so no house convention is being broken.
