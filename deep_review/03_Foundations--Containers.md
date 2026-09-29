> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 03_Foundations--Containers (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the ten chapters this one links (02, 04, 05, 12, 13, 16, 18, 19, 20, 22), the seven sentences in other chapters that cite this one, and the pinned interpreter (3.15.0rc2).
Probes confirmed the `Set changed size during iteration` message, the view operators, `frozendict` construction, order, and hashing, the `Counter` operators, and both unpacking messages.
The two timing listings ran three times each: list/deque ratio 82 to 93 against the `* 20` threshold, and membership gaps near 1,400 and 7,000 to 12,000.
Exercise 1's `n = 200_000` run took 5.8 seconds for the list, so "several seconds" holds.
`tip verify-ch CH=03` passes 24 of 24.

## Applied directly

Chapter, corrections:

- `setdefault()` paragraph: the sentence said `plain.setdefault(kind, []).append(name)` "returns the list". The whole expression returns `None`; `setdefault()` returns the list. Now "In `plain.setdefault(...)`, `setdefault()` returns the list".
- "Two List Traps": removing while iterating was "the same kind of surprise" as the shared row. The first is aliasing and the second is a skipped index. Now "the second surprise".
- `dict_iteration_trap.py` lead-in: "raises a `RuntimeError` instead of quietly skipping elements, as `remove_while_iterating.py`'s `list` does" let "does" attach to either verb. Split into two sentences, the `list` first.
- "A `list` has an operation for each of those four" followed a listing that ends on `maxlen`, a fifth thing. Now "A `list` can also add and remove at either end".

Chapter, teaching:

- "Lists" opens with the definition ("A `list` holds objects, of any kind, in an ordered, mutable sequence"), moved up from "Indexing and Slicing". The section used to open on the `for` statement.
- `list_traps.py` uses a comprehension, and the paragraph defining one sat a listing later. The definition now follows `list_traps.py` and says why the second grid works: `[0]` is evaluated three times. The remove-while-iterating advice points back to it.
- "Tuples and Unpacking": added the near-miss, "Without its comma, `(42)` is the integer `42` inside parentheses."
- "Dictionaries": the chapter said keys must be hashable and lists are not, with no reason. Added the mechanism: a hash that changed after insertion sends the lookup to a different slot. Exercise 4 asks for this explanation.
- "Sets": now says a set finds an item by its hash, so every item must be hashable. The chapter had stated that for `dict` keys alone.
- Dict views: the set operators appear here before the Sets section, so the paragraph now ends with a link to it.

Chapter, style:

- `membership_cost.py`: `def scan_gap(n: int) -> float` was the chapter's one annotated function. Now `def scan_gap(n)`, matching `min_max()`, `list_left_ops()`, and chapters 04 and 05.
- `defaultdict`: "The factory runs on the *read*" used italics for emphasis. Rewritten without them, and "Here, `list` produces..." moved up beside the factory definition.
- `queue.Queue` link now lands on chapter 19's "Coordinating Threads with Queues".
- Watch words and figures of speech: "even when the source is", "a value you never read", "both shout it", "earns a stable hash", "owns its contents outright".
- Exercise 1: cut "That is the point."

Solutions:

- Exercise 6: "The tally loop is the same length either way" was false. `counter.py` has no loop; `Counter(words)` counts in its constructor. The loop is now named as the first thing you write yourself.
- Exercise 6: dropped the `defaultdict[str, int]` annotation, which `ty` does not need and exercise 2's identical line does not carry.
- Exercise 10: "finds a key by hash and equality, never by identity" overstated it (CPython tries identity first). Now "so an equal key need not be the same object".
- Style: italic emphasis on "margin" (1); "exactly why" and "at all" (4); "two spellings" (5); "only take two operands" (3); "share one spelling", "has to be", "has to lose" (8); "never the intent" (9); "the property a `frozendict` key buys", "exactly as it is", "has to hash" (10).

## Considered and declined

- **`try`/`except` stays in chapters 02 through 04.** The chapter has seven `try` blocks that print `e`, and house style since 2026-09-16 is `expect()`. Chapter 05 is the first to import it, and chapters 02 and 04 use `try`/`except` the same way, so converting chapter 03 alone would put an unexplained helper ahead of its introduction.
- **Sets before Dictionaries.** Moving the Sets section up would remove the forward reference in the dict-views paragraph, but hashing is introduced under Dictionaries and chapters 02, 27, and 30 link these headings. The link to Sets costs one line.
- **View operators accept any iterable.** `ages.keys() & ["Bob"]` works, where `{...} & [...]` does not. The sentence ("against another dict's view or against any set") is true as written, and the extra case adds a lookalike the chapter has no use for.
- **"A dictionary key must be hashable, though it need not be immutable."** The example that answers it (an instance of an ordinary class hashes by identity) needs chapter 07.
- **Solution 1 hand-rolls `--numbers`.** Solutions listings can import `benchmark` since 2026-09-16, but Solutions 18, 19, and 23 hand-roll it too, so changing one breaks the set.
- **"compares all three"** (the link to chapter 22's "The Standard-Library Versions"). That section covers the data class and `NamedTuple` and contrasts `NamedTuple` with `namedtuple()` in two sentences. Close enough to leave.
- **Listing comment "Immutable containers are hashable"** in `immutable_containers.py` overstates by itself, and "Shallow Immutability" qualifies it two sections later. Existing comment, left alone.
