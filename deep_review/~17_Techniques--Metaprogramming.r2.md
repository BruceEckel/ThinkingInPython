> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 17_Techniques--Metaprogramming (2026-10-13)

I checked each claim against its listing and the chapter 12 and 25 passages it cites,
with runtime probes on Python 3.15.0 (`uv run`) and type probes under `ty` 0.0.86, Pyright 1.1.414, and mypy 2.4.0.
Every checker claim held: `ty` reports `invalid-return-type` naming the extra parameter when `init()` gains one,
Pyright rejects `return new_cls` and accepts the zero-argument `super()` in `Singleton`,
mypy reveals `type` and `Any` for the generated class and keeps `B` for an `Any`-returning metaclass `__call__()`,
and the quoted `ty` messages (`subclass-of-final-class`, the read-only `age`, `conflicting-metaclass`, the exercise 6 diagnostic) match.
The runtime claims held too: `__module__` is `"builtins"` for the `exec()` class,
the `PicklingError`, `TypeError`, and `OSError` messages, `Rectangle.width`'s `AttributeError`,
the `RecursionError`, and the `__prepare__()` without `@classmethod` message.
The prior review's one block (drop the two `cast(EventMaker, ...)` calls) is in the chapter.
`tip verify-ch CH=17 ISOLATED=1` passed 27 of 27 before and after.
No live blocks.

## Applied directly

Chapter:

- "Building Each Class on First Lookup": "The alternative, a `make_event()` function, pushes the build-or-fetch decision into every caller" described a function that would hide the decision as well as `__missing__()` does. Now says what the alternative is: without `__missing__()`, every caller checks for the name and builds the missing class.
- Same section: "`NAMES` beside it" placed a module-level constant beside a class attribute. Now "the module-level `NAMES`".
- Same section, teaching: `run_events()`'s `cast(type, ...)` had no explanation. Added a paragraph: `EventMaker` is a callable, `isinstance()` requires a class, `ty` reports `invalid-argument-type` without the cast (probed), and every stored value is a `type()`-built class.
- "Generating Classes with `exec()`": the `namespace` annotation paragraph called the `__builtins__` entry "the second reason" without stating the first clearly. Now: the checker cannot see into the string, so `namespace` is `dict[str, Any]`; `exec()` also adds the built-ins dictionary, so `namespace` holds more than classes.
- Same section: the `super()` paragraph never said that the exec'd `__init__()` can call zero-argument `super()`, and repeated the `greenhouse.py` explanation from two sections earlier. Now states the consequence first and the `init()` contrast in one sentence.
- "Generated Classes Cannot Be Pickled" is now "Pickling Generated Classes" (no link targets the old anchor). The section raised the question of a remedy and left it open, and "It is not for storage or introspection" contradicted `display_object(MyList)` earlier in the chapter. Now: the rest of `inspect` works on these classes, and binding each class as a module attribute (`globals()[name] = new_cls`) makes the pickle round trip work while `getsource()` still raises an `OSError` (both probed). Dropped "but just as completely" to match. Added the mechanism for `"builtins"`: the class body's `__name__` lookup falls through to the built-ins.
- "Multiple Inheritance and Metaclasses": the paragraph after `mixin.py` repeated "has nothing to do with metaclasses" from the layout-conflict paragraph. Now one sentence: a metaclass that needs a `dict` holds one in an attribute and keeps `type`'s layout.
- "When You Still Need a Metaclass": the decorator-versus-`__iter__()` paragraph gave the conclusion before the lookup rule that causes it. Reordered: the rule, its consequence, then where a class-level protocol method lives.
- Same section: "It cannot change the name, the bases, or the namespace" overstated, since a decorator can rebuild the class. Now says the decorator runs after `type.__new__()` has used them, so changing them means building a replacement class.
- "A Descriptor That Validates": "A descriptor is justified when" (passive) is now "Use a descriptor when".

Solutions:

- Exercise 9: a raw newline had replaced the `\n` inside the code span `print("injected code ran")\n`, splitting it across two lines. Restored.
- Exercise 8: "the `bases` parameter of `__init__()` reports the tuple `__new__()` used" was wrong for the chapter's `new_vs_init.py`, whose `__new__()` builds a longer tuple than `__init__()` receives. Now "holds the same tuple `__new__()` received".
- Exercise 3: "present in the book" is now "present in the chapter's `singleton.py`".

## Considered and declined

- "They belong to distinct subclasses, and `isinstance()` tells them apart" follows a listing that tests `type(light) is type(water)`. True, and it sets up `run_events()`'s `isinstance()` test.
- "Where Enforcement Lives" interrupts the run of hooks between "Making a Class Final" and `__set_name__()`. It grows out of `@final` as a marker; moving it later separates it from the example that motivates it.
- "`@dataclass_transform` generalizes exactly one shape" stays: the watch-words baseline records it as a judged keep.
- `Rectangle`'s hand-written `__init__()` is the point of the listing: the constructor's assignments route through `Positive.__set__()`.
- Vale flags "is mirrored" (the term *mirrored machinery*) and "be undefined"; both read correctly as written.

## For the session

- `deep_review_db.md`, the "17_Techniques--Metaprogramming: the sentinel unions" exemption, says `greenhouse.py` annotates `EventMaker | NOT_CREATED`. `greenhouse.py` no longer has `NOT_CREATED`; only `utils/display.py`'s union still applies. Update the exemption.
- `tools/data/pyright_baseline.txt` lines 23-24 (`greenhouse.py`) quote `EventMaker | NOT_CREATED` and `type[_] | EventMaker`; Pyright 1.1.414 now prints `parameter "value" of type "EventMaker"` and `Type "type[_]" is not assignable to return type "EventMaker"`. `tip pyright-review` will show the delta.
- No NEW `exercise_refs` or `quoted_diagnostics` hits.
