<!-- outside review of Chapters/22_Patterns--Data_Transfer_Objects.md, model gemini-3.8-flash-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `22_Patterns--Data_Transfer_Objects.md` chapter:

**1. Section: `NamedTuple` (technical accuracy)**

* **Target Text:** "[`copy.replace()`](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace) does the same job for a `NamedTuple`, a frozen data class, and any other type that defines `__replace__()`."
* **Issue:** Assuming Python 3.13–3.15, `copy.replace()` requires the `__replace__()` protocol (PEP 712) and does not fall back to `_replace()`. Standard `typing.NamedTuple` and `collections.namedtuple` classes define `_replace()` rather than `__replace__()`, so calling `copy.replace()` on a `NamedTuple` raises `TypeError: replace() unsupported operand type`.
* **Instruction:** Clarify that `copy.replace()` operates on data classes and types that implement `__replace__()`, whereas `NamedTuple` uses its own `_replace()` method. Change the sentence to: "It produces an updated copy. [`copy.replace()`](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace) does the same job for a frozen data class and any other type that defines `__replace__()`, while a `NamedTuple` relies on `_replace()` directly."

**2. Section: A NamedTuple Is Still a Tuple (technical accuracy / listing alignment)**

* **Target Text:** "`<` between two `FrozenColor`s raises a `TypeError` unless the decorator receives `order=True`, and a comparison between two different frozen types raises one even then."
* **Issue:** The phrase "a comparison between two different frozen types raises one even then" misdescribes the listing. Equality comparison between different frozen types does not raise—line 31 explicitly demonstrates `FrozenColor(1, 2, 3) == FrozenDimensions(1, 2, 3)` evaluating to `False`. Furthermore, the comparison in the listing that raises `TypeError` (`OrderedColor(...) < OrderedDimensions(...)`) is an ordering comparison between distinct *ordered* types (`order=True`).
* **Instruction:** Restrict the statement to ordering comparisons between distinct ordered types. Change the sentence to: "`<` between two `FrozenColor`s raises a `TypeError` unless the decorator receives `order=True`, and an ordering comparison between two different ordered types raises one even then."

**3. Section: Returning Multiple Values (technical precision)**

* **Target Text:** "Unpacking is the part a data class lacks. `mean, count = summarize(data)` against a `@dataclass` version of `Stats` raises a `TypeError`, since a data class is not iterable."
* **Issue:** Stating unqualified that a data class lacks unpacking overlooks pattern matching (PEP 634, Python 3.10+), where data classes automatically generate `__match_args__` and unpack positionally (e.g., `case Stats(mean, count):`). The limitation is specifically iterable assignment unpacking because a data class does not implement `__iter__()`.
* **Instruction:** Specify that iterable unpacking is what data classes lack. Change the sentences to: "Iterable unpacking is the part a data class lacks. `mean, count = summarize(data)` against a `@dataclass` version of `Stats` raises a `TypeError`, since a data class is not iterable (though pattern matching can unpack a data class positionally via `__match_args__`)."

**4. Section: A Hand-Rolled Messenger (technical completeness)**

* **Target Text:** "Because `**kwargs` is the only parameter after `self`, `Messenger` accepts keyword arguments alone. `Messenger("Spam")` raises a `TypeError`, and the `*` marker from [Positional-Only and Keyword-Only Parameters](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters) is unnecessary here. Writing `def __init__(self, *, **kwargs)` is a syntax error, since a named parameter must follow a bare `*`."
* **Issue:** While `*` is not needed to enforce keyword arguments in `**kwargs`, leaving `self` without the positional-only marker `/` leaves `self` exposed as a keyword parameter. A call such as `Messenger(self="val")` crashes with `TypeError: Messenger.__init__() got multiple values for argument 'self'`, whereas `SimpleNamespace(self="val")` succeeds because its constructor treats `self` as positional-only. Readers referencing chapter 5 benefit from knowing why `/` applies here even if `*` does not.
* **Instruction:** Add a brief note explaining that marking `self` positional-only with `/` prevents collisions with a keyword named `self`. Update the text to: "Because `**kwargs` is the only parameter after `self`, `Messenger` accepts keyword arguments alone. `Messenger("Spam")` raises a `TypeError`, and the `*` marker from [Positional-Only and Keyword-Only Parameters](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters) is unnecessary here (though marking `self` positional-only with `/`, as in `def __init__(self, /, **kwargs)`, is required if you want to allow a keyword argument named `self`). Writing `def __init__(self, *, **kwargs)` is a syntax error, since a named parameter must follow a bare `*`."

## Verdicts

Second run, on the Flash model. Applied in commit 82fd799c, after each item was tested against the chapter and run under `uv run`.

1. Rejected. On the pinned 3.15.0rc2, `hasattr(Color, "__replace__")` is `True` for a `NamedTuple` (the method arrived in 3.13), and `copy.replace(Color(1, 2, 3), g=9)` returns `Color(r=1, g=9, b=3)`, so the chapter's sentence is right.
2. Applied, with a different fix. The claim is accurate (a probe showed `<` between two distinct frozen types raising a `TypeError`, as does the listing's `Ordered` pair), but "a comparison" could be read as `==`, which the listing shows returning `False` between the two frozen types. The clause now reads "and between two different frozen types it raises one even then", so the subject stays `<`.
3. Rejected. The paragraph is about assignment unpacking, `mean, count = summarize(data)`, and that raises a `TypeError` on a data class; a `match` class pattern does destructure one (`case Stats(m, c):` bound `2.0 2`), but it is a different construct, and the parenthetical would take the paragraph away from its point about positional reads.
4. Rejected. The Pro run's item 1 raised the same `self` clash and left it out because the listing never passes a keyword named `self`; the sentence already reads "the only parameter after `self`". `SimpleNamespace(self="val")` does succeed, but the chapter makes no claim that `Messenger` accepts every name.
