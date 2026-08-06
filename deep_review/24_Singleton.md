# Deep review: 24_Singleton.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Demonstrate the module-caching fact the chapter opens by asserting

**Kind:** teaching
**Where:** section "A Module Is Already a Singleton" (lines ~10-21), plus `config.py`
**Problem:** the chapter's whole argument rests on its second sentence: "Python imports each module once and caches it in `sys.modules`. Every `import` after the first produces the same module object." The book has never taught this. I grepped every chapter: `sys.modules` appears nowhere except this line. [Modules and Packages](06_Modules_and_Packages.md) states that importing runs the module's top-level code, and its exercises 1 and 2 ask the reader to *confirm* the message prints only once, but its prose never says why, and an exercise the reader may have skipped is not a teaching. So a pointer to chapter 6 would point at nothing. The reader is asked to accept the chapter's foundational claim on assertion, in a chapter whose entire thesis is that the language already does this for you.

A cheap fix is available because `config.py` currently carries no evidence at all: it is two lines with no output, so nothing in the section shows the caching, only its consequence.

**Proposal:** add a `print()` to `config.py` so its body announces itself, then add one listing between `config.py` and `shared_config.py`. Both verified: lint clean under the repo's ruff config, output exactly as shown.

```python
# config.py
print("config body runs")
settings: dict[str, str] = {}
```

```python
# import_once.py
import config
import config as again

print(config is again, config.settings is again.settings)
#: config body runs
#: True True
```

Prose to follow it (replacing nothing; slot it after the new listing):

> Two `import` statements, one printed line.
> The first one runs `config.py` top to bottom and files the resulting module object in `sys.modules` under the name `config`.
> The second finds it there and skips the work, so the body never runs twice and only one `settings` dict is ever built.
> That is the singleton: not a rule the class enforces, but a lookup the import system performs.

`shared_config.py` then gains one marker line, since importing `config` prints:

```python
# shared_config.py
from config import settings

settings["theme"] = "dark"
print(settings)
#: config body runs
#: {'theme': 'dark'}
```

*Alternative, zero cost to existing listings:* leave `config.py` alone and add only `import_once.py` with the `#: True True` marker. This shows that both names reach one module object and one dict, but not that the body runs once, which is the half that explains why there is only one dict to share.

**Cost:** one extra `#:` line in `shared_config.py`. Exercise 4 tells the reader to predict `shared_config.py`'s printed values, so it should say "the two dicts" rather than "both printed values" if the banner line is added. Nothing outside this chapter imports `config`.

---

## 2. Say that a module singleton is one per interpreter, not one per program

**Kind:** teaching
**Where:** section "A Module Is Already a Singleton", line ~12
**Problem:** the chapter says module-level state is "shared, with one copy for the whole program." A reader who has come through [Concurrency](19_Concurrency.md) knows that is not true of every program they might write. That chapter's "Subinterpreters" section says each worker interpreter "keeps its own isolated objects," and its process-pool sections make the same point for processes. So the singleton this chapter recommends silently becomes several the moment the reader uses either. The chapter goes on to discuss threads at length and never mentions the boundary that actually breaks a singleton.

**Proposal:** change "with one copy for the whole program" to "with one copy for the whole interpreter" and add two sentences at the end of that paragraph:

> One interpreter, not one machine.
> A process pool or an [`InterpreterPoolExecutor`](19_Concurrency.md#subinterpreters) gives each worker its own `sys.modules`, so each builds its own copy and a write in one is invisible to the rest.
> A singleton is only single inside the interpreter that holds it, and that is true of every form in this chapter, not only the module.

**Cost:** none. It reuses a section title chapter 19 already has, so `heading_links.py` will hold the reference.

---

## 3. Show the eight-object race, do not only assert it

**Kind:** teaching
**Where:** section "Tests, Threads, and Locks", note 2 (lines ~136-146)
**Problem:** the chapter tells the reader "Eight threads calling `settings()` at once ... ran that constructor eight times and handed back eight different objects," and then shows a listing that prints `1`. The broken number is prose, the fixed number is output. This is the mechanism-versus-outcome gap: a reader can see the cure and has to take the disease on faith, when the disease is the more surprising fact (a decorator named `cache` calling the function eight times). I reproduced it: 8 constructor calls and 8 distinct objects on 8 of 8 runs.

**Proposal:** add this listing immediately after note 3, before the sentence "`@cache` is gone, because it no longer makes the object single". Verified: ruff clean, printed `True` on 6 of 6 runs.

```python
# singleton_cached_race.py
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import cache

@dataclass
class Settings:
    data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        time.sleep(0.05)  # Widen the first-call window

@cache
def settings() -> Settings:
    return Settings()

with ThreadPoolExecutor(max_workers=8) as pool:
    built = list(pool.map(lambda _: settings(), range(8)))
print(len({id(s) for s in built}) > 1)
#: True
```

One line of prose after it: "Eight threads, more than one object. Every thread checked the cache before any of them had filled it, so each ran the constructor and seven results were thrown away."

The marker is a boolean rather than `8` on purpose. The count is 8 every time I measured, but it is a timing measurement, and CLAUDE.md's traps warn that the self-healing gate would rewrite a flaky count without flagging it. "More than one" cannot degrade quietly, and the existing prose already supplies the number 8.

**Cost:** the listing repeats most of `singleton_locked_settings.py`, which is the point (same scaffolding, one difference), but it does add ~18 lines to an already long section. It also means the reader meets `ThreadPoolExecutor` one listing earlier than now.

*Alternative:* keep the assertion and add "(the listing below differs from this one only in the locking)" so the reader at least knows the two are the same experiment.

---

## 4. Name chapter 21's dissolution thesis in the conclusion

**Kind:** structure
**Where:** section "Which Should You Use?", final paragraph (lines ~667-669)
**Problem:** this chapter is one of the clearest cash-ins of the claim [The Pattern Concept](21_The_Pattern_Concept.md) makes: "A pattern is often a sign of something missing in a language ... When a language later absorbs the feature, the pattern dissolves into it." The chapter's closing paragraph makes that argument in its own words and never connects it. [Iterators](23_Iterators.md), [Changing the Interface](29_Changing_the_Interface.md), and [Pattern Refactoring](37_Pattern_Refactoring.md) all link back to chapter 21 at the equivalent moment; Singleton is the strongest case in the book and is missing from that set.

**Proposal:** append one sentence to the final paragraph:

> This is the dissolution [The Pattern Concept](21_The_Pattern_Concept.md) describes: the pattern acquired a name because the language was missing a feature, and Python's import system is that feature.

**Cost:** none.

---

## 5. Add an exercise on the `__new__()` return rule

**Kind:** exercise
**Where:** section "Exercises" (line ~671)
**Problem:** the chapter states one rule three separate times, in `singleton_with_new.py`, `singleton_class_variable.py`, and `singleton_metaclass.py`: `__init__()` runs only when `__new__()` returns an instance of the class being constructed, and the three listings deliberately land on both sides of it. It is the chapter's most repeated teaching, and no exercise touches it. The four current exercises cover the module form twice, the cached factory once, and lazy-versus-eager once.

**Proposal:** add as exercise 5:

> 5.  `singleton_with_new.py` and `singleton_class_variable.py` differ in what `__new__()` returns,
>     and that decides whether `__init__()` runs at all.
>     Give each class an `__init__()` that prints a line,
>     then predict how many times each one prints across three constructions before running either.
>     Explain the difference in terms of what `__new__()` handed back.

**Cost:** none. It is answerable from the "Overriding `__new__`" and "One Instance in a Class Variable" sections.

---

## 6. Explain `__getattr__()` where the reader first meets it

**Kind:** teaching
**Where:** section "Lazy Creation", after `singleton_pattern.py` (line ~283)
**Problem:** `__getattr__()` appears in the chapter's first classic listing with the gloss "`__getattr__()` delegates access." That does not say when Python calls it, so a reader can reasonably assume it intercepts every attribute access. The mechanism arrives a full section later, under "Eager Creation": "It answers for every name Python fails to find on the wrapper." `__getattr__()` is not taught anywhere earlier in the book either; [Metaprogramming](17_Metaprogramming.md) mentions the name once in passing, and [Surrogate](26_Surrogate.md) is two chapters ahead.

**Proposal:** change "`__getattr__()` delegates access." to:

> `__getattr__()` delegates access.
> Python calls it only when ordinary attribute lookup fails,
> so a name the wrapper does not have, such as `val`, falls through to the inner object.

Then, in "Eager Creation", the existing sentence "It answers for every name Python fails to find on the wrapper" becomes a reminder rather than the first statement, which is the right order.

**Cost:** none.

---

## 7. Retitle "Singleton Classes"

**Kind:** structure
**Where:** section heading at line ~494
**Problem:** every section in "The Classic Implementations" is a singleton class, so the heading does not say what distinguishes this one. The section is about a class decorator, and its most interesting content is the two ways the decorator breaks (`isinstance()` and subclassing both fail with errors naming a class the reader did not write).

**Proposal:** retitle to `### Singleton by Class Decorator`.

*Alternatives:* `### A Class Decorator` (matches the neighbouring `### Overriding \`__new__\`` in brevity), or `### Singleton by Decoration` (parallel to the existing `### Borg: Singleton By Inheritance`, which is the closest match in the chapter).

**Cost:** the auto-slug changes from `#singleton-classes` to `#singleton-by-class-decorator`. Nothing links to it today (`heading_links.py` passes now and found no reference), but check after the change.

---

## 8. Name double-checked locking, since the reader will think of it

**Kind:** teaching
**Where:** section "Tests, Threads, and Locks", after "That is the price of laziness under threads" (line ~215)
**Problem:** the chapter raises the cost ("Every call now acquires the lock, including the thousands that arrive long after the object exists") and offers one answer: create it eagerly. Any reader with C++ or Java behind them will immediately think of double-checked locking, which is the standard answer to exactly this cost, and will wonder why a chapter that just spent three notes on the race does not mention it. Note 3 says "The check must happen inside the lock", which reads as ruling the outside check out, when double-checked locking keeps both.

**Proposal:** add after "That is the price of laziness under threads":

> The classic escape is *double-checked locking*: test `_instance` before taking the lock, take it only when the test says the object is missing, then test again inside.
> The second test is the one note 3 insists on; the first exists to skip the lock once the object is there.
> It works, and it asks the reader to reason about which reads an interpreter may reorder, which is a bad trade for saving a lock acquisition.
> Eager creation is a better answer when the object can be built at import time.

The existing sentence "Eager creation is a better answer when the object can be built at import time" then moves into this block rather than being repeated.

*Alternative, one sentence:* "This is where other languages use double-checked locking; in Python, eager creation or the module form is the better answer." This names the term so the reader recognises it and stops there.

**Cost:** none, but the first version deliberately declines to assert that double-checked locking is safe on the free-threaded build. I did not find a claim I would stand behind either way, so the proposed prose stays on the "do not make the reader reason about this" side rather than pronouncing on memory ordering.

---

## 9. Drop the `__main__` guard from `singleton_class_variable.py`

**Kind:** code
**Where:** `singleton_class_variable.py` (lines ~413-418)
**Problem:** every other listing in the chapter runs its demo at column 0. This one indents the demo under `if __name__ == "__main__":` while its `#:` marker sits at column 0 outside the block. Nothing imports the module, so the guard protects nothing, and the mismatch between the indented `print()` and the dedented marker reads as a mistake. Project memory's "Demo code must be top-level" says tested demos sit at column 0.

**Proposal:** remove the guard and dedent the four demo lines. Output is unchanged.

```python
x = SingletonClassVar("sausage")
y = SingletonClassVar("eggs")
z = SingletonClassVar("spam")
print(x.val, x is y is z)
#: ['sausage', 'eggs', 'spam'] True
```

**Cost:** none. Nothing imports this module; there is no `test_singleton_class_variable.py`. If the guard was deliberate, say why in a line of prose instead, since it is the only one in the chapter.

---

## 10. Prose pass: nine specific lines

**Kind:** prose
**Where:** throughout
**Problem:** small wording issues, each independent. Take or leave them individually.

- **line ~89**, "which is the extent that Python offers" → "which is as far as Python goes."
- **line ~91**, "so it buys no privacy" ("buy" is on the watch list) → "so it hides nothing."
- **lines ~91-93**, "it breaks any reference written inside a class body, which rewrites `m.__Settings` into a lookup for `_TheClass__Settings`" — "which" reads as if the breakage does the rewriting. Proposed: "and inside a class body the compiler rewrites `m.__Settings` into a lookup for `_TheClass__Settings`, which breaks the reference."
- **line ~193**, "even though acquiring and releasing genuinely changes that lock's state" — drop "genuinely."
- **line ~222**, "The rest of this chapter exists only because it demonstrates interesting techniques and insights." Proposed: "The rest of this chapter is here for the techniques it demonstrates, not because you need these forms."
- **line ~383**, "Note that `x is y` is `False` for the wrappers, and `x is y is z` is `True` when the inner object is produced." The two halves name different listings without saying so. Proposed: "In the two wrapper versions above, `x is y` is `False`. Here, where `__new__()` produces the inner object directly, `x is y is z` is `True`."
- **line ~554**, "Only the first constructor call produces the construction of a `Registry` object." Proposed: "Only the first call constructs a `Registry`."
- **line ~642**, "when the line actually captures `Bar.__new__`" — drop "actually."
- **line ~645**, "`my_new()` returns an instance of `Bar` itself" — drop "itself"; the next two sentences already draw the contrast with the foreign object.

**Cost:** none.

---

## Already fixed directly (no decision needed)

- line ~276: "names an attribute that was never stored under that spelling" → "asks for an attribute that was never stored under that name". "spelling" is on the "Don't use" tier of the watch list.
- line ~156: "`@cache` is gone, because it is no longer what makes the object single" → "because it no longer makes the object single". The "is what" deletion test: the sentence means the same without it.
- line ~375: "so `x` is the shared instance itself, not a wrapper around it" → "so `x` is the shared instance, not a wrapper around it". "itself" as flourish; the following clause carries the contrast.

## Verified, no change needed

Recorded so a later pass does not re-check them.

- Every `#:` marker in the chapter matches real stdout. `ty`, `ruff`, and `pytest` all pass against `build/examples/24_Singleton`. `heading_links.py` and `banned_phrases.py` both clean.
- The unshown thread experiments in "Tests, Threads, and Locks" both reproduce: with a 0.05s constructor, 8 threads ran the constructor 8 times and got 8 distinct objects (8 of 8 runs); without the sleep, 20 trials produced no duplicates.
- `inspect.get_annotations(f, eval_str=True)` does raise a `NameError` for a quoted annotation naming a class defined inside the function, and the annotation is looked up in the enclosing scope, not the function's locals. Both claims confirmed on the pinned interpreter.
- `OnlyOne.__OnlyOne` written from outside the class does fail at runtime with `AttributeError` and passes `ty` silently. Confirmed against `ty` 0.0.63+ in a scratch project.
- The cross-reference to [Metaprogramming](17_Metaprogramming.md#intercepting-instance-creation) is accurate: that section's singleton overrides the metaclass `__call__()`, as this chapter says.
- The lowercase class name `singleton` in `singleton_class.py` is the book's established convention for decorators written as classes (`trace`, `count_calls`, `repeat` in chapter 14) and carries a matching `N801` per-file-ignore in `pyproject.toml`. Not a style drift.
- No hand-written `__init__()` in the chapter is an unexplained field-assigner. `singleton_borg.py`'s is explained at length; the rest carry singleton logic or exist to print.
