> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Factory

The chapter carries few AI-writing tells.
Its watch-list hits are keeps under `readability_db.md`,
and the seven edits below split "and" clauses that joined two subjects and hid the relation between them.
This file holds no live block, so it is the record of what was applied directly and what was considered and left alone.

## Applied directly

- Line 160, different-subject "and": "when the function runs, and both classes exist before anything calls `factory()`" -> two sentences, one per premise.
- Lines 350-351, different-subject "and" plus two pointers: "calls a `type[Shape]`, and any of those may be a concrete subclass, so the checker accepts it" -> "calls a `type[Shape]`. Any `type[Shape]` may be a concrete subclass, so the checker accepts the call."
- Lines 363-364, different-subject "and" plus a stranded particle: "runs its two `class` statements, and the key list shows the registry they left behind:" -> "runs its two `class` statements. The key list shows the names they registered:"
- Lines 547-548, contrast hidden in "and": "by the type of its first argument, and `make()` receives a name" -> "by the type of its first argument. `make()` receives a name."
- Lines 550-552, consequence hidden in "and": "has `Shape` as its bound, and the bound turns the decorator into a check. A decorated class must satisfy the Protocol." -> "has `Shape` as its bound. The bound turns the decorator into a check: a decorated class must satisfy the Protocol." The colon carries a restatement ("namely" fits).
- Line 574, consequence hidden in "and": "registers as well, and `make("Polygon")` fails" -> "registers as well, so `make("Polygon")` fails".
- Lines 966-968, contrast hidden in "and": "constructing a `BrokenFactory` is legal, and the checker reports `[1]`, which passes it to `GameEnvironment`" -> "constructing a `BrokenFactory` is legal. The checker reports `[1]` instead, the line that passes the factory to `GameEnvironment`." The old "which" could attach to the report rather than the line.

## Considered and declined

- Line 96, "*Factory* might be the most common design pattern." Binding keep in `readability_db.md`.
- Line 216, "That form is the most common factory." A superlative by §1/§4's shape. Kept: it is a claim about the `@classmethod` alternative constructor that the next sentence backs with two standard-library examples, and it rides on the line-96 precedent.
- Line 230, "A factory over a closed set of products reduces to a lookup." A closing generalization (§32 by shape). Kept: it states the conclusion the `Enum` paragraph builds to, and it sets up the next section's dictionary.
- Line 11, "with no changes to existing code ... or so it seems." First-edition voice and a deliberate turn; left alone.
- Lines 94-95, "Every object-oriented program creates objects, and you often extend such programs by adding new types." Two subjects joined by "and", but the clauses are two premises that the "Thus" of line 96 combines, so the "and" is additive.
- Lines 409-410, "The class is fine, the registry is fine, and nothing imported the module" A triple by §10's shape. Kept as deliberate rhythm: the first two items rule out the suspects the third replaces.
- Line 413, "even when the import statement is in the file." On the avoid list, but the concession is the claim: the import is present and the registration still never runs.
- Line 416, "never uses that name"; line 408, "never registered." Each "never" states the failure itself, a keep under the watch-list-absolute rule.
- Lines 157, 637, 759, 768, 770, 1033, 1323, "the only code", "the only method", "only when", "only in". Ruled-fine shapes of "only".
- Line 1042, "a warning, not an example to follow"; line 1208, "solves a problem Python does not have." Negations that are the claim, each half of a real contrast.
- "Thus" opens three sentences (96, 243, 879) across 1,400 lines: not a cluster (§62).
- "We can add a factory" (107) and "Here, we create one factory object" (641) are the author's "we"; left alone.
