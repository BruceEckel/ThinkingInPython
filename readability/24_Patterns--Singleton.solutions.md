> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Singleton, Solutions

The Solutions file for chapter 24 carries no Tier 1 or Tier 2 vocabulary,
no signposting, no significance inflation, and no curly quotes.
The nine changes below split "and" joins between clauses with different
subjects, merge two sentences in exercise 5 that stated the same timing
twice, cut one sentence in exercise 6 that the next paragraph repeats,
and rewrap two paragraphs broken mid-line by an earlier edit.
The claims next to the edits were checked against the listings and the
chapter: `functools.cache` stores the result of whichever call finishes
last, `singleton_locked_settings.py` and `singleton_eager_factory.py`
exist in the chapter, and chapter 17's metaclass keeps `_instances`.
This file holds no live block, so it is the record of the direct edits.

## Applied directly

- Line 338, "and" joining different subjects: "Whichever import comes first runs the body, and the other finds `config` in `sys.modules`" -> two sentences.
- Line 355, "and" hiding a consequence: "But each module now reads a different dict, and the sharing has ended." -> "But the sharing has ended. Each module now reads a different dict."
- Lines 472-473, "and" hiding a consequence: "the eight constructors overlap and the whole run takes about 50 milliseconds. With it they queue, and the run takes about 400." -> ", so the whole run takes ...", ", so the run takes about 400". (Close alternative: periods, which turned the pair into four clipped sentences.)
- Lines 495-497, treadmill (repeated timing): "before the second pool starts any worker thread. By the time the second `ThreadPoolExecutor` starts its workers, every call to `primed()` is a cache hit." -> "before the second pool starts any worker thread, so every call a worker makes to `primed()` is a cache hit."
- Lines 601-602, "and" joining two claims with different subjects: "overwrites a value belonging to `Singleton`, and nothing reports the overwrite" -> two sentences.
- Line 614, pointer with a distant antecedent: "`Separate`'s instances share that dict among themselves" -> "The instances of `Separate` share its dict among themselves", since "that dict" sat two sentences from `Separate`'s dict, after "that one line".
- Line 622, after it (old line 623), treadmill: cut "The subclasses that leave it alone keep sharing the inherited one.", which the next paragraph says in full ("Any subclass that leaves `_shared_state` alone writes into `Borg`'s dict").
- Lines 624-627, wrap: "*Borg*" stood alone on its line; rewrapped the paragraph at about 70 columns.
- Lines 704-707, "and" hiding a contrast: "The object is single, and every caller who constructs it resets its state." -> two sentences; the paragraph's broken wrap ("The trace" and "The" alone at line ends) rewrapped.

## Considered and declined

- Lines 371-373, "A name and the object it refers to are different things, and every singleton built on module state depends on that difference. Mutate through any name, rebind only through the module.": §32 maxim by shape, but it is advice the exercise has just earned, and no "but", "so", or "while" fits the "and".
- Lines 291-294, "Everywhere else, the module is the simpler tool.": restates the paragraph's opening "prefer the module", but it closes the exceptions just listed and sets their scope.
- Lines 336-337, "The listing puts `import config` at the top, where ruff expects every import": "at the top" means first of the two imports; rewording to name ruff's import sorting would add a claim the file does not make.
- Lines 502-504, "The import system runs a module body once, and a thread that imports the module while the body is running waits for the body to finish": the two clauses are joint parts of one reason, so the "and" is additive.
- Lines 618-620, "The base declares one object, and every subclass inherits that same one": a sequence; no "but", "so", or "while" fits.
- Line 247, "what only a class can offer": a ruled-fine restriction.
- Lines 357-364, "which is why the listing carries `# noqa: F811`": the book's standard causal connector (conventions confirmed clean in `readability_db.md`).
- Long lines after the bold step labels (lines 80, 88, 357, 463, 471, 493, 604, 611): artifacts of the labels' insertion, left as they are because rewrapping them changes no rendered text and only enlarges the diff.
