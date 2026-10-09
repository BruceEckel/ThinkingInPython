<!-- outside review of Chapters/34_Patterns--Composite_and_Interpreter.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `34_Patterns--Composite_and_Interpreter.md` chapter:

**1. Section: The Classic Composite (method call syntax consistency)**

* **Target Text:** "`disk_usage(root)` adds up every file below `root` to get 1940,"
* **Issue:** In `filesystem_classic.py`, `disk_usage` is an abstract method on `Node` and is invoked as `root.disk_usage()`. Describing it as a free function call `disk_usage(root)` describes the functional API introduced in the subsequent section (`filesystem.py`), contradicting the method syntax used in the classic listing and its output.
* **Instruction:** Change "`disk_usage(root)` adds up every file below `root` to get 1940," to "`root.disk_usage()` adds up every file below `root` to get 1940,".

**2. Section: Operators That Build Nodes (runtime operator dispatch order)**

* **Target Text:** "but at runtime `Var.__radd__()` runs before `str` tries to concatenate,"
* **Issue:** In Python's operator dispatch sequence, `"a" + x` calls `str.__add__("a", x)` first because `Var` is not a subclass of `str`. `str.__add__` checks whether `x` is a string, returns `NotImplemented`, and only then does Python fall back to `x.__radd__("a")`. Stating that `Var.__radd__()` runs before `str` tries to concatenate reverses Python's runtime dispatch order.
* **Instruction:** Change "runs before `str` tries to concatenate" to "runs after `str.__add__()` returns `NotImplemented`".

**3. Section: Simplification Rewrites the Tree (pronoun ambiguity with identity element)**

* **Target Text:** "An operator builds a node when either operand is one,"
* **Issue:** In a section detailing algebraic simplification rules for identity elements `0` and `1` (such as `1 * x`), using the pronoun "is one" to refer to "is a node" introduces an immediate ambiguity with the integer `1`. Readers can easily misread the sentence as stating that an operator builds a node only when an operand has the value `1`.
* **Instruction:** Change "when either operand is one," to "when either operand is a node,".

**4. Section: A Template Is a Tree (walker recursion requirement)**

* **Target Text:** "A walker that loops over the top level must therefore also recurse into any value that is a `Template`."
* **Issue:** In `template_query.py` directly below, `to_shape()` is a walker over `Template` that loops over the top level without recursing into `piece.value` (it inspects only `piece.expression`). Claiming categorically that any walker looping over the top level must recurse into `Template` values misdescribes `to_shape()`, as recursion is only required for walkers that evaluate or unpack the nested content.
* **Instruction:** Change "A walker that loops over the top level must therefore also recurse into any value that is a `Template`." to "A walker that evaluates or flattens the contents must therefore also recurse into any value that is a `Template`."

## Verdicts

Second run, on the Flash model. Applied in commit f377d163, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The sentence comments on the `composite_tree` figure directly above it, whose labels read `disk_usage(root)`, `disk_usage(src)`, and `disk_usage(File("lone.txt", 10))`; it introduces the operation before either listing, in the call form that `filesystem.py` ends up with. Rewriting the prose as `root.disk_usage()` would make it disagree with the figure, and changing the figure is a change to its generated spec in `tools/story_figures/`, outside this chapter's files.
2. Rejected. The Pro run rejected the same claim (item 2 there), and a rerun repeats its evidence: against the extracted `expr.py`, `"a" + x` printed `Add(left=Num(value='a'), right=Var(name='x'))`, `"a".__add__(x)` raises a `TypeError` instead of returning `NotImplemented`, and a probe class's `__radd__()` printed "radd ran" before the `str` `TypeError`. CPython tries the numeric slots, which reach `__radd__()`, before `str`'s concatenation, so the chapter's order is right.
3. Applied. "One" sat two sentences after a rule about multiplying by one, so "when either operand is one" could read as the integer `1`; it now says "when either operand is a node".
4. Applied, with a different fix. `to_shape()` in the listing below loops over the top level and leaves nested templates alone, and run on `outer` it printed `SELECT * FROM t WHERE <inner>`, a correct shape, so "a walker that loops over the top level must" overstated the rule. The sentence now says "A walker that needs the pieces at every level must therefore also recurse", which states the condition positively rather than listing the reviewer's "evaluates or flattens".
