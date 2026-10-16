> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/10_Foundations--Cleanup/README.md`, 2026-10-16.
The prose carries almost no AI-writing tells: no Tier 1A vocabulary, no stacked transitions, no watch-list hits beyond a comparative "just as", and the bold step labels are the Solutions convention.
Three edits were applied directly.
One block remains, about exercise 4's "the leak it exists to detect", which mirrors the open block on the chapter's last sentence in `readability/10_Foundations--Cleanup.md` and should follow the same verdict.

## Applied directly

- Line 254, §26 hyphenated chain: "the original `for`-loop-with-`append()` version" -> "the original version, which calls `append()` in a `for` loop"; paragraph rewrapped.
- Line 342, repeated "now" in consecutive sentences: "`live_count()` now reports" -> "`live_count()` reports"; the "now" in the sentence before carries the contrast with the weak registry.
- Line 412, dangling modifier: "Run as a standalone script, the whole output is:" -> "Run as a standalone script, the program prints:", so the participle attaches to the program.

## Exercise 4: "the leak it exists to detect"

Line 341, §32 (aphorism formula):

> The registry now causes the leak it exists to detect.

The sentence says the registry exists to detect leaks.
The chapter presents `weak_value.py`'s registry as a live-instance counter and never names leak detection as its job; the chapter review raises the same question about its closing line ("the leak it exists to catch").
If Bruce keeps the chapter's sentence, this one stays as the matching echo.
If he changes the chapter's, this one should drop the purpose claim too.
Proposed, using only what the paragraph already says:

> The registry now leaks every `Counter` it tracks.

Reject this block to keep the current sentence (and decide it together with the chapter's block).

[] Reject

## Considered and declined

- Lines 181-185 against 150-154, §70 restatement: the closing paragraph of exercise 2 repeats that insertion order is creation order and that `sorted()` is needed. Kept: the opening paragraph shows the mistake through its output, and the closing one names the mechanism behind it.
- Lines 539-540, §32 kicker: "The loss is in the guarantee, not in what this run prints." It restates the paragraph's first and fifth sentences. Kept: it is the one-line answer to the exercise's two halves (no guarantee, yet the same transcript), and the chapter keeps its own "X, not Y" closes ("to catch the mistake, not to be the plan").
- Line 448, §9 tailing negation: "keeps a string alive, not a connection". Kept: the contrast is the point of the paragraph.
- Line 652, positive statement: "`C closed` does not print for `Faulty`." Kept: the negation is the answer the exercise asks for.
- Line 279, "plain `dict`": contrasts with `WeakValueDictionary` (recurring keep).
- Line 256, "the only references": the "the only X" shape, which states the restriction (recurring keep).
