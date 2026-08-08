[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

[] Reject
**Line 289 and line 733 — the thread caveat does not survive into the
recommendations.**
Line 289 says "Modules and cached factories should cover your singleton
needs" immediately after four pages showing that a cached factory hands eight
threads eight different objects. Line 733's summary bullet repeats it:
"If you want a class, hide construction behind a cached factory (`@cache`), or
override `__new__()`."
A reader who skims to "Which Should You Use?" gets the racy recommendation
with none of the qualification.
Proposed: line 733 becomes

    - If you want a class, hide construction behind a cached factory
      (`@cache`), or override `__new__()`.
      Under threads, prime the factory at import time or use the module form.

and line 289 gains ", primed at import time if threads are involved," after
"cached factories". Also note that the summary's "override `__new__()`" is
ambiguous between the two `__new__` listings, and only
`singleton_class_variable.py` returns an instance of its own class; naming that
one would help.

[] Reject
**Lines 165-174 (note 2) — the recommended fix is never shown.**
Note 2 ends with "create it eagerly instead: call `settings()` once at import
time, or use the module form", and the section then spends two full listings
on the race (`singleton_cached_race.py`) and on the lock
(`singleton_locked_settings.py`), and closes at line 273-283 by saying "Eager
creation is a better answer when the object can be built at import time." The
answer the section twice recommends is the only one with no code.
Proposed: a three-line listing right after `singleton_locked_settings.py`,
e.g.

    # singleton_eager_factory.py
    from dataclasses import dataclass, field
    from functools import cache

    @dataclass
    class Settings:
        data: dict[str, str] = field(default_factory=dict)

    @cache
    def settings() -> Settings:
        return Settings()

    settings()  # Build it before any thread can race for it
    print(settings() is settings())
    #: True

with one sentence saying that the import system's own once-only guarantee is
what makes the priming call safe, which is the same guarantee the chapter
opened with. Placement and whether the chapter wants a fourth listing here is
your call, which is why this is a proposal rather than an edit.

[] Reject
**Lines 501-547 (Borg) — every Borg subclass shares one namespace, and the
chapter does not say so.**
Line 513 sells the design as "you reuse *Borg* through inheritance", and
`_shared_state` is a single `ClassVar` on `Borg`, so two unrelated subclasses
share it. I verified:

    class A(Borg):
        def __init__(self, v): super().__init__(); self.val = v
    class B(Borg):
        def __init__(self, v): super().__init__(); self.val = v
    a = A("apple"); b = B("banana")
    print(a.val, b.val, a.__dict__ is b.__dict__)
    #: banana banana True

`A("apple")` loses its value to `B("banana")`. This is the near-miss a reader
writes the moment they take the chapter's advice to reuse Borg by inheriting,
and Martelli's own article (already linked at line 503) makes the point: each
subclass that wants its own state declares its own `_shared_state = {}`.
Proposed: two sentences after the dataclass warning, plus the one-line fix
(`class Singleton(Borg): _shared_state: ClassVar[dict[str, Any]] = {}`).
Whether that earns a second listing or just prose is your call.

[] Reject
**Lines 743-759 (Exercises) — the set covers the first two sections and skips
the rest.**
Exercise 1 is Lazy vs. Eager, exercise 2 is the cached factory, exercise 3 is
"rewrite one of the class-based singletons as a module", exercise 4 is the
module rebinding trap. Nothing touches the threading section — the longest and
most consequential stretch of the chapter, with two listings, a lock, a
`global` lesson, and double-checked locking — and nothing touches Borg, the
class decorator, or the metaclass.
Proposed: add one exercise on the race, which is answerable purely from the
chapter, e.g.

    5.  Add a `threading.Lock` *inside* `settings()` in
        `singleton_cached_race.py`, wrapping only the body of the cached
        function, and run it. Explain why the object count does not drop to
        one, then fix it without a lock.

and optionally one on Borg:

    6.  Give `singleton_borg.py` a second `Borg` subclass and construct one of
        each. Explain the value you get back, and change the code so the two
        subclasses keep separate shared state.

The Borg exercise depends on the Borg finding above being applied.

[] Reject
**Lines 120-122 and 343 — name mangling is used 220 lines before it is named
and linked.**
Line 120 says "At module level nothing is mangled ... the compiler rewrites
`m.__Settings` into a lookup for `_TheClass__Settings`". That is the first use
of the mechanism in the chapter, and it arrives with no definition and no
link. Line 343, in a later section, then says "This is
[name mangling](11_Testing.md#white-box-and-black-box-tests)", which is where
the reader who was confused at line 120 finally gets the term.
Proposed: move the link to first use, so line 120-122 reads
"At module level nothing is
[mangled](11_Testing.md#white-box-and-black-box-tests), so it hides nothing,
..." and line 343 becomes plain "This is name mangling." That keeps exactly
one link to chapter 11's anchor (see the Cross-chapter note below) and obeys
"nothing used before it is taught".
Alternative if you prefer the explanation to stay where the nested class makes
it concrete: keep line 343 as it is and add "(explained under [name
mangling](...) below)" at line 120. I recommend the first.

[] Reject
**Lines 663-668 — the two metaclass singletons behave differently on repeat
construction, and the pointer to chapter 17 does not say so.**
This chapter's `singleton_metaclass.py` replaces `__new__`, so `__init__` runs
on every `Bar(...)` and `val` ends up `"spam"` — which lines 716-725 make a
point of. Chapter 17's `Singleton` metaclass overrides `__call__` and returns
the cached instance *without* calling `type.__call__`, so `__init__` does not
re-run and the first construction's arguments win. Same problem, same tool,
opposite answer to "do my constructor arguments take effect?", and the chapter
sends the reader to 17 with "shows another metaclass singleton" and no warning.
This is the chapter's own lookalike pair, and it is the one behavioral
difference a reader would actually be bitten by.
Proposed: after "shows another metaclass singleton, one that overrides
`__call__()`", add

    Overriding `__call__()` skips `__init__()` on every later construction,
    so the first call's arguments win;
    the version here replaces `__new__()`, so `__init__()` reruns and the
    last call's arguments win.

That also joins up with line 626-630, which already warns that a caller whose
arguments are discarded "is holding an object configured by someone else" —
the `__new__` form has the mirror-image bug, where the arguments are not
discarded and silently overwrite everyone else's.

[] Reject
**Line 147 — "which means a `Protocol`" is stated as the only exit.**
"The signature must name something reachable, which means a `Protocol`."
A `Protocol` is one exit; `-> Any`, a module-level `_Settings` the annotation
can name, or simply not nesting the class are the others, and the paragraph
just spent five lines arguing that nesting buys nothing anyway.
Proposed: "The signature must name something reachable, so nesting costs you
either the annotation or a separate `Protocol` to name in its place." Or keep
the sentence and add "which is more machinery than the nesting saved."

[] Reject
**Lines 277-283 — the double-checked-locking paragraph is vague about which
interpreter it is warning about.**
"It works, and it asks the reader to reason about which reads an interpreter
may reorder, which is a bad trade for saving a lock acquisition."
Two things. First, "and" reads as addition where the sentence means concession;
"but" is the word. Second, "which reads an interpreter may reorder" leaves the
reader unable to check the claim. On a GIL build the unlocked `if _instance is
None` is safe, because `STORE_GLOBAL` publishes an already-constructed object
and no bytecode boundary falls between construction and publication; the
reordering worry is a free-threading (PEP 703) worry, and free threading is
exactly what makes a lazy singleton interesting in the first place.
Proposed:

    It works, but it asks the reader to reason about what a free-threaded
    interpreter may reorder, which is a bad trade for saving a lock
    acquisition.

with a link to whichever section of [Concurrency](19_Concurrency.md) covers
free threading, if there is one. This is one sentence, and it turns an
unfalsifiable warning into a checkable one.

[] Reject
**Lines 139-147 — the quoted-forward-reference discussion is written against
pre-PEP-649 Python.**
"Quoting the name, `def settings() -> \"Settings\"`, is the obvious approach.
It parses and runs because an annotation is evaluated only when something
reads it."
On the book's Python (3.15, PEP 649) the *unquoted* form behaves identically.
I verified it: `def settings() -> Settings:` with `class Settings` nested in
the body parses, runs, and returns an instance; `inspect.get_annotations(...,
eval_str=True)` then raises `NameError: name 'Settings' is not defined`,
exactly as for the quoted form. So the quoting is not what makes it parse and
run — laziness is — and the book's own style rule says "Forward references
need no quotes."
Proposed rewrite of the first two sentences:

    Nesting costs the return annotation as well.
    `def settings() -> Settings` still parses and runs,
    because an annotation is evaluated only when something reads it,
    and nothing has read this one yet.

The rest of the paragraph is correct and can stand unchanged. This also makes
the trap sharper: the reader does not have to do anything unusual (like
quoting) to walk into it.

[] Reject
**Line 300 — the section preamble describes only the first three of seven
subsections.**
"The classic approach takes control of creation by delegating to a single
instance of a private nested class."
That is true of Lazy Creation, Eager Creation, and Overriding `__new__`. It is
false of One Instance in a Class Variable (which explicitly drops the nested
class), Borg, the class decorator, and the metaclass. As written the reader
carries a wrong expectation into four sections.
Proposed:

    The first three take control of creation by delegating to a single
    instance of a private nested class.
    The rest reach the same guarantee by other means:
    a class variable, a shared `__dict__`, a decorator, and a metaclass.

That also gives the section an itinerary, which it currently lacks; the seven
subsections read as a list rather than an argument.

[] Reject
**Line 33 — `import_once.py` collides with chapter 6's example of the same name.**
`Chapters/06_Modules_and_Packages.md:63` already has a listing called
`import_once.py` that teaches exactly this: two `import` statements, one
execution of the body, `sys.modules` as the cache. This chapter's
`import_once.py` re-teaches the same mechanism under the same filename.
Nothing breaks (the two live in different `Examples/` directories and
`validate_output.py` clears `sys.modules` between blocks), but two examples
with one name are a hazard for the reader searching the repo, and
`thinking-in-python-skill.md`'s own advice is to give a widely-used name
something distinctive.
Proposed: rename this chapter's block to `module_singleton.py`. That is not a
safe unilateral edit during a parallel review, because the rename orphans
`Examples/24_Singleton/import_once.py`, which `extract_examples.py`'s check
mode then fails on until `make prune-examples` runs. If you take it, the
sequence is: change the `# import_once.py` first line in the fence, then
`make sync && make prune-examples`.
I did add the back-link to chapter 6 (line 13), which was the other half of
this gap.
[[Also modify the build system to ensure every file name is unique]]

## Cross-chapter

**Chapter 11 (`11_Testing.md`).** `24_Singleton.md:343` links to
`11_Testing.md#white-box-and-black-box-tests` for the definition of name
mangling, and chapter 11's reviewer flagged a proposed move of that section. If
that section moves or is retitled, this link and (if the "name mangling used
before it is taught" finding above is applied) a second link at
`24_Singleton.md:120` both need the new anchor. No change should be made in
chapter 11 on this chapter's account; this is only a note that the anchor is
load-bearing from here. Chapter 11 is also the only place in the book that
defines the term, so if the target section is split, the half that keeps
`name_mangling.py` is the one this chapter needs to point at.

**Chapter 6 (`06_Modules_and_Packages.md`).** No edit needed there. Chapter 6's
untitled opening section holds the original `import_once.py`; this chapter now
links to `06_Modules_and_Packages.md` with no anchor, because that material
sits above chapter 6's first `##` heading. If chapter 6 ever grows a heading
over that material, this chapter's line 13 link should gain the anchor. See
also the filename-collision finding above, which is resolvable entirely inside
chapter 24 plus a `make prune-examples`.
