> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 37_Patterns--Pattern_Refactoring, second review (2026-09-29)

This review follows the completed one of 2026-09-25 (`~37_Patterns--Pattern_Refactoring.md`) and the five commits made after it:
the `ClassVar[float]` restatement, the two opener commits, the fix triage of 2026-09-27, and the negative-ending rewrite.
Nothing here needs your decision, so the file has no live blocks.
Probes ran in `build/examples/37_*` under `ty` 0.0.84 and the pinned 3.15.0rc2.
Every checker claim in the chapter holds:
`ty` rejects `Trash(1.0).value = 2.0` and `Aluminum(1.0).value = 2.0`, accepts `bins: Bins = {}`,
and that dictionary raises a `KeyError` on the first piece.
At runtime `Aluminum.create("Paper", 1.0)` returns a `Paper`, `case Aluminum()` matches a `CrushedAluminum`,
`recycling_note()` returns `Aluminum`'s note for it,
and `create()` raises a `KeyError` for an unregistered name.
`tip verify-ch CH=37` passes 24 of 24.

## Applied directly

Chapter, damage from the edits made after the first review:

- "The First Cut": the triage cut "Here is the requirement that makes it concrete" and left "That is the argument." with nothing to announce.
  That sentence is gone, and the paragraph opens "Now the plant starts accepting plastic".
  The lead-in also names the data before the class, the order in which the two listings appear.
- "The Data File and Its Parser": the triage rewrite put "So adding a new kind of trash..." directly after "so it never names a concrete material".
  The two sentences are now one, with a single "so". The words "needs no edit to the parser, and cannot break it" are unchanged.
- "A Method on Every Material": with its lead-in cut, the section opened on "The plant already prints a recycling instruction",
  and nothing earlier in the chapter prints one.
  It now says the instruction comes from a `note()` method on each class, which the listing then shows.

Chapter, corrections:

- "you must find every `case` statement": `case` is a clause of the `match` statement. Now "every `match` statement".
- "The program changed in two places" compared `recycle_dict_plastic.py` with `recycle_dict.py`,
  and the listing also adds the two lines that count the pieces.
  Now "Handling plastic takes two changes to `recycle_dict.py`", with a sentence saying what the last two lines are for.
- "Choosing the Lightest Construct": "this chapter used", "This chapter met", and "Each vector now lands in one place"
  are now "uses", "meets", and "touches one place", the verb the chapter's opening uses for the same idea.

Chapter, teaching:

- `assert_never()` paragraph: it said exhaustiveness needs a closed union and stopped.
  A probe shows what the reader who tries it sees:
  `ty` reports `assert_never(t)` although the `match` names all four materials,
  since the remainder is `Trash & ~Aluminum & ~Paper & ~Glass & ~Cardboard`, not `Never`.
  The paragraph now says the report appears whether or not a `case` is missing, so it cannot find the missing one.
- Exercise 5 is new, with its solution.
  The fallback risk (a forgotten registration gets the default answer) was stated and had no exercise,
  and no exercise asked the reader to write a `singledispatch` operation.
  The fallback paragraph points to it with "(see exercise 5)", accepted into `exercise_refs_baseline.txt`.
  It is appended, so exercises 1 to 4 keep their numbers.

Chapter, prose:

- "Point this sorter at `plastic.dat`" commanded the reader to do what the listing does. Now "The next listing points this sorter at...".
- "warns against exactly this shape" is "warns against this shape"; "with no edit at all" is "with no edit";
  "has to search" is "must then search"; "and never checks what type a piece is" is "without checking the type of a piece".

Solutions:

- Exercise 1: "Two changes remain: the data files gain `Plastic:NN` lines" contradicted the exercise,
  which points `recycle_dict.py` at `plastic.dat`, a file that has those lines. One optional step remains, the registration.
- Exercise 1: the accounting the exercise asks for now gives the number.
  Sixty pounds at 0.15 is the `Total value = 9.00` line that `recycle_dict_plastic.py` prints and `plastic_dropped.py` omits.
  "The plant gets a report that balances against nothing" is replaced by what the report shows.
- Exercise 1: "That class" opened the prose with no class named; now "The `Plastic` class".
  "Update the expected set and the test goes back to guarding..." was an imperative with its consequence; now "Once you update...".
- Exercise 2: "Both read only `t.weight` and `t.value`" was wrong for `heaviest()`, which reads `t.weight` alone.
- Exercise 3: the listing defined `registry` and `__init_subclass__()` and used neither.
  Its loop now reads `Trash.registry.values()`, as `recycling_note.py` does. The markers are unchanged.
  The prose gains the trap the chapter names beside `singledispatchmethod`: a subclass of `Sorter` shares the dispatcher.
- Exercise 4: `CrushedAluminum`'s `bin = Aluminum` was a bare override of a `ClassVar`,
  the form the chapter's subclasses stopped using on 2026-09-25.
  It now restates `ClassVar[type[Trash]]`, and the prose says why.
  "The lesson generalizes past this exercise" is cut.
- Exercises 1 to 3: flourish words removed ("simply", "actually", "genuinely", "earns its place", "identical", "plain function").

Checked and correct: the four links into chapter 32 and the one into chapter 12 credit those sections with what they say;
chapter 33 gives the `NotImplementedError` advice and explains the `_` placeholder under the linked heading;
chapter 13's "When Not to Match" and "The Expression Problem" say what this chapter credits them with;
the markers of all nine run listings and the four tests.

## Considered and declined

- The material classes are undecorated subclasses of a record, so their instances carry a `__dict__` and are not records.
  Decorating each with `@record` would run `__init_subclass__()` twice per class, since `slots=True` builds a second class,
  and would add a second topic to `trash.py`. No sentence in the chapter claims the subclasses are records.
- "Readers of *Composite* and *Interpreter* may expect `assert_never()`": chapter 13 teaches `assert_never()` first.
  Chapter 34 is the nearer chapter and states the expectation in its own prose, so the attribution stays.
- "cannot break it" in the parser lead-in: a material class with a second field would break `create()`.
  The clause is the one you accepted on the triage page, and the failure would sit in `create()`, not in the parser.
- "The key is the *exact* class": the italics mark the term the exact-type dispatch thread uses (chapters 31, 32, and here).
- The `# Dollars per pound (per subclass)` comment in `trash.py`: the first review left it, and the unit appears nowhere else.
- Exercise 1 also changes what `recycling_note.py` and `disposal_hazard.py` print, since both loop over the registry.
  The exercise asks about the sorter and the test, and a longer question would bury both.
