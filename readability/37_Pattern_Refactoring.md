> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/37_Pattern_Refactoring.md` (r2)

A sweep of the Tier 1A, 1B, 2 and 3 vocabulary tables returns zero hits, and
there is no boldface, no curly quote, and no spaced ` -- `.
Everything below was in prose that had never had a readability pass: the deep
review's manifest edits and today's apply.

Every finding was resolved directly and applied (listed below).
No blocks remain.

## Applied directly

- "so a `CrushedAluminum` derived from `Aluminum` lands in a bin of its own"
  → "gets a bin of its own" ("lands" is on the global "Don't use" list; "it
  sorts into its own bin" nearby keeps its own verb, so the two stay
  consistent without repeating).
- Three `is what` clefts, each followed by a verb, each passing the deletion
  test unchanged:
  - "which is what [Pattern Matching] warned against" → "which [Pattern
    Matching] warned against."
  - "which is what the next section does" → "which the next section does."
  - "The `defaultdict(list)` is what creates a bin the first time a material
    turns up." → "The `defaultdict(list)` creates a bin..."
- `Choosing the Lightest Construct`: "Here that meant two lines of Python."
  → "Here each vector cost one line at the point of use: `bins[type(t)]`
  for a new material, one `@recycling_note.register` for a new operation."
  (the old count was checkable and false: `recycling_note.py` runs to
  sixteen lines. The per-use cost is the claim the chapter proved, echoing
  "cost a line instead of an edit spread across classes" from the
  singledispatch section. The cheaper alternative was dropping the count.)
- "The First Cut": "That is what "silently drop trash on the floor" means:
  not an exception to debug, but a number that is wrong and looks right."
  → ""Silently drop trash on the floor" means a number that is wrong and
  looks right, not an exception to debug." (removes the cleft and the
  staged colon while keeping the sentence's rhythm; the fuller rewrite the
  review drafted lost that rhythm for no extra content).
