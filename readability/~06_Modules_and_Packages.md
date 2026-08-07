[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/06_Modules_and_Packages.md`

This chapter reads as human throughout.
A full pass over the Tier 1A/1B/2 vocabulary, the promotional and significance patterns, the structural tells, and the repo-banned strings turned up no hits: no `reach for`, no spaced ` -- `, no curly quotes, no boldface or bullet inflation, and sentence and paragraph lengths vary naturally.
The only two candidates are both mild, and both sit in the newer explanatory paragraphs rather than the older narrative prose.

***

[] Reject

**Section:** Intro, paragraph after `import_once.py` (the `sys.modules` explanation)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> A module's top-level code is a one-time setup step rather than something that runs per import.

Proposed:
> Cut this sentence.

Why: The two sentences before it already say that a later `import` "finds it there and binds the same object instead of re-running the file," so this line restates the same fact as a general rule in the "X rather than Y" shape.

***

[] Reject

**Section:** Intro, paragraph after `globals_demo.py`
**Pattern:** §70 Interpretive Metadiscourse (P2), borderline

Current:
> It matters whenever code needs to define a module-level name that isn't known until runtime,

Proposed:
> Assigning into `globals()` matters whenever code needs to define a module-level name that isn't known until runtime,

Why: The nearest antecedent for "It" is "the cost ... and a reason to keep it rare" in the previous sentence, so the sentence reads as though the *cost* is what matters, the opposite of the intended point.
This is a referent-clarity fix rather than a classic AI tell, so it is borderline for this skill.
