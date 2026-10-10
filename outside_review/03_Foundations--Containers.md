<!-- outside review of Chapters/03_Foundations--Containers.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `03_Foundations--Containers.md` chapter:

**1. Section: Lists (Precision on `append()`)**

* **Target Text:** "`append()` adds new elements to `odds`."
* **Issue:** The `append(13)` call adds a single element to the list, but the text uses the plural "new elements". This could prematurely blur the distinction between `append()` (which always adds exactly one element) and `extend()` (which adds multiple elements from an iterable).
* **Instruction:** Change to "`append()` adds a new element to `odds`."

**2. Section: Growing, Shrinking, and Sorting (Contradiction with listing)**

* **Target Text:** "`key=str.lower` folds the case here."
* **Issue:** The text claims that the listing uses `key=str.lower` to fold the case, but the `sorting.py` listing never uses this argument. Its output (`['Fig', 'apple', 'pear']`) demonstrates default case-sensitive sorting. 
* **Instruction:** Remove the sentence "`key=str.lower` folds the case here.", or modify `sorting.py` to include a line like `print(sorted(words, key=str.lower))` to demonstrate the case-folding.

**3. Section: Dictionaries (Caveat for `|=` vs `update()`)**

* **Target Text:** "`|` builds a merged `dict` and `|=` updates in place, the same job `update()` does."
* **Issue:** While `|=` updates a dictionary in place like `update()` does, their type signatures differ in a way that often bites in practice: `|=` strictly requires another mapping, whereas `update()` is more flexible and also accepts an iterable of key-value pairs (like the one `zip()` produces at the end of the listing).
* **Instruction:** Change to "`|` builds a merged `dict` and `|=` updates in place, similar to `update()`, though `|=` requires a mapping while `update()` also accepts an iterable of pairs."

**4. Section: Dictionaries (Accurate terminology for dict unpacking)**

* **Target Text:** "Like a list display, a `dict` display accepts any number of starred operands, with ordinary `key: value` entries among them."
* **Issue:** The text refers to dictionary unpacking as using "starred operands", which could mislead readers into using a single star `*`. Using a single star inside curly braces creates a `set`, not a `dict`; dictionary unpacking specifically requires double stars `**`.
* **Instruction:** Change "starred operands" to "double-starred operands" to accurately describe the dictionary unpacking syntax.

## Verdicts

Applied in commit d8e1423e, after each item was tested against the chapter and run under `uv run`.

1. Applied. The listing's one call is `odds.append(13)`, which adds one element, and the next section's "adds its argument as a single element" is the distinction the plural blurred. The sentence now reads "adds a new element".
2. Applied, with a different fix. `sorting.py` never passes `key=`, so "folds the case here" described a call the listing does not make; the sentence meant what the key would do to this example. It now reads "`sorted(words, key=str.lower)` folds the case and puts `apple` first", which a run confirmed (`['apple', 'Fig', 'pear']`), and the listing stays as it is.
3. Rejected. On 3.15.0rc2 `d |= [("b", 2)]` succeeds and gives `{'a': 1, 'b': 2}`: `dict.__ior__()` accepts an iterable of pairs the same way `update()` does, so the claimed difference does not exist and the sentence stands. (`|` with a list on the right does raise a `TypeError`, but the listing never writes that.)
4. Applied. The language reference's dict display grammar uses `"**" or_expr` for the unpacking item, and `{*[1, 2]}` builds a `set`, so "starred" alone could send a reader to the wrong form. The sentence now says "double-starred operands".
