When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

# Deep review: 26_Surrogate

Reviewed 2026-08-30, after the day's restructure (`b259f977`) and the
surrogate-first listing order (`2007d25b`). Every technical claim that can be
executed was executed: `copy.copy()` and `pickle` on both proxy shapes raise
`RecursionError`; `Service.register(Proxy)` and a `__class__` property both make
`isinstance()` answer `True`; `ty` rejects `len(p)`, `p.level = ...`, and
`run(Surrogate(...))` against `Behavior` exactly as the prose says, and reports
an unused `# type: ignore` as a warning, so every ignore in the chapter is
load-bearing. The underscore guard added to the trap paragraph was verified to
turn the typo into `AttributeError('_imp')` and to let both `copy.copy()` and
`pickle` round-trip a plain proxy and a `WriteProxy`. All markers match; the
full verify loop passes. Standing exemption applied: the hand-written
`__init__()`s on the wrapper stand-ins are deliberate and were not flagged.

## Applied directly

- Intro: added one sentence after "forwards all method calls to it" saying
  what the indirection buys (refuse a call, delay creation, count or log,
  swap), so the 360 lines of mechanics that follow have a stated reason.
  The chapter had opened on machinery with its motivation in "What Proxy
  Solves".
- Explicit Forwarding lead-in: "Implementing *Proxy* following the above
  diagram" became "The smallest *Proxy* drops the shared base and forwards each
  call by hand". `proxy_1.py` has no base class, so it does not follow the
  diagram, and the intro had just said the base is GoF's shape.
- State typing paragraph: "no matter how you annotate the surrogate" became
  "while the call reaches `f()` through `__getattr__()`". The checker is blind
  because of the hop, not the annotation; an explicitly forwarding proxy is
  checkable, as `proxy_interface.py` shows.
- Trap paragraph: added the standard cure, a guard at the top of
  `__getattr__()` that raises `AttributeError` for underscore names, with what
  it fixes (the typo now names itself; `copy` and `pickle` get the
  `AttributeError` their `__setstate__()` probe expects). The chapter and the
  exercise-4 solution both explained the recursion and neither said how to
  stop it.

## Findings

### 1. Show the GoF shape once: `class Proxy(Service)` in `proxy_interface.py`

The intro presents the diagram (surrogate and implementations derived from one
base) as "the shape in *GoF Design Patterns*" and promises "You'll see that
Python does not need the shared base", but no listing ever shows the shape it
is dropping. `proxy_interface.py` has the base, `Service`, and the explicitly
forwarding `Proxy`, yet `Proxy` does not inherit it.

Making it `class Proxy(Service)` with `@override` on `f()` and `g()` costs
three lines and buys two things. It shows the GoF structure once, so the
"does not need" claim is a comparison rather than an assertion. And it makes
calls *on the proxy* type-checked: `run(p: Service)` accepts a `Proxy`, which
is exactly the guarantee the State section later says the `__getattr__()` hop
loses ("Annotating `run(b: Behavior)` and handing it `b` is a type error").
That contrast is currently made against nothing; with this change it points
back at a listing.

Follow-through if accepted: the sentence at the top of "Forwarding with
`__getattr__()`" ("The abstract base class and the `Protocol` above still
guard the implementation side ... Calls on the proxy get no such check") gains
a clause noting that `proxy_interface.py`'s inheriting proxy did get that
check; the closing section's "the base class to state what they owe you"
stays true. `Solutions/26` does not reference `proxy_interface.py`.

The case against: the chapter's thesis is that Python needs no base, and
having the proxy inherit one, even once, softens that. I would still do it,
because the thesis is stronger when the reader has seen the alternative.

[] Reject

## Considered and declined

- **`impl: Any` → `impl: object` on the surrogate constructors.** `object` is
  the stricter type and every use is `getattr()`, which accepts it. Declined:
  it buys no checking (the `getattr()` result is `Any` either way), it would
  contradict the State section's "annotations that carry the implementation
  are all `Any`" paragraph, and `Any` here is the chapter's explicit subject
  rather than a leak.
- **A virtual-proxy (lazy initialization) listing.** The GoF list names it and
  the generic-proxy paragraph claims `__getattr__()` can do it, but no listing
  shows it. Exercise 1 asks for it and `Solutions/26` has it. The chapter
  already carries nine listings in the Proxy half; a tenth for a use the
  exercise covers is not worth the length.
- **Moving the `__getattribute__()` lookalike paragraph into "The Limits of
  `__getattr__()`".** It is a lookalike warning, not a limit of the hook, and
  it sits where `__getattr__()` is introduced, which is where a reader would
  confuse the two.
- **Dataclass forms for `Settings`, `Words`, `Guarded`.** Standing exemption:
  wrapper stand-ins whose one new thing is the pattern.
