> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 03_Foundations--Containers

The chapter carries no AI-writing tells: no vocabulary clusters, no curly quotes or spaced `--`, no metadiscourse, and every claim tied to a listing.
Four small sentence-level fixes were applied directly, three of them "and" joins between clauses with different subjects.
This file holds no live block, so it is the record of the applied changes and of what was examined and left alone.

## Applied directly

- Line 374, "and" joining a second claim with a new subject: "follows insertion order, and the language guarantees that order" -> "follows insertion order, which the language guarantees".
- Lines 406-407, "and" joining two clauses with different subjects (the second is the consequence): "each key unpacks into its two letters and the loop runs to the end with ..." -> two sentences, "each key unpacks into its two letters. The loop runs to the end with ...". Checked against `forgot_items.py`, which prints `B o` and `A l`.
- Lines 542-544, "and" joining two separate claims with different subjects: "The methods accept any iterable ..., and `union()`, `intersection()`, and `difference()` take several arguments at once" -> two sentences, the second "`union()`, `intersection()`, and `difference()` also take several arguments at once". Checked against `set_methods.py`'s `a.union(b, [6, 7])`.
- Line 975, echo of "too" from the sentence before ("unhashable too" then "immutable too"): "when every nested object is immutable too" -> "when every nested object is also immutable".

## Considered and declined

- Line 9, "`in` and `len()` work on all of them, and slicing works on the sequences": an "and" between different subjects, but splitting it made a run of five short sentences in the opening paragraph, and the "and" reads as additive (two facts about what works on the containers). Tried and reverted.
- Line 10, "Lists, tuples, dictionaries, and sets are fundamental data types": portable by the §1 test, but it names the four types the chapter covers and closes the opening paragraph, so kept.
- Line 147, "Two list operations produce surprises." under `### Two List Traps`: §29 restates its heading by shape, but "the second surprise" at line 179 depends on it, so kept.
- Lines 804-806, "Appending five values ... keeps the last three. A `deque` with a `maxlen` is a sliding window. A `list` has no equivalent.": three short sentences, but each makes its own claim and the run does not inflate the tone (§31 needs both), so kept.
- Line 975, "Immutability is beneficial": a mild, general verb, but the `because` clause right after it says what the benefit is.
- Line 336, "the slot where the entry lives": a figure by shape, but the standard idiom for a hash-table slot, and the sentence names the mechanism (reducing the hash to a slot).
- Line 207, "Tuples are the natural way to return several values": a stance word, not a §7 term, and the listing's `min_max()` shows the use.
- Lines 696, 1008, "plain": against `defaultdict` and against `frozenset`, the named-contrast keep; line 696 also names the listing's `plain` variable.
- Line 698, "already stored under `kind`": temporal, the keep for "already".
- Line 987, "only when": a shape ruled fine on 2026-10-04.
