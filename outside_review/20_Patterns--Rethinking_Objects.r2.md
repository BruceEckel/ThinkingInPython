<!-- outside review of Chapters/20_Patterns--Rethinking_Objects.md, model gemini-3.8-flash-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `20_Patterns--Rethinking_Objects.md` chapter:

**1. Section: The Liskov Substitution Principle (Correction of caller role)**

* **Target Text:** "The base class calls a method and trusts every subclass to stand in for the base."
* **Issue:** In the Liskov Substitution Principle, the base class is not the caller; client code written against the base class contract calls the method and expects any subtype to fulfill that contract. The listing directly below illustrates this: `fill()` is client code calling `stack.push()`.
* **Instruction:** Change "The base class calls a method and trusts every subclass to stand in for the base." to "Client code calls a method on the base type and trusts every subclass to stand in for the base."

**2. Section: What Is Polymorphism? (Classification of polymorphism kinds)**

* **Target Text:** "*Subtype polymorphism* is what the four subsections below demonstrate. One function accepts any type that fits a shape, and each subsection defines that shape differently: an `ABC` the type inherits, a method an `Any` parameter calls at runtime, a `Protocol` the type matches structurally, or a union the `match` statement covers."
* **Issue:** Neither dynamic typing via `Any` nor pattern matching on a union is subtype polymorphism. Calling a method on an `Any` parameter is unchecked dynamic duck typing, and pattern matching on a union is functional case analysis over a sum type (which the chapter itself contrasts with polymorphism when introducing the Expression Problem). Only the `ABC` (nominal subtyping) and `Protocol` (structural subtyping) subsections demonstrate subtype polymorphism.
* **Instruction:** Replace the paragraph with:
  "The four subsections below demonstrate different ways to handle multiple types: *subtype polymorphism* via an `ABC` (nominal subtyping) or a `Protocol` (structural subtyping), dynamic typing via `Any` (runtime duck typing with type checks turned off), and functional dispatch where a union type is handled by an exhaustive `match` statement."

**3. Section: Abstract Base Classes (Precision regarding abstract methods)**

* **Target Text:** "You cannot instantiate it, and you cannot instantiate a subclass until that subclass defines `area()`."
* **Issue:** `Shape` already defines `area()` as an abstract method; a subclass cannot be instantiated until it overrides or implements `area()` with a concrete implementation.
* **Instruction:** Change "until that subclass defines `area()`." to "until that subclass overrides `area()` with a concrete implementation."

## Verdicts

Second run, on the Flash model. Applied in commit e2866acc, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The caller in `lsp_violation.py` is `fill()`, client code typed against `Stack`, so "the base class calls a method" pointed at the wrong caller. The sentence now reads "Code written against the base class calls a method", which echoes the paragraph's earlier "code you write against the base class".
2. Rejected. The chapter defines subtyping as Cardelli and Wegner's inclusion polymorphism, and a union is a supertype of its members: a probe assigning `Rectangle(1.0)` to a `Shape = Rectangle | Circle` variable and passing a `Circle` to `area(shape: Shape)` passed `ty` with no diagnostic. The chapter also says "Dynamic typing and protocols are the same idea, checked at different times", so grouping the `Any` subsection with the `Protocol` one is its stated position, and the replacement would split the section's one framing into three.
3. Rejected. For the listing, "defines `area()`" and "overrides `area()` with a concrete implementation" say the same thing: a probe subclass that defined `area()` with a body instantiated and printed `1.0`, and one that left it out raised a `TypeError` ("Can't instantiate abstract class Missing without an implementation for abstract method 'area'"). The case the new wording guards, a subclass redeclaring `area()` as abstract, appears nowhere in `shapes_oo.py`.
