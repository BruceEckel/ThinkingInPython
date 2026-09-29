> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 26_Patterns--Surrogate (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the chapters it links (8, 10, 11, 19, 24, 29, 31), the GoF text for *Proxy* and *State*, and probes on the pinned interpreter.
The probes covered `ty` 0.0.84 with each `# type: ignore` removed, Pyright 1.1.414 and mypy on `len(p)`, `copy`/`pickle` on a guarded and an unguarded proxy, `register()` on a `Protocol` and on an ABC, and a `__class__` property.
Every checker claim and every runtime claim in the chapter held.
`tip verify-ch CH=26` passes 24 of 24.

## Applied directly

Chapter, corrections:

- Opening: "This is the shape in *GoF Design Patterns*" described the shared-base figure as GoF's shape for both patterns. GoF gives that structure to *Proxy* alone (its *State* has a Context that shares no interface with the states), and the chapter's closing section says the two structures differ. Now "the shape *GoF Design Patterns* gives *Proxy*".
- Opening: "*State* holds several and switches among them." `state_surrogate.py` holds one implementation at a time. Now "*State* switches among several."
- "Forwarding Writes": "The implementation attribute no longer needs a double underscore" stated a need that had not changed. The paragraph now says `WriteProxy` uses one underscore because of the string-literal problem, and states the cost: an implementation's own `_implementation` is out of reach through the proxy.
- "The Recursion Trap": `copy` and `pickle` "look up `__setstate__()` before `__init__()` has run" implied `__init__()` runs later. Now "on an instance whose `__init__()` has not run".
- "What Proxy Solves", item 4: "implementing the *copy-on-write* idiom and preventing aliasing" named copy-on-write without saying what it is, and exercise 3 depends on it. The item now defines it in two clauses.
- `weakref.proxy()` paragraph: "neither needing this one" had two candidates for "this one" (the module, the function). Now "neither needs `weakref.proxy()`". Dropped "own" from "The standard library's own".

Chapter, teaching:

- "Forwarding with `__getattr__()`": added the near-miss that the lost static check allows. A misspelled `p.ff()` passes the checker and fails at runtime with the implementation's `AttributeError` (probed).
- "Protection Proxy": added that the protection is a convention. `guest._doc.erase()` reaches the document without asking the proxy, so the proxy guards against mistakes. A reader meeting "protection" could otherwise take it for enforcement.
- "State": the paragraph about the `Any` annotations sat between `state_surrogate.py` and `state_demo.py`, and discussed `Behavior`, `first: Behavior`, and `test_state.py` before the reader had seen any of them. It now follows `test_state.py`, after all three listings. Its opening "`Surrogate.__init__()` and `change_to()` are a choice" made the methods the choice; it now says the `Any` on their parameters is the choice, and that `__getattr__()` returns `Any` because it answers for any name.

Chapter, prose:

- "A *Surrogate* Is Not Its Implementation": two paragraphs after the listing said the same thing twice (the call works, `hasattr()` is `True`). Merged. The three-line preview of the protection proxy's `PermissionError` became a pointer to that section, which explains it in full.
- "Protection Proxy": "does not return `False`, it raises `PermissionError` too" was a comma splice. Rewritten as one clause.
- Section openers "A *Virtual proxy*", "A *Protection proxy*", "A *Smart reference* proxy" carried a capital mid-sentence. Lowercased, matching the "*virtual proxy*" later in the chapter.
- Exercise 3 read "Create a simple copy-on-write implementation." It now names what to build and what to confirm, matching the solution.

Solutions:

- Exercise 1 asks to extend `virtual_proxy.py`'s `Lazy`, and the solution defined `LazyProxy` over `ExpensiveResource`. Renamed to `Lazy` and `Expensive`, with the chapter's `query()` and message.
- Exercise 2: the `#:` markers sat at the end of a top-level demo. Each now follows the statement that printed it.
- Exercise 3: `Box` hand-wrote a field-assigning `__init__()`. Now a `@dataclass`. Dropped "exactly what 'copy-on-write' means".
- Exercise 5: the exhausted-pool demonstration was a `try`/`except` printing `e`. Now `expect(PoolExhausted, pool.acquire)`. Added the sentence the exercise's "modeled on *Singleton*" asks for: `Pool` builds every `Connection`, the limit raised from one to `POOL_SIZE`.
- Exercise 6 asks to give `dunder_bypass.py`'s `Proxy` a `__len__()`, and the solution's `Proxy` built its own `Words()` in a no-argument constructor. It now takes `impl`, as the chapter's does. The explanation's "which only runs when an instance lookup fails" is restated in order: the lookup skips the instance, so nothing fails, so `__getattr__()` is not called.
- Exercise 7: "It must compare the type of the value" read as the checker's obligation. Now "The decision compares ..., and the checker knows neither".

## Considered and declined

- **Move "What Proxy Solves" ahead of the mechanism sections.** Motivation-before-mechanism argues for it. The chapter's second paragraph block already lists what the indirection provides (refuse, delay, count, swap), and the three proxies in that section are written with `__getattr__()`, so they need the mechanism first.
- **`weakref.proxy()` "solves none of these four".** It checks its referent on every access, which is close to GoF's smart reference. The sentence draws the line at purpose (it exists to avoid keeping an object alive), which is defensible.
- **Exercise 5's `ConnectionProxy` raises `RuntimeError` from `__getattr__()`,** which breaks `hasattr()` the way the chapter's protection proxy does. That is the chapter's own design for a refusing proxy, so the solution stays.
- **The guard listing and later listings use one underscore where `proxy_getattr.py` mangles.** The guard works with a mangled name too. `counting_proxy.py`'s prose explains the single underscore, and the "Forwarding Writes" paragraph now gives the reason at first use.
- **Blank lines between methods** appear in `dunder_bypass.py` and `counting_proxy.py` and not in the other listings. Both are within the one-blank limit.
- **Hand-written `__init__()` in every wrapper**: standing exemption in `deep_review_db.md`.
