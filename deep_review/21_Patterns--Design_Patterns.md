> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 21_Patterns--Design_Patterns (2026-09-29)

This is the first review since the Coupling section merged in on 2026-09-24, and most of the findings are in that section.
I checked every GoF quotation and count against the text in `C:\git\DesignPatternsCD\markdown\` (the eight causes of redesign, the glossary's two coupling entries, the two design principles, the behavioral discussion, *Observer*'s consequences): all match.
I checked the four figures' labels and edges against the prose that describes them, each cross-chapter link against the section it names, the Norvig count (Singleton is one of his seven), PEP 234's release (2.2), and the Kay and Saint-Exupéry quotations.
Two `ty` probes back the Solutions claims and the corrected rename paragraph.
`tip verify-ch CH=21` passes 24 of 24, `tip verify` and `tip exercise-refs` pass, and Vale reports nothing in either file.

## Applied directly

Chapter, corrections:

- "What One Part Knows About Another": the rename paragraph said that after renaming a method on a class reached through a `Protocol`, "the callers keep working while the protocol keeps its name."
  They do not: the class stops matching the protocol, `ty` reports `invalid-argument-type` where the class is passed, and the call raises an `AttributeError` at runtime.
  The paragraph now says what holds: no caller's source changes, the renamed class stops matching, and the checker reports each place that passes it.
- "Reading the Chapters Ahead": "A note under each figure counts the heavy edges and says which way they point" described notes that commits b447e62c and dfd39688 removed.
  No panel has a note or a caption now.
  The sentence became an instruction to the reader: "In each figure, count the heavy edges and note which way they point."
- "The Edge Python Deletes": the link quoting "in libraries you cannot edit" pointed at chapter 20's `#protocols-generalize-composition-adapts`, and that section does not contain the phrase.
  It is in `### Protocols`, so the link is now `#protocols`.
- *Simplicity before generality*: the link said chapter 37 "works through a case of this, one requirement at a time" and pointed at `#choosing-the-lightest-construct`, the closing summary.
  The chapter works through the case, so the link now names the chapter.
- "inheritance 'breaks encapsulation'": GoF reports this as a saying ("it's often said that", citing Snyder).
  Now "repeats the saying that".
- "ranks four of them by it": GoF compares the four and ranks only *Observer* against *Command*, and "it" had no clear target.
  Now "compares four of them by their coupling", and the next paragraph's "A diagram makes that measure visible" is "A diagram makes coupling visible."

Chapter, prose:

- "Erased details are also where scaling limits come from" ended on a stranded preposition. Now "the source of scaling limits."
- "Every abstraction discards something (a copy, an ordering, a lookup behind an attribute)" read as though the abstraction throws away a copy.
  Now "hides some work (a copy, a sort, a lookup...)", and "one discarded detail dominates" is "one hidden cost dominates."
- Ladder paragraph: "reads its type", "every class that joins that set", and "nothing joins" each needed a second reading.
  Now "tests an object's type against it", "every class that implements them", and "no class declares that it implements them."
- The 40-word sentence that closed "Two rungs come free" held its subject open across two relative clauses. Split into two sentences, one per kind of language.
- "*Decorator* has no heavy edge at all" read as news after *Strategy* had none. Now "*Decorator*, like *Strategy*, has no heavy edge."
- "a `Callable` annotation is not a class at all": dropped "at all."

Chapter, teaching:

- Exercise 4 is new.
  Coupling is the chapter's longest section and had no exercise.
  The exercise has the reader build both halves of the reach figure and count the edits a Markdown writer causes.
  It is appended, so exercises 1 to 3 keep their numbers.

Solutions:

- Solution 4 is new: `exercise_4a.py` and `exercise_4b.py`, with the edit count for each (three edits in two parts, against one edit in one part), matching the figure.
- The opening paragraph said "All three exercises ask about your own experience." Now "The first three", with a sentence for the last.
- Solution 3 had two imperative-plus-consequence sentences ("Remove the abstract base ... and you have", "Remove `checkout()`'s `shipping` parameter ... and the program still runs"). Both are "If you remove" now.
- Solution 1: "it is not wrong, it just makes you the one who changes" was a comma splice ending on a figure of speech. Now "It is not wrong, but every new format is an edit you make by hand."
- Solution 3: "the design's actual intent" lost "actual."

## Stages three and four read as the same thing

"Pattern Evolution" defines stage three, **Standard Design**, as "a way to solve every problem of that kind, not just the one in front of you," and stage four, **Design Pattern**, as "how to solve an entire class of similar problems."
"Every problem of that kind" and "an entire class of similar problems" say the same thing, so the list does not tell a reader what changes between the two stages.
The paragraph after the list does: the self-registering dictionary is stage three because it is one program family's reusable design, and *Template Method* is stage four because it is "a shape of solution you could build in any language with polymorphism."

The definitions are yours (commit d33b3a50), so I left them.
I would move the distinction into the list:

> 3.  **Standard Design**: a specific design made general through reuse,
>     so it solves this kind of problem wherever it appears in your own programs.
> 4.  **Design Pattern**: the shape several standard designs share,
>     stated apart from any one program or language.
>     This usually appears only after you apply a standard design several times,
>     and then see a common pattern across those uses.

`[] Reject`

## Considered and declined

- "Two rungs come free in Python" is a figure of speech, and a `Protocol` is still a class you write.
  The paragraph explains the cost of each rung in its next three sentences, and the ladder figure's bracket says the same thing, so it stays.
- "23 patterns" beside "twenty-three times" and "twenty-three shapes": the numeral counts and the words are rhetorical. Left.
- "this handful of fundamental ideas" describes fifteen principles. Yours, and the sense is "few enough to remember."
- "Most hold for any code, but *Reflexivity* and the *Law of Demeter* assume classes and objects" leaves out Liskov substitution.
  A `Protocol` has subtypes without classes inheriting, so the sentence is defensible.
- "An abstraction is a bet about which details no caller will ever need" carries two watch-list items. The sentence reads well and "ever" does work there.
- The Coupling section says "GoF" where the introduction sets *GoF Design Patterns* as the name. "GoF" there names the authors, as chapter 39 does.
- `strategy_is_a_function.py` has no blank line between `apply()` and the `print()`. The listing is six lines and the house style minimizes blank lines.
- No figure changed, so `tools/coupling_panels.py` and the four section figures are untouched.
