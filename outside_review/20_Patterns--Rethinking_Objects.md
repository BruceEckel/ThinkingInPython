<!-- outside review of Chapters/20_Patterns--Rethinking_Objects.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `20_Patterns--Rethinking_Objects.md` chapter:

**1. Section: Evolution (Smalltalk's inheritance model)**

* **Target Text:** "You built a program at runtime by finding the closest existing object and inheriting from it to add behavior."
* **Issue:** Smalltalk is a strictly class-based language; inheritance occurs between classes, not objects. Inheriting directly from an object to create a new object describes prototypal inheritance, a concept introduced later by languages like Self and JavaScript.
* **Instruction:** Change the sentence to: "You built a program at runtime by finding the closest existing class and inheriting from it to add behavior."

**2. Section: One Class, Many Protocols (C3 Linearization scope)**

* **Target Text:** "If two base classes trace back to a common ancestor, Python resolves which version to call with C3 linearization, its method resolution order (MRO)."
* **Issue:** Python uses C3 linearization to calculate the Method Resolution Order (MRO) for *any* class inheriting from multiple bases, not just when those bases share a common ancestor (a diamond pattern). The current wording incorrectly implies C3 is a special fallback just for the diamond problem.
* **Instruction:** Change the sentence to: "When a class inherits from multiple base classes, Python resolves which version to call using its method resolution order (MRO), which it calculates via C3 linearization."

**3. Section: Null Object (Optional parameters vs optional types)**

* **Target Text:** "If you give the do-nothing case a class, the optional parameter becomes required, with a default:"
* **Issue:** In Python terminology, a parameter with a default value is inherently optional for the caller to provide, making "required, with a default" a contradiction. The text likely means the parameter's type annotation becomes concrete by dropping the `| None`.
* **Instruction:** Change the sentence to: "If you give the do-nothing case a class, the parameter's type becomes concrete instead of optional, and you can provide that neutral object as a default:"

**4. Section: The Liskov Substitution Principle (@override semantics)**

* **Target Text:** "Because `BoundedStack.push()` takes the same argument and returns the same type, `@override` holds and the type checker reports nothing."
* **Issue:** The `@override` decorator does not check signature compatibility; it only ensures that a method with the same name exists in an ancestor class. The type checker separately validates that the signatures are compatible for substitution.
* **Instruction:** Change the sentence to: "Because `BoundedStack.push()` takes the same argument and returns the same type, it passes the type checker's signature check, while `@override` verifies the method name exists in the base class."

## Verdicts

Applied in commit 16bbba9b, after each item was tested against the chapter and run under `uv run`.

1. Applied. Smalltalk subclasses classes; deriving a new object from an existing object is the prototype model of Self and JavaScript, so "closest existing object" misdescribed it. The sentence now says "closest existing class".
2. Rejected. The sentence explains how Python settles the diamond, and that holds: a probe diamond `D(L, R)` over `Top` gave `D, L, R, Top, object` and called `R.m()`. The conditional describes the diamond case without claiming C3 applies only there, and the reviewer's wording drops the diamond the paragraph exists to name.
3. Applied, with a different fix. "Required, with a default" contradicts itself, since a parameter with a default is optional for the caller. The sentence now says "an instance of that class replaces `None` as the default"; the paragraph after the listing already covers the type losing its `| None`.
4. Applied, with a different fix. Under `ty` 0.0.84 a `push(self, item: str)` override of `push(self, item: int)` drew `invalid-method-override` with and without `@override`, and `@override` on a misnamed `pushh()` drew `invalid-explicit-override`, so the decorator checks that a base method exists and the signature check is separate. The prose now says the signatures match and `@override` finds a `push()` in `Stack`.
