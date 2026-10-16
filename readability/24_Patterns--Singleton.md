> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: Singleton

The chapter carries few AI-writing tells after the 2026-10-16 metadiscourse pass,
the colon pass, and the terminology rulings.
Four fixes had one sensible answer and are applied below.
One block remains, about the mutate-versus-rebind contrast stated several times in twenty lines,
because cutting part of a deliberate refrain is the author's call.
`tip reflow CH=24` and `tip verify-ch CH=24 ISOLATED=1` passed (27/27).

## Applied directly

- L83-84, "and" joining two subjects: "three steps through `sys.modules`, and a fourth step shows the mistake" -> two sentences, "...through `sys.modules`. A fourth step shows the mistake...".
- L202-204, §31 staged punchline: "The second underscore has one effect, and that effect is a failure. In code inside a class body, the compiler rewrites a reference to..." -> "The second underscore has one effect: it breaks a reference written inside a class body. There the compiler rewrites `m.__Settings` into a lookup for...". The claim is unchanged; the effect is named instead of announced.
- L312, §31 verdict fragment on output already on the page: cut "Eight threads, more than one object." after the `#: True` marker. Precedent: the 2026-10-04 Sweep Decisions cut of chapter 18's "Same answer, from 242,785 calls against 26." The next sentence explains the `True` in full.
- L325, filler opener: "Here, the locked version drops `@cache`" -> "So the locked version drops `@cache`", which states the consequence of the sentence before (the wrapper leaves no room for a lock).

## The mutate-versus-rebind contrast, stated three times in a row (L88-101)

§70 / treadmill. After the story figure, three passages make the same contrast back to back:

- L88-91 (the figure's explanation): "A mutation follows the name's arrow into the dict that `config` holds, so every importer sees the change. A rebinding moves the arrow to a new dict and leaves the module's dict as it was."
- L93-94: "Mutation makes the sharing work. Rebinding is the mistake that quietly ends it."
- L95-101: the same contrast walked through `settings["theme"] = "dark"` and `settings = {}`.

L93-94 adds one new word, "quietly," which L99's "silently diverge" repeats.
Proposed: cut L93-94, so the code walk follows the figure's explanation directly.
The paragraph would then open "`from config import settings` gives your module its own name for the same `dict` object named by `config.settings`."
The alternative is to keep L93-94 as the thesis pair and cut the figure paragraph's last two sentences instead, but those sentences are the only prose that reads the figure's arrows.
I left it for you because L93-94 sets up the refrain "Mutate through any name. Rebind only through the module." (L110-111), which L365-366 echoes, and that pattern looks deliberate.

[] Reject

## Considered and declined

- L22, "One interpreter, not one machine." A fragment beat among long sentences; the recurring keep for short emphatic fragments covers it.
- L56-57, §9 negative parallelism: "The singleton here is not a rule a class enforces, but a lookup the import system performs." Both halves of a real contrast, and the contrast is the chapter's thesis.
- L80, "No class, no ceremony." Named in `readability_db.md`'s recurring keeps.
- L110-111 and L365-366, "Mutate through any name. Rebind only through the module." / "Mutate through any name. Declare only what you rebind." §47 mirroring by shape, but a deliberate callback: the second pair applies the first pair's rule to `global`.
- L296-297, §32 aphorism by shape: "A window too narrow to reproduce is still a window." It closes the paragraph that reports twenty clean trials without the sleep, and it states the paragraph's point (a missed race is still a race), not a decoration.
- L435, "The race needs laziness, and this listing gives it up on purpose." Two subjects joined by "and", but neither "but" nor "so" fits cleanly, and splitting it loses the link between the requirement and the giving-up.
- L721, rhetorical question "Why does `__call__()` intercept the constructor for a `Registry`?" The question is the content the paragraph answers; recurring keep.
- L793, "The class decorator causes that confusion." Reads as a closing verdict, but the next paragraph's "The decorator weakens static checking as well" leans on it.
- "real" at L293, L573, L731, L801: each names its contrast (the sleep, a non-instance from `__new__()`, `singleton.__call__()`, a `singleton` object); §34 recurring keep.
