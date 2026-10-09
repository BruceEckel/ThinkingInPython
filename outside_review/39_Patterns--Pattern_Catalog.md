<!-- outside review of Chapters/39_Patterns--Pattern_Catalog.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `39_Patterns--Pattern_Catalog.md` chapter:

**1. Finding a Pattern by Problem (Missing core database pattern)**

* **Target Text:** `| Persisting domain objects to a database | *Active Record*, *Repository*, *Table Module*, *Lazy Load*, *Unit of Work*, *Identity Map* |`
* **Issue:** *Data Mapper* is one of Fowler's fundamental architectural patterns specifically designed for persisting domain objects while keeping them completely decoupled from the database schema. Omitting it from this problem category leaves out the primary structural alternative to *Active Record*.
* **Instruction:** Insert `*Data Mapper*, ` into the list of patterns so it reads: `| Persisting domain objects to a database | *Active Record*, *Data Mapper*, *Repository*, *Table Module*, *Lazy Load*, *Unit of Work*, *Identity Map* |`

**2. Pattern Catalog (Inaccurate distinction between State and State Machine)**

* **Target Text:** "The machine chooses each successor, so the object advances without the client choosing."
* **Issue:** The GoF *State* pattern explicitly allows the internal state subclasses or the context to choose the successor and transition automatically without the client's involvement. The true architectural distinction of a *State Machine* is that it formalizes the events and valid transitions into an explicit, centralized model (like a graph or transition table) instead of just distributing the transition logic opaquely across polymorphic subclasses.
* **Instruction:** Replace the sentence with: "The machine formalizes the valid events and transitions into an explicit model, rather than just distributing behavior across subclasses."

**3. Patterns Python Absorbed (Broadening Command absorption)**

* **Target Text:** `| [*Command*](28_Patterns--Function_Objects.md#command-choosing-the-operation-at-runtime) | A function stored in a list |`
* **Issue:** Describing Python's absorption of *Command* solely as "a function stored in a list" artificially restricts the pattern to macro or queue scenarios. The essence of a Command is encapsulating a deferred request, which in Python is frequently just a callable saved to a single variable or attribute (such as an `on_click` callback).
* **Instruction:** Change the right-hand column to: `A callable saved to run later, or stored in a list`

**4. Patterns Python Absorbed (Modernizing Visitor absorption)**

* **Target Text:** `| [*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch) | functools.singledispatch |`
* **Issue:** While `functools.singledispatch` manages single-node polymorphism externally, structural pattern matching (`match`/`case`, introduced in Python 3.10) is modern Python's primary and most powerful tool for deconstructing objects and traversing tree structures, fully superseding the need for a classic Visitor class.
* **Instruction:** Change the right-hand column to: `functools.singledispatch` and structural pattern matching (`match`)

**5. Concurrency (POSA and others) (Missing modern concurrency pattern)**

* **Target Text:** `| *Read-Write Lock* | Allow concurrent readers but exclusive writers. |`
* **Issue:** The Concurrency table lacks *Structured Concurrency*, a major and widely recognized modern pattern that safely scopes concurrent task lifetimes so they complete or cancel as a unified block. This is a fundamental paradigm in modern async programming and is natively implemented in Python 3.11+ via `asyncio.TaskGroup`.
* **Instruction:** Insert a new row below *Read-Write Lock* in alphabetical order: `| *Structured Concurrency* | Bind the lifetimes of concurrent tasks to a scope so they complete or cancel as a unit. |`

## Verdicts

Applied in commit f2062667, after each item was tested against the chapter and run under `uv run`.

1. Applied. The catalog's own Fowler table gives *Data Mapper* the intent "Move data between objects and the database, so neither names the other", the persistence alternative to *Active Record*, yet the problem table listed it under moving data across a boundary alone. The persistence row now names *Data Mapper* after *Active Record*.
2. Rejected. The sentence matches the book's framing in two other chapters: chapter 26's *State* section says "Here the client programmer calls `change_to()`, but in a *State Machine*, each implementation chooses its own successor", and chapter 31 opens with "*State* lets the client programmer swap the implementation." The proposed wording ("an explicit model, rather than distributing behavior across subclasses") contradicts chapter 31's first design, "Each State Decides", where each `State` object returns its own successor.
3. Applied, with a different fix. Chapter 28 defines *Command* as wrapping an action "so you can pass it around and run it later", and the list in `command.py` is one macro built from such functions; the cell now reads "A function saved to run later", which states the intent and sets it beside *Strategy*'s "A function passed as an argument". The proposed "or stored in a list" repeats the same idea, since a list is one place to save it.
4. Applied, with a different fix. The book backs a `match` as a *Visitor* replacement: chapter 34's "New Operations, Same Tree" says `to_infix()` adds an operation without editing a node class, "the ability *Visitor* exists to provide", and chapter 33 names a `match` over a union as the closed-set alternative to `singledispatch`. The cell now reads "`functools.singledispatch`, or a `match` over a union of types"; the "fully supersedes" claim was left out, since chapter 33 keeps `singledispatch` for an open set of types.
5. Applied. Chapter 19 has a section titled "Structured Concurrency with `TaskGroup`", so the pattern is one the book covers and the catalog lacked. A linked row now sits between *Read-Write Lock* and *Thread Pool*, with the intent worded from that section's `TaskGroup` behavior (the block exits after every task finishes, and a failure cancels the rest); `heading_links` reports the anchor OK.
