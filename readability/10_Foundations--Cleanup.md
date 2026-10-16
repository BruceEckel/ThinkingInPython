> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/10_Foundations--Cleanup.md`, 2026-10-16.
The chapter has been through a deep review, the 2026-10-13 prose pass, a straighten pass, and a metadiscourse pass, and it carries almost no AI-writing tells:
no Tier 1A vocabulary, no stacked transitions, no generic conclusion, and every watch-list absolute it keeps states a guarantee.
One edit was applied directly.
One block remains, about the chapter's last sentence, which only Bruce can settle because it turns on what the registry is for.

## Applied directly

- Line 47, repeated connective: the sentence after "so every `Counter`'s reference count stays above zero" opened with a second "So"; "So no `deleted` lines appear" -> "No `deleted` lines appear". The consequence still reads from the order of the two sentences.

## The Rule, last sentence: "the leak it exists to catch"

Line 593, §32 (aphorism formula) and §31 (manufactured punchline):

> To track objects without owning them, hold them weakly,
> so the registry cannot become the leak it exists to catch.

The closing kicker says the registry exists to catch leaks.
The chapter presents `weak_value.py`'s registry as a live-instance counter ("tracking which objects are alive without keeping them alive"), and never says its job is leak detection.
If that purpose is intended, the sentence is a fair close, and a reader who knows instance counters as leak detectors gets the irony.
If it is not, the sentence adds a claim the chapter does not make.
Proposed, reusing the chapter's wording from the `finalizer.py` discussion:

> To track objects without owning them, hold them weakly,
> so the registry leaves each object's lifetime as it was.

Reject this block to keep the current sentence as deliberate voice.

[] Reject

## Considered and declined

- Line 3, epigraph: "Python frees memory on its own, and a file, a socket, or a lock is not memory." The "and" joins clauses with different subjects and a contrast ("but" would fit). Kept: the epigraph is deliberate voice, and its two halves read as a pair.
- Line 114, §27 superlative: "the failure most likely to go unnoticed in production". Kept: the paragraph after `del_swallows.py` supports it point by point (nothing on stdout, exit status `0`, a stdout test passes).
- Lines 269, 186, 192, §34 "real": "a real `close()`", "a real program". Each contrasts with the toy listing beside it (recurring keep).
- Lines 469-471: "`WeakSlot` lists `__weakref__` among its slots, so its instances accept weak references. `finalize()` accepts the `WeakSlot` instance." Near-restatement by shape, but the second sentence applies the general rule to the listing and gives "The instance" in the next sentence its antecedent.
- Lines 517-519: the `WeakSet` aside sits before the paragraphs on `id(self)` and `live_count()`. Moving it after them was considered; kept where it is, since it answers "why a dictionary?" right after the listing, and the `id(self)` paragraph then answers "why this key?".
- Lines 582 and 591, §9/§32 "X, not Y" twice: "to catch the mistake, not to be the plan" and "as the backstop, not as the plan". Kept: the echo is deliberate and ties `weakref.finalize()` to the role the paragraph above gives the standard library's `__del__()`.
- Watch-list absolutes ("the only remaining references", "The only referrer", "runs only after", "only live objects", "correct only if", "Never release a resource in `__del__()`"): each states a restriction or a guarantee (recurring keep).
