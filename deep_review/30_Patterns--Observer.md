> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 30_Patterns--Observer (2026-10-09)

This run found nothing that needs your decision, so the file has no live blocks.
The chapter is in an open editing pass (`edit-start-30`), so the review read the working tree,
and the 2026-10-07 review file, which had no live blocks either, is retired as `~30_Patterns--Observer.r2.md`.
Two Opus `verify-claims` agents checked the chapter (about 160 claims) and its Solutions file (about 95 claims)
against the listings, every linked anchor, the GoF text, the story figure, and live `ty` 0.0.84 and runtime probes on Python 3.15.0rc2;
every `#:` marker matched a direct run (the two timing listings on three runs each), both test files pass,
and every anchor resolves and covers what chapter 30 credits it with.
The chapter's own claims all held, including the three added since the last review from the Gemini outside review
(`super().__init_subclass__()` and `Thermometer[int]`, construction announcing to no responders, the `None` return alias).
`tip verify-ch CH=30` passes 27 of 27 before and after the edits below.

## Applied directly

Chapter, teaching:

- "Decorated Responders": added the near-miss. A decorator's result replaces the decorated name, so `Broadcaster.connect()`, which returns `None`, cannot serve as one; that is why `respond()` exists and returns its function. Solutions exercise 11 runs the failure; the chapter now says why the method has its own name.

Chapter, prose:

- "Why `notify()` Copies the List": "does not attach to the copy, so the new observer isn't part of the `notify()` on the copy" (two negatives) is "joins `_observers` alone, so its first notification comes from the next `notify()` call".
- "The Pythonic Observer": "as seen in the `Responder` `type` alias" is "as the `Responder` `type` alias declares".
- "Decorated Responders": "To minimize application code, all common behaviors are captured in the library" named no library; now "The two listings that follow hold the shared machinery, so a subclass such as `Thermometer` declares its fields and inherits the rest."
- `published.py` prose: `property()` "returns a class attribute" returned a property object; it becomes a class attribute at `[4]` in `broadcasting.py`. Now "returns a property object that, once installed as a class attribute, intercepts...".
- `broadcasting.py` walk, `[1]`: "passes the new class to `dataclass(eq=False)`. This returns a decorator" had the class going into the wrong call. Now "calls `dataclass(eq=False)`, which returns a decorator, and applies that decorator to `cls`."

Solutions:

- Exercise 8: "moves two cells out of `skyblue` and two into `khaki`" was the gross flow, while the tally printed above it (3/3/3 to 2/3/4) shows a net change of one each; the center cell goes from `khaki` to `skyblue`. The sentence now lists all five moves and the net effect.
- Watch words with no change in meaning: "at all" (exercise 1), "already" (exercises 4, 8, and 9, four in all), "anyway" (exercise 5, the sentence restated).

Tooling: `tools/data/stranded_baseline.txt` carried a stale chapter 30 entry ("A responder chooses which notifications to act on", a sentence cut on 2026-10-08); dropped.

## Considered and declined

- "Even though `alarm` is connected before `log_reading`" and "the behavior you want when a responder counts readings": both are your edits in the open pass, and `tip watch-words` lists them as NEW because chapter 30 is held out of the baseline until the pass closes. Left for `/edit-done 30`.
- `broadcasting_thermometer.py` runs `thermometer.disconnect(alarm)` and the sentence that explained it went on 2026-10-08. The reader has met `disconnect()` three sections earlier and the marker shows the result, so no sentence was restored.
- Pyright reports an error at `fields(built)` in Solutions exercise 12 that the prose does not mention. The chapter's `fields()` paragraph describes `ty`, the book's checker, and Pyright disagreements live in `tools/data/pyright_baseline.txt`, not in prose.
- The order of "Four Scenarios, One Shape" and "Deciding What Matters": declined on 2026-10-07 and unchanged.
