> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 17_Techniques--Metaprogramming (2026-09-29)

I checked each claim against its listing, the sections it links in chapters 8, 9, 12, 13, 14, 20, 27, and 28, runtime probes on the pinned 3.15.0rc2, and type probes under `ty` 0.0.84, Pyright 1.1.414, and mypy 2.3.1.
One claim was false, the one about what `ty` does with a `type()` call, and it is corrected below.
The block asks whether the listings should follow.
`tip verify-ch CH=17` passes 24 of 24.

## Applied directly

Chapter, corrections:

- "A Family of Generated Classes": the prose said `ty` "cannot follow a class built by `type()`" and "checks nothing about the generated class". `ty` 0.0.84 reads the bases and a dict-literal namespace: `new_cls(1, 2, 3, 4)` draws `too-many-positional-arguments` against `init()`, `inst.hour` reveals `int`, and `inst.nothing` is `unresolved-attribute`. The revealed type `<class '<unknown>'>` has an unknown name, not an unknown class. The Pyright half left out which constructor it checks: Pyright builds the class from the bases alone, so it checks calls against `Event`'s three-argument constructor and ignores `init()`. mypy reveals `type` and `Any`, as the prose said. The paragraph now says what each checker does, and gives the `cast()` the reason that still holds: every checker sees the `EventMaker` signature.
- "`@dataclass_transform` Is a Claim", closing paragraph: it cited the `type()` listings' `cast()` as the case the checker cannot see. It now cites `commander.py`, whose class exists only as text in a string, which holds under all three checkers.
- "Building Each Class on First Lookup": "a generated class doing something a plain string could not" overstated the case, since `e.action == "RingBell"` prints the same marker. Now says what the subclass adds: the event carries its kind as its type, where `isinstance()` or a `match` class pattern can test it. The next paragraph's "has no class left to check against" ended on a preposition; now "has no `RingBell` class for `isinstance()` to test".
- "A Descriptor That Learns Its Name": "calls `__get__()` again, forever" is now "until Python raises a `RecursionError`" (probed). "assigning `p.greet = something`" pointed at `p`, which is a `Point` in the listing above it; now "assigning to `greet` on a `Person` instance".
- "Intercepting Instance Creation": "a subclass must write `class ASingleton(metaclass=Singleton[ASingleton])`" called `ASingleton` a subclass of `Singleton`. It is a class `Singleton` builds. Now "each class must write".
- "Multiple Inheritance and Metaclasses": "`class X(dict, type): pass` fails the same way with no metaclass involved" named a class that inherits `type`, so it is a metaclass. Now `class X(list, dict)` (probed, same `TypeError`), "and neither base is a metaclass".
- Same section: "`expected` prints the exception through the helper, wrapped so it fits the page; the message is Python's, unwrapped" read as two helpers. Now "The `expected()` helper wraps the message across three lines to fit the page; Python reports it as a single line."
- "When You Still Need a Metaclass": `IterableMeta.__iter__()` yields values (`v for k, v in ...`), not names. "the three names" is now "the three values", quoted as strings.
- "The Core Functions": "`display_object()` combines three of these functions" counted `get_annotations()`, which the bullet list above it does not contain. The sentence now introduces `get_annotations()` in a clause.

Chapter, teaching:

- "A Descriptor That Validates": `Positive.__get__()` has no `obj is None` branch, so `Rectangle.width` raises `AttributeError: 'NoneType' object has no attribute '_width'` (probed). A reader copying `Positive` gets that on the first class-level read. Added a four-line paragraph naming the omission and pointing back at `Field`. The listing is unchanged; the alternative, adding the branch, needs a `float | Positive` return type or two overloads, a second topic in a listing about validation.

Chapter, style:

- `type` is now `type()` wherever the prose calls it, the section heading included. The anchor `#generating-classes-with-type` is unchanged, and no other chapter links to it.
- `ty` takes backticks in the four places it lacked them, and "pyright" is "Pyright", as in the rest of the book.
- `hook_order.py`: `def tag[T: type](cls: T) -> T` is now `def tag[T](cls: type[T]) -> type[T]`, the form chapter 14's `register()` and this chapter's two `model()` decorators use.
- Dropped "really", "just", "plain" (twice), "exactly", and "honest" where the sentence reads the same without them, and joined a sentence that carried two colons.

Solutions:

- Exercise 5: `describe(func)` had no parameter annotation. Now `func: FunctionType`, which covers the `def` and the lambda it is called on.
- Exercise 6: the quoted diagnostic lacked the ` --> metaclass_layout_conflict.py:6:21` line that `ty` 0.0.84 prints under `info:`. Added.
- Exercise 3: "where a type checker rejects a zero-argument `super()`" holds for `ty` and mypy and not for Pyright, as the chapter says. Now names `ty`.
- Exercise 1: italics on "it" were emphasis. Exercise 10: dropped "exactly".

## Findings for your decision

### Drop the two `cast(EventMaker, ...)` calls, now that `ty` checks the signature

`eager_event_classes.py` ends `make()` with `return cast(EventMaker, new_cls)`, and `greenhouse.py` has `maker = cast(EventMaker, new_cls)`.
Under `ty` 0.0.84 both listings pass with the cast removed (`return new_cls`, `maker = new_cls`).
`ty` compares the class it built from the `type()` call with `EventMaker` and accepts it.
With a third parameter added to `init()` it reports `invalid-return-type` and names the extra parameter (probed).
So under the book's checker the cast replaces a check with a claim, which is the distinction "Where Enforcement Lives" teaches.

What removing them costs:

- Pyright rejects `return new_cls` ("Type `type[_]` is not assignable to return type `EventMaker`"), since it gives the class `Event`'s constructor. That is two new entries in `tools/data/pyright_baseline.txt`. mypy accepts either form.
- The paragraph I corrected would change again, to say that `ty` verifies the signature and that Pyright needs the cast.
- `commander.py`'s sentence "the same idiom `greenhouse.py` uses for `EventMaker`" goes, and `greenhouse.py` keeps its `cast` import for `cast(type, ...)` in `run_events()`.
- `ty`'s changelog has carried dynamic-class entries since 0.0.52, so the inference is not new, but the tool is pre-1.0 and the probe belongs in the `tool-upgrade` skill either way.

I recommend removing both casts and rewording the paragraph to match.
The listings get shorter, and the chapter's claim about who enforces what becomes something the reader can watch `ty` do.
I left them in because the chapter reports all three checkers' behavior in several places, and with the casts the listings pass all three.

`[] Reject`

## Considered and declined

- `greenhouse.py`'s `name : NOT_CREATED  # Dict key : value` has a space before the colon, against PEP 8. The comment shows it is deliberate, separating a dict entry from the annotations around it in the class body.
- "CPython allows multiple inheritance only when at most one base carries a nontrivial layout" simplifies the rule: two bases whose layouts extend one another combine. Every case a reader meets in this chapter is two unrelated built-ins, where the simplification holds.
- "Generated Classes Cannot Be Pickled" says `LightOn` gets `__module__` set to `eager_event_classes`. That holds when the listing is imported, which is how the probe and any pickling caller reach it; run as a script the module is `__main__`, and pickle fails the same way.
- The intro links chapter 20 for `abc.ABC`, though chapter 13 uses `ABC` first. The link is to where the book explains it, and "You have used metaclasses already" holds because of chapter 13.
- The bullet list in "When You Still Need a Metaclass" and the sentence under it both name `EnumType` and `for c in Color`. The repetition reintroduces the listing after a three-item list; cutting either leaves the listing without its lead-in or the bullet without its example.
- No exercise covers "Where Enforcement Lives" or the validating descriptor. The ten exercises reach every section that has a hook in it, and the chapter is already one of the book's longest.
