> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Second deep review of chapter 32 and its Solutions file, run 2026-09-29 after
the 2026-09-27 fix triage.
It carries forward `~32_Patterns--Multiple_Dispatching.md`, which has no
rejections.
The `ty` claim in the `-> Meters` paragraph was re-probed on `ty` 0.0.84:
`Meters | NotImplementedType` still draws `unresolved-attribute` on
`(Meters(1) + Meters(2)).n`.
`tip verify-ch CH=32`, `tip spell`, and `tip prose` are clean.

## Applied directly

- "That original caller arrives ... as its `item` argument": the triage cut
  "A richer game reads the caller's state through it.", which left a
  paragraph that names the argument and then says the game ignores it, with
  no reason it exists. Restored as "A game whose outcome depends on the
  caller's state reads that state through `item`." It also sets up the
  first reason "Methods or Table" gives for the double-dispatch version.
- "(see exercise 1)" sat on the `NoTransition` sentence, where the
  2026-09-25 pointer conversion moved it. It stood for "Adding `Lizard` in
  exercise 1 puts you in that situation", about a table you are still
  filling in, so it now ends that sentence.
- `match` section: "it matches subclasses: a class pattern tests with
  `isinstance()`, so a subclass matches the pattern its base would:" had two
  colons; split at the first.
- "the table lookup in `exact_match.py` raised `KeyError`" is now "raises a
  `KeyError`" (standing behavior).
- Ladder paragraph: "The type tests repeat in every class, as in the method
  version" said the method version has type tests. It repeats `eval_*()`
  methods, and the sentence now says so.
- "the easier form to write" right after "awkward to write": dropped the
  second "to write".
- `radd_dispatch.py`: the comment "# Int declines; the right operand handles
  it" capitalized a type name. Now "# int.__add__() declines;
  Meters.__radd__() handles it", which names both methods and starts with
  code, so the capitalization check leaves it alone.
- Solution 3 did not do what exercise 3 asks: it printed `len(EXPECTED)`,
  and its prose claimed the test passes over both modules, which is true
  only for modules that include `Lizard`. It now imports exercise 1's table
  and exercise 2's methods and checks all sixteen answers against both.
  Exercises 1 and 2 guard their demonstrations with `__main__`, as the
  chapter's two versions do, so the import prints nothing. The prose says
  which modules the test needs.
- Solution 2's closing said the chapter "reserves the method version for
  combinations that need real, type-specific logic too large for one table
  cell." The chapter says a cell can hold a function (exercise 9), and it
  gives two other reasons: behavior that reads the object's state, and a
  subclass that overrides one combination. The sentence now gives those.
  The same paragraph also lost "*existing*" (italics for emphasis) and "one
  line each" (each new method is two lines).
- Solution 7: exercise 7 asks for a `Project` that makes the inhabitants
  interact, and the loop sat outside the class. It is now `Project.meet()`.
  "genuinely *double* dispatch" lost the intensifier and the emphasis
  italics.
- Solution 9: "That answers the part of the question about keeping the
  syntax of a method call over a table" referred to an older wording of the
  exercise. Now "A table of callables keeps the method-call syntax." Two
  unwrapped long lines were rewrapped, and a semicolon splice was split.
- Solution 10: `isinstance(winner, (Inhabitant2, type(None)))` printed
  `True` for any possible result, so it showed nothing. Now it prints the
  winner's class name (`Elf2`). Its closing link pointed to "One Type or
  Many", but the "shorter and easier to maintain" conclusion is in
  "Methods or Table". Relinked, and the chapter's wording is used.

## Solution 8 has no second dispatch

Exercise 7 ends "The next exercise adds the second dispatch", and
exercise 8 asks you to decide which weapons win "as in
`paper_scissors_rock.py`", the double-dispatch version.
Solution 7's closing also says exercise 8 adds that dependence.
Solution 8 makes `Weapon` an `Enum` and decides every pairing with one
arithmetic function, `weapon_outcome()`, so no dispatch happens at all.
Solution 10 ("rebuilt on a table") then compares that formula with a table
built from it, and leaves out `Troll2` and `meeting()`.

The faithful solution makes the six weapons classes with `compete()` and
six `eval_*()` methods each: 42 methods, about 90 lines.
Its length would show the chapter's point about the method version's cost,
and solution 10 would then build the table by hand or from the classes and
keep `meeting()`.
The alternative keeps the formula and changes the exercise instead:
drop "The next exercise adds the second dispatch" from exercise 7 and say
in exercise 8 that the weapons may decide by rank.

I recommend the faithful solution, since exercises 7, 8, and 10 are the
chapter's only practice in writing a second dispatch outside the game.
This is a choice between a long solution and a change to what the
exercises teach, so it is yours.

`[] Reject`

## Considered and declined

- Solution 4 defines `duel()` and never calls it (`pass  # duel(item1,
  item2) in the real version`). Calling it would print 100 lines; the
  comment explains the stub.
- "Turning One Unknown Type Into a Second Dispatch" titles a section that
  also covers the table, which replaces both dispatches. The title names
  the question the three techniques answer, so it stands.
