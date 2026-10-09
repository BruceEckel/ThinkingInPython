<!-- outside review of Chapters/25_Patterns--Template_Method.md, model gemini-3.8-flash-high, 2026-10-08 -->

**Please apply the following technical and structural refinements to the `25_Patterns--Template_Method.md` chapter:**

**1. Section: Hooks and the Misspelled Override (descriptor resolution and @final)**

* **Target Text:** "For those, `getattr()` on the class returns a bound method, the bare function, or the property object, and none of them carries `__final__`."
* **Issue:** For an instance method, `getattr(super(cls, cls), name)` also returns the bare function, which is precisely what carries `__final__`. For `@staticmethod`, if `@final` decorates the inner function (`@staticmethod` over `@final`), the returned bare function *does* carry `__final__`; if `@final` wraps `@staticmethod` on the outside, `typing.final` silently fails to set `__final__` because `staticmethod` descriptor objects disallow attribute assignment.
* **Instruction:** Clarify that descriptor binding returns a bound method for `@classmethod` and a property object for `@property` (neither exposing `__final__`), while descriptors like `property` and `staticmethod` reject attribute assignment if `@final` decorates the descriptor itself. Change the sentence to: "For `@classmethod` and `@property`, `getattr()` returns a bound method or property object that does not expose `__final__`. For `@staticmethod`, the check only succeeds if `@final` decorates the inner function, because decorating the descriptor itself silently fails to set `__final__`."

**2. Section: Substitutability (qualifying empty steps)**

* **Target Text:** "An unexpected exception, an empty step, and a skipped pass each corrupt the anchored algorithm."
* **Issue:** The sentence states unconditionally that an empty step corrupts the anchored algorithm, which contradicts the preceding section ("Hooks and the Misspelled Override") and the next sentence ("The `...` defaults make a step optional"). In this framework, steps intentionally default to `...` do-nothing bodies to serve as optional hooks; an empty step only breaks the algorithm when the workflow relies on that step performing work.
* **Instruction:** Qualify "an empty step" to match the opening paragraph of the section. Change the sentence to: "An unexpected exception, an empty step when the flow depends on it, and a skipped pass each corrupt the anchored algorithm."

**3. Section: Passing the Steps as Functions (enclosing function vs loop name)**

* **Target Text:** "The box beneath them changes, along with the loop's name in frame 3."
* **Issue:** In Python, loops do not have names. The name change in frame 3 (from `run()` to `run_framework()`) belongs to the enclosing function that contains the loop, not the loop itself.
* **Instruction:** Replace "the loop's name" with "the enclosing function's name": "The box beneath them changes, along with the enclosing function's name in frame 3."

**4. Section: What Anchors the Algorithm (runtime status of @final)**

* **Target Text:** "This holds at runtime, whereas `@final` is only a type-checking attribute."
* **Issue:** Calling `@final` "only a type-checking attribute" contradicts the earlier section explaining that `@final` explicitly sets the runtime attribute `__final__ = True` on the function object—which is the exact runtime attribute `__init_subclass__()` inspects. The intended distinction is that enforcement of `@final` is performed only by the type checker by default, not that the attribute itself does not exist at runtime.
* **Instruction:** Clarify that default enforcement is what is restricted to the type checker. Change the sentence to: "This holds at runtime, whereas `@final` is enforced only by the type checker unless inspected manually."

**5. Section: Exercises (type checking exceptions vs abstract methods)**

* **Target Text:** "What must be true of the base class for the type checker to catch either one?"
* **Issue:** The question asks what must be true of the base class for the type checker to catch "either one" of the broken subclasses (raising an unexpected exception vs. omitting an essential step). While declaring the step with `@abstractmethod` allows the type checker to catch an omitted step, Python's type system has no checked exceptions and cannot reject unexpected exceptions; framing the question around "either one" implies both can be caught by base-class typing.
* **Instruction:** Distinguish between the two failure modes. Change the question to: "What must be true of the base class for the type checker to catch the omitted step, and why can no base-class typing construct catch the exception?"

## Verdicts

Second run, on the Flash model. Applied in commit 2170e774, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. On 3.15.0rc2 `@final` above `@classmethod` or `@staticmethod` does set `__final__` on the wrapper (the Pro-run verdict found the same), so "silently fails to set" is wrong for those two; but with `@final` below either one, `getattr(super(D, D), name)` returns a bound method or function that reports `__final__` as `True`, so the chapter's unqualified "the check misses" was too broad, while `@property` misses in both orders (`ty` rejects the override in all six cases). The sentence now says the check misses a `@final` on a `@property` and one written above `@classmethod` or `@staticmethod`, and adds that `@final` written below those two marks the function `getattr()` returns, so the check catches the override.
2. Applied. The list at the top of the section already says "leaves a step empty when the flow depends on it", and the summary sentence dropped that qualifier; it now reads "an empty step the flow needs".
3. Applied, with a different wording. The SVG labels the loop's box `@final run()` in frames 1 and 2 and `run_framework()` in frame 3, so the name belongs to the function holding the loop; the sentence now says "the name of the function that holds the loop, `run_framework()` in frame 3."
4. Applied, with a different wording. The chapter says earlier that `@final` sets `__final__ = True` at runtime, so "only a type-checking attribute" contradicted it; the bullet now reads "whereas the type checker alone enforces `@final`", echoing "Only the type checker enforces `@final`" in The Anchored Algorithm, without the reviewer's "unless inspected manually".
5. Rejected. The question is built for the reader to discover that one failure can be caught and the other cannot: the solution's hint says "Consider which of the two failures any declaration available in Python could expose", and its answer splits the two (`@abstractmethod` catches `HalfDone`, nothing in Python's type system catches `Exploder`). The proposed wording states that answer inside the question.
