> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 25_Patterns--Surrogate (2026-10-13)

Nothing here needs your decision, so the file has no live blocks.
I read the chapter and its Solutions file against the 2026-09-29 review and `deep_review_db.md`,
and checked each claim against its listing and against the chapters it links (8, 10, 11, 19, 24, 29, 31).
Probes ran on `ty` 0.0.86 and Python 3.15.0 under `uv run`:
each `# type: ignore` removed (`call-non-callable` on `Partial()`, `invalid-argument-type` on `len(p)`, `unresolved-attribute` on `p.level`),
the misspelled `p.ff()` (no diagnostic),
`run(surrogate: Behavior)` (rejected, `Surrogate` lacks `f`),
`Behavior` on `Surrogate`'s parameters (`state_demo.py` passes, `StateA` rejected with the quoted message),
and the generic `Surrogate[T]` (`ty` reveals `Surrogate[StateA]` and narrows `first` to `Implementation1`, rejecting both `change_to()` calls).
Runtime probes covered `copy` and `pickle` on an unguarded, a narrowly guarded, and a fully guarded proxy, and `Service.register()` on a runtime-checkable `Protocol`.
Every checker claim and every runtime claim in the chapter held.
`tip verify-ch CH=26 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after.

## Applied directly

Chapter:

- "Forwarding with `__getattr__()`": the paragraph opening "`proxy_interface.py`'s abstract base class still guards the implementation side" read as though the `__getattr__()` proxy kept that check, but `proxy_getattr.py` annotates `impl` as `Any`. It now says a `__getattr__()` proxy can keep the check by annotating its parameter `Service`, as `proxy_interface.py` does.
- Same place: the paragraph carried three explanations (the implementation side's check, the unchecked calls on the proxy, the proxy passing as a `Service`). Split at both seams, one paragraph each.
- "The Recursion Trap": "do not include the guard" is now "leave the guard out" (positive form).
- `weakref.proxy()` paragraph: Cleanup's reliable alternatives use `weakref.finalize()` as well as `weakref.ref()`; the sentence named only `ref()`. It now names both, and "Both come from the same module" became "All three", since three tools are named.
- Exercise 3: the three-clause "and ..., and ..." sentence is two sentences. The Solutions quote follows through `tip statements`.

Solutions:

- Exercise 1: "a property on the proxy" is "a property of `Lazy`", found "on the class", which is why lookup succeeds without the fallback.
- Exercise 5: the "Refuse use after release" paragraph described a `RuntimeError` the demo never showed. The demo now ends with `c1.query("select 3")` under `expected(RuntimeError)`, marker `[RuntimeError] connection already released`, and the paragraph points at it.
- Exercise 7: "Both are `Any`, because `__getattr__()` delegation deliberately leaves the implementation's type untracked" contradicted the chapter, which says the `Any` on the parameters is a choice, made so one surrogate accepts any implementation. Now says that. "a set shape" became "one shape", since `methods()` returns a `set` two paragraphs up.

## Considered and declined

- **Opening: "*Proxy* is a special case of *State*."** The closing section says *GoF Design Patterns* gives the two different structures. The chapter's claim is about the surrogate mechanism, and "One Surrogate, Two Intents" argues it; the two statements are consistent.
- **"Python calls `__getattr__()` for any name the proxy and its class lack, but not for the proxy's own attributes."** The second half restates the first in negative form, but it names the proxy's own attributes, which the next sentence depends on. Left.
- **The `StateA`/`StateB` stand-ins are introduced twice** (before `test_state.py` and in the `Any` paragraph after it). The second mention is the callback the `ty` rejection needs, a whole listing later.
- **Solutions exercise 4 renames the proxy `BrokenProxy`** where the exercise says to edit `counting_proxy.py`. The 2026-09-29 review accepted this; the solution reproduces the edited class in one file so the `RecursionError` can carry a marker.
- **Earlier declined items** (moving "What Proxy Solves" ahead of the mechanism, `weakref.proxy()` as a smart reference, the single-underscore listings, blank lines between methods, hand-written `__init__()`) stand as recorded in `~25_Patterns--Surrogate.md`.

## For the session

- `tip verify-ch`'s solutions-sync regenerated `Solutions/25_Patterns--Surrogate/exercise_5.py` from the edited README; that file belongs in the same commit.
- No NEW `exercise_refs` or `quoted_diagnostics` hits. `tip prose CH=26` reports 0 new hits in every check.
