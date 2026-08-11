When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the readability pass over `Chapters/17_Metaprogramming.md`,
run after the deep review in `deep_review/~17_Metaprogramming.md`.
The chapter is clean of AI-vocabulary clusters
(no Tier 1 or Tier 2 hits anywhere in the prose),
has no curly quotes, no spaced `--`, no boldface or list inflation,
and its rhythm varies naturally.
What remained were watch-list words that fail the deletion test
and two "is what" clefts, all settled mechanical rules,
so everything found was applied directly.
No findings needed a decision, so there are no live blocks.

## Applied directly

- Line 210, watch-list "itself": "reads `make()`'s result as `Event` itself"
  is now "as `Event`"; the base-not-subclass contrast is already carried by
  the preceding sentence about the checker not following `type()`.
- Line 341, "is what" cleft: "which is what a caller writing
  `try: ... except KeyError` around a lookup expects" is now
  "which a caller writing ... expects"; deletion changes nothing.
- Lines 892-894, treadmill restatement: "Otherwise, prefer `__init__()`,
  which is simpler." and "When the choice does not matter, pick `__init__()`
  and reserve `__new__()` for a genuine need." said the same thing twice,
  back to back; merged to "Otherwise, prefer `__init__()`, which is simpler,
  and reserve `__new__()` for a genuine need." No information lost.
- Line 967, "is what" cleft: "which is what a checker must confirm before it
  accepts a zero-argument `super()`" is now "which a checker must confirm ...".
- Line 1015, watch-list "ever": "predicts a crash before the program ever
  runs" is now "before the program runs"; the static-versus-runtime contrast
  is fully carried without it.
- Line 1101, §53 worth-frame: "`__prepare__()` is the one with no simpler
  substitute, so it is worth seeing:" drops the endorsement clause; the
  no-simpler-substitute fact is the justification, and the colon leads
  straight into the listing.
- Line 1362, watch-list "itself": "storage that lives on the object itself"
  is now "on the object"; the class/object contrast is explicit in
  "borrowed from the class from storage that lives on the object".
- Line 1467, watch-list "even": "before the `dunder` logic even sees the
  name" drops "even"; "The check runs first" already states the priority.
- Line 1664, watch-list "at all": "Decide whether an instance gets built at
  all" is now "gets built"; "whether" already frames it as yes-or-no.
- CRTP footnote, stranded preposition: "no equivalent incomplete-type stage
  to lean on" is now "to exploit" (close alternative considered: cutting the
  infinitive entirely; kept it because it says the C++ trick depends on that
  stage).

## Considered and declined

- "hook" throughout, including the "Which Hook for Which Job" heading:
  literal technical term, settled in the deep review. Not re-examined.
- Line 92, "what a `class` statement actually does": kept, settled in the
  deep review (real contrast with "a class definition is shorthand").
- Line 428, "only three fixed names ever reach the template": "ever" kept;
  it universalizes the security guarantee (no execution path lets another
  name through), which "only" alone does not state.
- Line 556, "The commented line is what the type checker rejects": the
  keep-case of the "is what" rule; deleting it breaks the sentence.
- Line 406, "so `namespace[class_name]` is just `Any` to it": "just" kept as
  the diminishing beat; it carries "no more precise than".
- Line 71, "You have used metaclasses already": "already" carries
  prior-to-this-chapter and stays; same for the timing uses at lines 433,
  628, 915, 980, 1139, and 1466.
- Line 63, "even ones already created": both words draw the real surprise
  (class changes reach pre-existing instances); kept.
- CRTP footnote, "before the name `ASingleton` is even bound": "even" kept;
  it draws the contrast with C++, where the name is bound but incomplete.
- Line 1090, "unless you truly need them": kept; echoes the intro's "the
  temptation to use it is strong" and distinguishes need from temptation.
- Line 1015, "static typing at its best": authorial stance, kept.
- "Can a metaclass inherit from more than one class, the way an ordinary
  class can?" (§43 by shape): a genuine structural question the section
  then answers two ways; not a stalling transition.
- "Here is the job list:" (§28 by shape): a one-line label on a genuine
  list, not an announcement standing in for content.
- Lines 168-170, "pays off when a family of classes differs only by name" /
  "Where you might otherwise write many near-identical subclasses by hand":
  mild restatement, but the second sentence adds the by-hand alternative
  the first does not name.
