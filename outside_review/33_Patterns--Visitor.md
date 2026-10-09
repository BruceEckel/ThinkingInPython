<!-- outside review of Chapters/33_Patterns--Visitor.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `33_Patterns--Visitor.md` chapter:

**1. The Classic Visitor: The Classic Visitor (Ambiguous "version" phrasing)**
* **Target Text:** "In this Python version a new operation whose behavior varies by flower type also needs a new method on Flower, for a reason The Price of the Empty Base explains below."
* **Issue:** The phrase "Python version" can be easily misread by readers as referring to a specific release of the language (e.g., Python 3.15), whereas the context implies you are talking about this specific Python adaptation/implementation of the Visitor pattern.
* **Instruction:** Change "In this Python version" to "In this Python variant of the pattern".

**2. The Classic Visitor: The Classic Visitor (Subclass depth caveat)**
* **Target Text:** "`flower_gen()` reads the concrete classes from `Flower.__subclasses__()`, the same registry-free enumeration as Factory."
* **Issue:** `__subclasses__()` only returns immediate/direct subclasses. If a reader experiments by adding a subclass to an existing flower (like the `Hybrid(Gladiolus)` that appears in the later test snippet), they might be surprised when it is silently excluded from the enumeration.
* **Instruction:** Add this sentence immediately after: "Keep in mind that `__subclasses__()` only returns direct subclasses, so it misses deeper descendants unless called recursively."

**3. The Pythonic Visitor: singledispatch (Stale Pyright/ty claim)**
* **Target Text:** "ty and Pyright accept nectar(42) too, because the dispatcher that @singledispatch builds declares its parameters as Any. Only mypy rejects it, since mypy's built-in singledispatch plugin checks the call against the base function's signature."
* **Issue:** This claim is outdated for modern Python 3.10+ environments. `ty` and Pyright now rely on modern `typeshed` stubs that use `ParamSpec` to accurately preserve and enforce the base function's signature for `@singledispatch`. Consequently, Pyright (and thus `ty`) will correctly reject `nectar(42)` just as mypy does.
* **Instruction:** Replace these sentences with: "Type checkers like ty and mypy reject `nectar(42)` because they check the call against the base function's signature, which expects a `Flower`."

**4. The Pythonic Visitor: singledispatch (Class method omission)**
* **Target Text:** "singledispatchmethod dispatches on the first argument after self."
* **Issue:** This definition inadvertently excludes class methods. Python's `singledispatchmethod` inspects the first non-self or non-cls argument, meaning it elegantly accommodates `@classmethod` decorators where the first argument is `cls`.
* **Instruction:** Change the sentence to: "`singledispatchmethod` dispatches on the first argument after `self` or `cls`."

## Verdicts

Applied in commit 7a28e353, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. In a book pinned to Python 3.15, "this Python version" can read as a release. The sentence now opens "In this Python form of the pattern," which keeps the reviewer's point in the chapter's wording.
2. Rejected. The sentence links the Factory section, which says that `__subclasses__()` covers only the first level of inheritance and that a deeper hierarchy needs recursion (chapter 27, "covers only the first level of inheritance"). `flower_visitors.py`'s hierarchy is flat, and the `Hybrid` subclass appears in `test_visitor.py`, which never calls `flower_gen()`.
3. Rejected. `ty` and Pyright 1.1.414 both check `nectar(42)` against the extracted `visitor_singledispatch.py` with no error, and both reveal `nectar` as `_SingleDispatchCallable[str]`, whose typeshed `__call__()` takes `*args: Any, **kwargs: Any`. The chapter's claim holds; there is no `ParamSpec` in that stub.
4. Rejected. A probe confirmed that `@singledispatchmethod` over `@classmethod` dispatches on the argument after `cls`, but the sentence introduces the method form for an operation that "should read like a method," and it links chapter 41's `singledispatchmethod` section, which carries the full treatment in the same words. The class method case falls outside this chapter's scope.
