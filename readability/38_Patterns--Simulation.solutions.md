> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/38_Patterns--Simulation/README.md`
(2026-10-16). The file reads as written by a person: no Tier 1A vocabulary,
no chatbot artifacts, no inflated significance. The findings were the
global rules' "and"-joins whose second clause is a consequence or a
contrast, one closing sentence that restated a point made a paragraph
earlier, one pronoun with two candidates, and one "where" that read as a
location. Every one had a single sensible fix, so this file holds no live
block; it is the record of what was applied. The tool-owned block quotes,
`<details>` lines, and shape blocks were left alone, and
`tip verify-ch CH=38 ISOLATED=1` passed afterward.

## Applied directly

- 118-120, §25 generic closer: cut "The test needs no randomness and no real maze." The rat has no random step to remove, and line 111 already says the fake uses no real `Maze`. The paragraph now ends on "`run()` returns."
- 588-589, and-join with a consequence: "Both move into it, and that overlap breaks the invariant" -> "Both move into it. That overlap breaks the invariant".
- 607-609, and-join with a consequence: "between the test and the add, and that interleaving breaks the guarantee" -> two sentences. The paragraph was rewrapped.
- 866-867, and-join with a consequence: "sends the robot through a teleporter ..., and `game.robot.coins` stays `0`" -> "..., so `game.robot.coins` stays `0`".
- 868-869, and-join with a consequence: "moves `Coin` out of the factory's search, and the factory silently substitutes" -> "... search. The factory then silently substitutes".
- 1213, and-join with a consequence: "a nodal line straight down the main diagonal, and the figures all share" -> "..., so the figures all share".
- 1298, pointer with two candidates ("Its" could be the field or either product): "Its zeros lie along the curves" -> "The difference is zero along the curves".
- 1362-1363, treadmill plus and-join with a contrast: "fails differently, and its agitation readings look like a successful run's readings. Agitation falls to `0.00` as convincingly as it does at the default kick, and the figure does not appear." -> "fails differently. Its agitation falls to `0.00` as convincingly as it does at the default kick, but no figure appears." The two sentences made the same point twice. A close alternative kept the first sentence's "look like a successful run's" wording and cut the second instead; the second carries the numbers, so it stayed.
- 1371, ambiguous connective: "a whole patch, where along a nodal line" -> "whereas along a nodal line". The "where" read as a place rather than the contrast it marks.
- 1388, and-join with a consequence: "keeps the step small in a loud region too, and the grain barely travels" -> "..., so the grain barely travels".

## Considered and declined

- 1304-1307, §31 and §10, "same grains, same random walk, same rule ... Only the field changes, and with it every pattern the model produces." This reads like a staccato closer, but the three items are the real parts of the model that stay the same. The closing sentence states why exercise 7 passes a field function to `Plate`, so it stays.
- 1372-1375, §31, "The low agitation is accurate. The sand has settled, in the wrong places." This is a beat after long sentences, not a staccato run (`readability_db.md`, short emphatic fragment).
- 856-865, §70 restatement. The exercise 4 explanation repeats the opening trap paragraph (lines 810-815) about `Coin(Food)` falling off `Item.__subclasses__()`. The opening paragraph states the trap, and the later one walks through the mechanism and its consequence, which is the order the other solutions in this file use.
- 1352-1360, past tense "the default kick was down to `0.00` by step 400". This describes a run whose output is on the page, which the present-tense rule keeps in the past.
- 16, 1035, 1192, 1304, 1358, watch-list hits ("only the methods", "plans only the first leg", "exactly `0.0`", sentence-initial "Only", "anyone wants"). Each is a shape the rules keep: a ruled-fine `only` form, a numeric "exactly", and a "want" with a human subject.
- 376, clause-level "which" in the hint ("only at an `await`, which decides whether `claim()` needs a lock"). The antecedent is the whole preceding fact, and no other candidate fits.
