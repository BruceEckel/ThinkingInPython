> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 27_Patterns--Factory (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the chapters it links (3, 6, 7, 8, 12, 13, 14, 17, 20, 21, 24, 26, 32, 37, 38), the GoF text for *Factory Method*, *Prototype*, and *Builder*, `ty` 0.0.84 and Pyright 1.1.414 probes, and runtime probes on the pinned 3.15.0rc2.
The inbound sentences in chapters 6, 12, 14, 17, 21, 29, 32, 33, 37, 38, 39, 40, and 47 that describe this chapter all hold.
`tip verify-ch CH=27` passes 24 of 24, and `tip verify` passes in the worktree.

## Applied directly

Chapter, corrections:

- "Abstract Factories": the chapter said the Protocol reports a missing `make_obstacle()` before the program runs, "earlier than the construction-time `TypeError`" of the ABC version. `ty` reports the ABC case too (`Cannot instantiate abstract class`, at the constructing line), and chapter 26 says so about `Partial()`. The two paragraphs now say both versions report at check time, at different lines, and that the runtime difference is the real one: the ABC refuses construction, the Protocol version fails with an `AttributeError` inside `GameEnvironment.__init__()` (probed).
- "The Pythonic Factory": "the same trade Abstract Factories makes with a Protocol" rested on that claim. The link now points to "Explicit Registration with a Protocol", which does move a runtime failure to the check.
- "Self Registration": "No type checker reports that case" is true only of the `Shape.registry[name]()` call. The paragraph now says the checker reports a line that constructs such a class by name and accepts the call through `type[Shape]`. It also says what the `ABC` guard is, which the old order left for the reader to infer.
- "Builder": "The *GoF Design Patterns* structure looks like this" introduced the fluent telescoping-constructor builder, which is Joshua Bloch's (*Effective Java*). GoF's *Builder* has a director driving an abstract builder so one process yields different representations. The opening now gives GoF's form in two sentences, names Bloch's as the one the listing translates, and keeps the telescoping-constructor explanation.
- "Builder", the `GameBuilder` paragraph: "No single constructor call can express that" is contradicted by `GameBuilder(string_maze)`, which runs all three stages in its constructor. Now "No list of keyword arguments can express that." "Connecting doors" is now "connecting each room to its neighbors", matching the stage-two comment, and the link goes to `#building-the-maze-in-stages`, the section that shows `GameBuilder`, not `#a-robot-in-a-maze`.
- "Prototype": the chapter gave `cannot pickle '_thread.lock' object` as the message for a file, a socket, or a lock. Each has its own message (probed). The sentence now gives the lock's message as the lock's and says why a copy mentions pickling.
- "Hazards of Self Registration": "`make()` stays a module-level function for two reasons" precedes three reasons. Now "three".
- "Hiding the Concrete Classes": the duplicate classes leave `Shape.__subclasses__()` when the collector reclaims them (probed: four entries fall to two after `gc.collect()`). One sentence added.

Chapter, teaching:

- "Simple Factory Method": `factory()` names `_Circle` and `_Square` above their definitions. Three lines say why that works.

Chapter, house style:

- `shape_table.py` and `prototype_registry.py`: `Kind = Literal[...]` is now `type Kind = Literal[...]`, the form every other `Literal` alias in the book uses. `ty` then prints `Kind` in its message, so the comment in `shape_table.py` is `# ty: expected Kind, found Literal["Hexagon"]:`.
- "For a frozen data class, `replace()` is..." (twice) is now "For a record", the prose noun from chapter 18 on.

Chapter, prose:

- "collapses to a lookup, the form the next section builds by hand, and then lets the classes fill for an open set" split into two sentences with the object of "fill" stated.
- "The cost is the mirror failure" is now "the opposite failure", and "a `KeyError` that points at nothing" now says what the error names and what it omits.

Solutions:

- Exercise 3: the exercise says to pass the factory to `GameEnvironment`, and the Protocol half passed it to a `play()` function the chapter does not have. The listing now carries `GameEnvironment`, and the quoted diagnostic is requoted from `ty` 0.0.84 (`Argument to GameEnvironment.__init__ is incorrect`, line 31). `tools/data/quoted_diagnostics_baseline.txt` has the one changed entry.
- Exercise 3: the closing paragraph said only the Protocol half is reported before the program runs. Rewritten to match the chapter's corrected account.
- Exercise 3: `GnomesAndFairies` built a `Gnome` and a `Riddle`. The chapter's factories name their two products, so the obstacle is now `Fairy`.
- Exercise 8: the listing wrapped both dispatchers in classes (`EvalFactory`, `TableFactory`) with class-level caches, an older form of the chapter's listing. It now uses the chapter's module-level `FACTORIES` and `create_shape()`, with `eval_shape()` beside them, and `Shape` is the chapter's ABC.
- Exercise 5: `Pizza` defaulted to size 9 where `pizza_direct.py` has 12. Now 12, and the last line prints the toppings, since the full `repr` at size 12 is 61 columns.
- Exercise 5: the exercise points to `stars_class.py` and the solution never mentioned it. A closing paragraph ties the builder that checks in `build()` to `damaged` printing `Stars(13)`.
- Exercise 1: the error message was `Bad shape creation`, the chapter's is `Bad shape`.
- Exercise 2: the prose called the class `Triangle`; the listing defines `_Triangle`.
- Prose: removed "at all", "itself", "exactly", "actually", "is what allows", "wants", "spelling", an italic used for emphasis, a repeated "in miniature", and a second "points at nothing".

## Considered and declined

- `prototype.py` shows `clone()`, the shallow-copy warning, and `copy.replace()` in one listing. Splitting it repeats `Monster` three times, and the prose takes the three in order.
- `Monster` stays a mutable `@dataclass`. The listings mutate the clone, which a record forbids.
- `GameEnvironment.__init__()` is hand-written because it calls the factory. `PizzaBuilder.__init__()` is a standing exemption.
- No exercise covers "Subclasses Choose the Type". The chapter has eleven exercises and the section's own advice is to prefer the dictionary.
- The heading "Which Factory to Use" is no longer a question, unlike the set `deep_review_db.md` lists. It reads well and four chapters link nothing to it, so I left it.
- "Thus, *Factory* might be the most common design pattern" is an opinion no listing can settle. It is hedged and yours.
- Solutions 1 and 2 share one heading, "1 & 2". The numbering gate accepts it.
- A link from the new "Python looks up a name in a function body when the function runs" sentence to an earlier chapter. No section states that rule by itself, so the sentence stands alone.
