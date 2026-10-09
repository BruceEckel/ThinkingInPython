<!-- outside review of Chapters/21_Patterns--Design_Patterns.md, model gemini-3.8-flash-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `21_Patterns--Design_Patterns.md` chapter:

**1. Section: When a Pattern Dissolves (Prose misdescribes listing)**

* **Target Text:** "The `how` parameter replaces all three."
* **Issue:** In the classic GoF *Strategy* pattern, the three components are the `Strategy` interface, the concrete algorithm classes, and the context class. In `strategy_is_a_function.py`, the `how` parameter (specifically its `Callable` annotation) replaces only the `Strategy` interface; the `apply` function replaces the context class, and functions like `max` and `sum` replace the concrete algorithm classes. Stating that the parameter alone replaces all three misidentifies how Python represents the context and algorithm implementations.
* **Instruction:** Clarify the division of roles by replacing the target sentence with: "Python replaces all three with functions and callables: `apply` replaces the context class, the `Callable` annotation on `how` replaces the `Strategy` interface, and functions like `max` and `sum` replace the concrete algorithm classes."

**2. Section: What One Part Knows About Another (Technical accuracy)**

* **Target Text:** "In a language whose only rungs are a part's internals and its name, a pattern exists to build a declared interface."
* **Issue:** The coupling ladder earlier in this section establishes abstract base classes (declared interfaces) as the third rung, sitting directly above internals and names. GoF patterns were developed in C++, which already had nominal declared interfaces (abstract base classes); the patterns exist to construct that nominal interface scaffolding because the language lacks structural protocols (`Protocol`) or first-class callable annotations (`Callable`). Saying the language's "only rungs are a part's internals and its name" contradicts the ladder and misattributes the limitation of nominal OOP languages.
* **Instruction:** Replace the target sentence with: "In a language whose only decoupling rung is a nominal declared interface (an abstract base class), a pattern exists to build that interface and its inheritance scaffolding."

**3. Section: A Pattern Moves an Edge (Technical accuracy)**

* **Target Text:** "An observer names its subject's class in `update()`, whose `subject` parameter receives the subject that changed."
* **Issue:** The section defines a heavy edge as naming a concrete class and a thin edge as naming an interface. In GoF's *Observer* pattern, the abstract `Observer` interface does not name a concrete subject class, which would couple the interface to a specific implementation. Instead, a concrete observer names the concrete subject (either in its type annotation or when querying state in the pull model), while the subject depends only on the abstract `Observer` interface.
* **Instruction:** Replace the target sentence with: "A concrete observer names its concrete subject's class in `update()` (or when querying its state), while the subject depends only on the abstract `Observer` interface."

**4. Section: Design Principles (Technical accuracy)**

* **Target Text:** "A method should talk to itself, its own attributes, its parameters, and objects it creates, not to the internals of objects it reached through something else."
* **Issue:** In object-oriented design and the formal formulation of the Law of Demeter, methods do not own attributes, nor does "talking to itself" describe anything other than recursive calls. Demeter restricts a method to invoking members on its receiving instance (`self`), that instance's attributes/components, its own parameters, and objects created within the method.
* **Instruction:** Update the sentence to reference the receiving instance: "A method should talk to its receiving object (`self`), that object's attributes, its parameters, and objects it creates, not to the internals of objects it reached through something else."

## Verdicts

Second run, on the Flash model. Applied in commit 5040295e, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. `strategy_is_a_function.py` prints `3 6` and passes `ty check`, and in it `apply()` holds the chosen algorithm while `max()` and `sum()` are the algorithms, so "the `how` parameter replaces all three" overstated the parameter's share; the sentence now assigns the interface to the `Callable` annotation, the algorithm classes to `max()` and `sum()`, and the context class to `apply()`, and the later summary reads "a function with a `Callable` parameter can replace a pattern's interface and classes".
2. Applied, with a different fix. The contradiction is real: the ladder puts the abstract base class rung above internals and name, and C++ and Java have that rung, so "whose only rungs are a part's internals and its name" was wrong. The reviewer's "only decoupling rung is a nominal declared interface" would drop the value rung too, so the sentence now reads "In a language where every implementer must name its interface", which matches "The Edge Python Deletes" ("The implementer must name the interface").
3. Rejected. GoF's abstract `Observer::Update(Subject*)` names the subject class, and so do chapter 30's `classic_observer.py` protocol and its `Display` (`subject: Subject[float]`, the base class, not the concrete `Thermometer`); `tools/coupling_panels.py` draws the heavy edge from `Display` to `Subject` with the label `subject: Subject`. The reviewer's "concrete subject's class" contradicts both, and the subject's dependence on the abstract interface is the next sentence's quote.
4. Applied. "A method should talk to itself, its own attributes" made the method the owner of the attributes; Demeter's first two targets are the method's object and that object's attributes, so the bullet now reads "its own object (`self`), that object's attributes, its parameters, and objects it creates".
