<!-- outside review of Chapters/39_Patterns--Pattern_Catalog.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `39_Patterns--Pattern_Catalog.md` chapter:

**1. Section: Dependency Supply (technical accuracy: Service Locator and Inversion of Control)**

* **Target Text:** "Let a framework call your code rather than the reverse. *Dependency Injection* and *Service Locator* each implement *Inversion of Control*."
* **Issue:** *Service Locator* does not implement Inversion of Control. In Inversion of Control (as demonstrated by Dependency Injection), an external framework or container injects dependencies into an object without the object asking; with a Service Locator, the client object retains control by explicitly querying the locator registry for its dependencies.
* **Instruction:** Clarify that Dependency Injection implements Inversion of Control, whereas Service Locator is an alternative registry lookup where control remains with the component: "Let a framework call your code rather than the reverse. *Dependency Injection* implements *Inversion of Control*; *Service Locator* avoids it by querying a registry directly."

**2. Section: Finding a Pattern by Problem (technical accuracy: categorization of Service Locator)**

* **Target Text:** "| Supplying a collaborator from outside, an application of Inversion of Control | *Dependency Injection*, *Service Locator*, *Strategy* |"
* **Issue:** A Service Locator does not supply a collaborator from the outside (the client reaches into the locator to fetch the dependency itself), nor is it an application of Inversion of Control. Describing this problem category as supplying collaborators from the outside via Inversion of Control miscategorizes Service Locator.
* **Instruction:** Broaden the problem description so it accurately covers both injected and retrieved collaborators without mislabeling Service Locator: "| Supplying or resolving a collaborator | *Dependency Injection*, *Service Locator*, *Strategy* |"

**3. Section: Dependency Supply (structural refinement: mismatched section anchor)**

* **Target Text:** "| [*Service Locator*](46_Effects--Stateless.md#dependency-injection) | Look up dependencies through a central registry. |"
* **Issue:** The row for *Service Locator* points to `46_Effects--Stateless.md#dependency-injection`. The pattern is *Service Locator*, but its anchor is `#dependency-injection`, which is also the topic of the first row in the table (linked to Chapter 11); confirming whether Chapter 46 has a dedicated `#service-locator` heading would require checking `46_Effects--Stateless.md`.
* **Instruction:** Update the link anchor to point to the Service Locator section in Chapter 46 (e.g., `46_Effects--Stateless.md#service-locator`) rather than `#dependency-injection`.

**4. Section: Enterprise Application (Fowler) (technical accuracy: scope of Special Case)**

* **Target Text:** "| [*Special Case*](20_Patterns--Rethinking_Objects.md#null-object) | Supply a subclass for a special case instead of a null check at every use. |"
* **Issue:** This definition restricts Fowler's *Special Case* pattern exclusively to null checks, which conflates it with *Null Object* (cataloged separately in Other Patterns and Idioms as "Use an object with neutral behavior in place of null"). In *Patterns of Enterprise Application Architecture*, Special Case addresses any domain-specific exceptional case (such as an unknown customer or default configuration), not merely null checks.
* **Instruction:** Generalize the intent to match Fowler's definition: "| [*Special Case*](20_Patterns--Rethinking_Objects.md#null-object) | Provide a specialized object or subclass for particular cases to avoid conditional checks. |"

## Verdicts

Second run, on the Flash model. Applied in commit b5946b90, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The row's own intent ("Let a framework call your code rather than the reverse") and chapter 25's definition ("the framework defines the flow of control and calls your code") exclude a locator, and chapter 46 calls `dependency_injection.py` "a service locator: a body reads the container with `get(Console)`", where `greet()` makes the call itself; Fowler's essay likewise credits the inversion to injection, since the locator user "asks for it explicitly". The cell now says *Dependency Injection* applies *Inversion of Control* to an object's collaborators, and *Service Locator*, the usual alternative to *Dependency Injection*, keeps control in your code, which asks a registry; the proposed "avoids it" was replaced with that positive form.
2. Applied, with a different fix. The "an application of Inversion of Control" clause was wrong for *Service Locator* for the reason in item 1, while "from outside" stays true for *Dependency Injection* and *Strategy*. The problem now reads "Supplying a collaborator from outside, or looking one up in a registry", which names both mechanisms instead of the vaguer "resolving".
3. Rejected. Chapter 46 has no Service Locator heading: its `## Dependency Injection` section holds `dependency_injection.py` and the sentence naming it "one shape of DI, a service locator", so `#dependency-injection` is the section that covers the pattern, and `heading_links` reports the anchor OK in `verify-ch`.
4. Applied, with a different fix. Fowler's catalog entry for *Special Case* is "a subclass that provides special behavior for particular cases", with Missing Customer and Unknown Customer as examples, so the row's "instead of a null check" narrowed it to *Null Object*'s intent two tables later. The cell now reads "Supply a subclass for a particular case, such as a missing or unknown customer, instead of a conditional at every use", keeping the chapter's verb and the subclass Fowler names rather than the proposed "specialized object or subclass".
