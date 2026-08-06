# Deep review: 09_Class_Attributes.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Show that mutating a shared class attribute never shadows

**Kind:** teaching
**Where:** section "Class Attributes Are Not Default Values", after the `inside_objects.py` paragraph (line ~62)
**Problem:** the chapter's central rule is "reading checks the instance first, assigning writes to the instance." That rule protects the reader only when the class attribute is immutable. `Stars.rating` is an `int`, so `a.rating = 1` shadows and the damage stops there. The rule has a hole the chapter never mentions: `a.items.append(x)` is not an assignment, so no instance variable is created and every instance sees the change. This is the class-attribute bug people actually ship, and a reader who has learned only the shadowing rule will conclude the opposite of the truth: that touching an attribute through one instance cannot affect another. The chapter also has no place where a reader could learn this later; chapter 5 covers mutable *default arguments*, chapter 12 covers `@dataclass` rejecting mutable defaults, and neither covers the class-body case.

**Proposal:** add one listing and a short paragraph. Verified output.

```python
# shared_mutable.py

class Cart:
    items: list[str] = []  # One list, shared by every Cart

a, b = Cart(), Cart()
a.items.append("apple")  # Mutates, does not assign
print(a.items, b.items)
#: ['apple'] ['apple']
a.items = ["pear"]  # Assignment shadows, as before
print(a.items, b.items)
#: ['pear'] ['apple']
```

Prose to follow it:

> `a.items.append("apple")` never assigns to `a.items`.
> It reads `items`, finds nothing on `a`, falls back to the class,
> and mutates the one list stored there.
> No instance variable is created, so `b` sees the apple too.
> The next line does assign, which creates `a.items` on the instance and shadows the class list,
> leaving `b` still reading the shared one.
> Reading is the dangerous half: an attribute read that ends in a method call can change shared state,
> and the shadowing rule offers no protection.
> A type checker cannot help here either, since `a.items.append("apple")` is a correct call on a `list[str]`.
> A mutable per-instance default belongs in a `@dataclass` field with a `default_factory`,
> covered in [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes).

Also add an exercise:

> 5. Rewrite `Cart` from `shared_mutable.py` as a `@dataclass` with
>    `items: list[str] = field(default_factory=list)`, then repeat the
>    `append` and confirm `b.items` stays empty. Then try the same class with
>    `items: list[str] = []` and report what `@dataclass` does about it.

(That last part raises a `ValueError` at class-definition time; verified.)

**Cost:** one new file in `Examples/09_Class_Attributes/`. The forward link to chapter 12 duplicates the one already at the end of the chapter, which is fine but could be dropped. Nothing else references `Cart`.

---

## 2. Say why the counter writes `Tally.total` and not `self.total`

**Kind:** teaching
**Where:** section "Class Attributes Are Not Default Values", `class_var.py` and the prose after it (line ~79, ~146)
**Problem:** `class_var.py`'s `__init__` contains `Tally.total += 1`, and no prose says why the class name is written out. The near-miss is `self.total += 1`, which is what a reader coming from an instance-method habit will type. It reads the class value, adds one, and *assigns* the result to the instance, so every `Tally` ends up with its own `total` of `1` and the class counter stays at `0`. Worse, the chapter's stated reason for using `ClassVar` is that "the checker ... stops you from accidentally creating an instance variable that shadows it." I verified that this is untrue for augmented assignment: `ty` 0.0.65 flags `self.total = 5` and `a.total = 99`, but passes `self.total += 1` with no diagnostic. So the one form a reader is most likely to write is the one form the checker misses, and the chapter currently states the checker has it covered.

**Proposal:** add the near-miss listing and amend the `ClassVar` claim. Verified: prints `1 1 0`, and `ty check` reports "All checks passed!".

```python
# counter_near_miss.py
from typing import ClassVar

class Tally:
    total: ClassVar[int] = 0

    def __init__(self) -> None:
        self.total += 1

a, b = Tally(), Tally()
print(a.total, b.total, Tally.total)
#: 1 1 0
```

Prose to follow it:

> `self.total += 1` expands to `self.total = self.total + 1`.
> The read falls back to the class and finds `0`;
> the write lands on the instance and creates a fresh `total` there.
> Every `Tally` counts itself once and the shared counter never moves,
> which is why `class_var.py` writes `Tally.total += 1` with the class name spelled out.
> `ClassVar` does not save you here.
> `ty` rejects a direct `self.total = 5`, but it passes the augmented form,
> so the one mistake you are most likely to make is the one the checker misses.

And change line ~66 from "and stops you from accidentally creating an instance variable that shadows it" to "and rejects a direct assignment through an instance that would shadow it".

**Cost:** one new file. If proposal 5 (splitting out a `ClassVar` heading) is accepted, this listing goes at the end of that new section.

---

## 3. `real_defaults.py` says the dataclass default is "not class attribute", but it is

**Kind:** code
**Where:** section "ClassVar and Inheritance", `real_defaults.py` (line ~204)
**Problem:** the comment reads `x: int = 100  # Constructor default, not class attribute`. `@dataclass` leaves `x = 100` sitting on the class, exactly where an ordinary class attribute sits. I verified: `vars(B)["x"]` is `100` after decoration. The chapter has just spent two listings teaching the reader to check `vars()`, so a reader who applies that lesson here finds the comment contradicted by the tool the chapter told them to use. What makes `B` safe is not the absence of a class attribute but the generated `__init__()`, which writes `self.x` on every instance and shadows the class attribute from birth. That is a better explanation than the comment, and the chapter is one line away from being able to give it.

**Proposal:** change the comment to `# Becomes a constructor default` and add two lines plus a paragraph. Verified output.

```python
print(vars(B)["x"], vars(B())["x"])
#: 100 100
```

Prose to follow the existing "`@dataclass` reads the class-attribute declarations as a template and generates a constructor from them.":

> The class attribute survives the decoration: `vars(B)` still holds `x = 100`.
> What changes is the generated `__init__()`,
> which assigns `self.x` on every instance,
> so each object shadows the class attribute the moment it is built
> and never reads the shared one.
> That is why `b.x = -1` cannot leak into a later `B()`,
> while `a.rating = 1` on `Stars` left `b` reading a value someone else could change.

**Cost:** `Examples/09_Class_Attributes/real_defaults.py` regenerates. Exercise 3 uses `B` and stays correct; it becomes better motivated.

---

## 4. Give the per-object-defaults material its own heading

**Kind:** structure
**Where:** section "ClassVar and Inheritance", line ~188 through ~216
**Problem:** the last third of the "ClassVar and Inheritance" section is about neither `ClassVar` nor inheritance. It starts at "For real per-object defaults, write a constructor with default arguments," and runs through `real_defaults.py` and the chapter's closing pointer to chapter 12. A reader scanning headings to find how to get real defaults will not look under an inheritance heading, and this is the material they came for: the chapter's title question is answered here.

**Proposal:** insert `## Real Per-Object Defaults` immediately before "For real per-object defaults, write a constructor with default arguments,". No prose changes needed; the paragraph already reads as an opener.

Alternative: move the whole block ahead of "ClassVar and Inheritance" so the chapter answers "then how do I get a default?" before detouring into subclass behavior. That reads better as an argument but is a bigger diff.

**Cost:** none for the first form. Three other chapters link to this chapter by anchor (`08_Static_Typing.md`, `12_Data_Classes_as_Types.md`, `17_Metaprogramming.md`), all to `#class-attributes-are-not-default-values`, which this does not touch. `heading_links.py` passes either way.

---

## 5. Split the `ClassVar` material out of the opening section

**Kind:** structure
**Where:** section "Class Attributes Are Not Default Values", line ~64
**Problem:** the opening section runs from line 5 to line 148 and carries three separate lessons: shadowing, the two attribute dictionaries, and `ClassVar` plus bare annotations. The third is the longest and is what the following section ("ClassVar and Inheritance") builds on, but it has no heading of its own, so the chapter looks like one huge section followed by two small ones. It also means the `ClassVar` discussion has no anchor other chapters can link to.

**Proposal:** insert `## Declaring Shared State with ClassVar` before "When you genuinely want one shared value, say so with `ClassVar` from `typing`." The following section, "ClassVar and Inheritance", then reads as a natural continuation.

**Cost:** none. The existing `#class-attributes-are-not-default-values` anchor stays on the earlier heading, so the three inbound links keep working.

---

## 6. "Assigning always writes to the instance" contradicts the listing above it

**Kind:** prose
**Where:** section "Class Attributes Are Not Default Values" (line ~39)
**Problem:** the sentence follows a listing whose second-to-last line is `Stars.rating = 9`, an assignment that writes to the class. The paragraph's implicit subject is "through an instance," carried over from the preceding sentence, but a reader checking the rule against the listing they just read finds a counterexample two lines up.

**Proposal:** change

> Assigning always writes to the instance,
> creating the instance variable on first assignment.

to

> Assigning through an instance always writes to the instance,
> creating the instance variable on first assignment.
> Assigning through the class name, as `Stars.rating = 9` did, changes the shared value.

**Cost:** none.

---

## 7. "the class's two attributes" contradicts the paragraphs above it

**Kind:** prose
**Where:** section "Class Attributes Are Not Default Values" (line ~140)
**Problem:** three paragraphs have just established that `label: str` stores nothing on `Tally`, that `display_object(Tally)` finds no `label`, and that a bare annotation is a declaration rather than a placeholder. The sentence then calls `total` and `label` "the class's two attributes," which is the reading the section spent a page dismantling.

**Proposal:** change "so the class's two attributes read together at the top instead of one hiding inside the constructor" to "so both names read together at the top instead of one hiding inside the constructor".

**Cost:** none.

---

## 8. Cash the parallel between the two classes named `A`

**Kind:** teaching
**Where:** `inside_objects.py` (line ~45) and `real_defaults.py` (line ~198)
**Problem:** the two listings both define a class `A` whose `x` is `100`, and they behave in opposite ways: in `inside_objects.py` the `100` is shared storage, and in `real_defaults.py` it is a per-object default. That contrast is the chapter's whole claim, sitting in two listings that already share a class name and a value, and the prose never points at it.

**Proposal:** after "The change in `a` does not leak", add:

> Both listings define a class `A` whose `x` starts at `100`,
> and the two behave in opposite ways.
> In `inside_objects.py` the `100` lives on the class and every instance reads it;
> here it is a default argument, evaluated per call,
> and `self.x = x` gives each object its own storage before anything can read it.
> The difference is not the value but where it is written.

**Cost:** none. If proposal 4 is accepted, this paragraph goes in the new section.

---

## 9. Say what class attributes are for

**Kind:** teaching
**Where:** section "Class Attributes Are Not Default Values", after the `ClassVar` listing (line ~148)
**Problem:** the chapter is entirely a warning. A reader finishes knowing that class attributes are a trap and that `ClassVar` tells the checker about the trap, without ever being told when they should write one on purpose. `Tally.total` is a legitimate use sitting right there, unlabeled as one.

**Proposal:** add after "`ClassVar` is a hint for the checker, not the runtime." and its two following sentences:

> Shared storage is not a mistake when sharing is the intent.
> A count of every object created, a registry mapping names to classes,
> and a constant that all instances read but none change
> are all class attributes, and all are clearer with `ClassVar` on them.
> `Tally.total` is the first of these.
> The bug is not the class attribute; it is writing one where you meant a per-object default.

**Cost:** none. The registry example anticipates chapter 27; it names the idea without depending on it.

---

## 10. Note that a subclass override does not repeat `ClassVar`

**Kind:** teaching
**Where:** section "ClassVar and Inheritance", `class_var_inheritance.py` (line ~169)
**Problem:** `Right` writes `shared = 100` with no annotation while `Base` writes `shared: ClassVar[int] = 0`, and nothing says whether the bare form is a shortcut, an oversight, or required. It is the house convention. The checker accepts both forms (verified), so nothing in the tooling will tell a reader which to copy.

**Proposal:** add to the paragraph after the listing:

> `Right` writes `shared = 100` without repeating the annotation.
> A subclass overriding a `ClassVar` inherits the declaration along with the name,
> so restating `ClassVar[int]` adds nothing.

**Cost:** none.

---

## 11. Show that `del` un-shadows

**Kind:** exercise
**Where:** section "Exercises"
**Problem:** the chapter teaches that assignment creates the shadowing instance variable but never shows the reverse. A reader who has understood the two dictionaries should be able to predict that deleting the instance attribute makes the class attribute visible again, and that a second delete raises an `AttributeError` rather than removing the class attribute. Confirming it is the cheapest way to check whether they have the model or just the rule.

**Proposal:** add an exercise:

> 6. In `inside_objects.py`, add `del a.x` after the final `print`, then
>    print `vars(a)` and `a.x` again. Predict both before running. Then
>    run `del a.x` a second time and explain the exception, given what
>    `vars(A)` still holds.

(Verified: `{} 100`, then `AttributeError`.)

**Cost:** none. Renumber if proposal 1's exercise is also accepted.

---

## 12. Three uses of "actually"

**Kind:** prose
**Where:** lines ~99, ~132, ~236
**Problem:** "actually" is on the watch list, and all three uses are doing work a stronger verb would do better.

**Proposal:**

- line ~99: "shows what the class actually holds" to "shows what the class holds". The contrast with what it appears to hold is already carried by the next clause, "`total`, and nothing called `label`".
- line ~132: "instead of verifying that every method actually sets it" to "instead of verifying that some method sets it".
- line ~236: "what that assignment actually creates" to "what that assignment creates, and where".

**Cost:** none.

---

## 13. Blank line after the file marker in `inside_objects.py`

**Kind:** code
**Where:** `inside_objects.py` (line ~44)
**Problem:** every other listing in the chapter puts a blank line between the `# slug.py` marker and the first statement, or has an import block there. `inside_objects.py` runs `class A:` straight into the marker.

**Proposal:** add the blank line, matching `class_attribute_confusion.py` and `shared_mutable.py`.

**Cost:** `Examples/09_Class_Attributes/inside_objects.py` regenerates.

---

## Already fixed directly (no decision needed)

Nothing. Every listing runs clean, every `#:` marker matches real stdout, `ty` and `ruff` pass, both cross-reference anchors resolve (`38_Simulation.md#a-robot-in-a-maze` and `12_Data_Classes_as_Types.md#data-classes`), `banned_phrases.py` and `heading_links.py` report no findings, and `reflow_prose.py --diff` reports no paragraphs to change.
