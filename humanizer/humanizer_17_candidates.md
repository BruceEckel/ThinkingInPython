[[Reviewed]]
# Humanizer candidates: Chapters/17_Metaprogramming.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

## How to use this

Each edit is a `###` block with a CURRENT and a PROPOSED fence.
Delete any block you don't want, save the file, and hand it back to me.
I apply what survives, verbatim, and run `make verify`.

The CURRENT fences are exact copies from the chapter,
so don't hand-edit inside them or the match will fail.
If you want a different wording, edit the PROPOSED fence instead
and I will use yours.

Tier A is what I'd apply. Tier B is genuinely arguable, delete freely.
Housekeeping is not humanizer output; separate list at the end.

## Verdict

Mostly clean. The chapter's only real cluster is person: four "we" sites
(one pair back to back in the opening paragraph, two more at later section
openers) in a book written second person throughout. There's also a
recurring "X itself" tic, dense enough to be worth a pass but genuinely
mixed, some sites draw a real contrast and earn the word. One bullet list
breaks its own parallel structure for no reason. No em dashes anywhere in
the chapter, no word-level AI vocabulary, no promotional language, no
fragmented-header padding beyond two borderline openers.

## Tier A

### A1 — lines 4, 7, 953, 1007 — person consistency

Four first-person-plural sites in a chapter that otherwise addresses the
reader as "you" throughout. Two sit back to back in the opening paragraph.
Delete individual rows you want left alone.

**line 4**

CURRENT
```text
These special objects are called *classes* and we configure them to produce desired objects.
```

PROPOSED
```text
These special objects are called *classes* and you configure them to produce desired objects.
```

**line 7**

CURRENT
```text
We can modify objects:
```

PROPOSED
```text
You can modify objects:
```

**line 953**

CURRENT
```text
Up to now we've been modifying classes.
```

PROPOSED
```text
Up to now, you've been modifying classes.
```

**line 1007**

CURRENT
```text
Throughout the book we've been using `display_object()` to show the layout of an object.
```

PROPOSED
```text
Throughout the book you've been seeing `display_object()` to show the layout of an object.
```

### A2 — lines 530, 689 — "itself" adds nothing

Both sites are a noun re-tagged with "itself" where the noun already said
it plainly, the exact shape CLAUDE.md's rule warns against ("the class
itself," where "the class" alone says the same thing). Neither draws a
contrast; dropping the word changes nothing.

**line 530**

CURRENT
```text
That branch returns `self`, the descriptor object itself,
which is why `isinstance(Point.x, Field)` is `True`.
```

PROPOSED
```text
That branch returns `self`, the descriptor object,
which is why `isinstance(Point.x, Field)` is `True`.
```

**line 689**

CURRENT
```text
`setattr(cls, ...)` still works because it modifies the class object itself.
```

PROPOSED
```text
`setattr(cls, ...)` still works because it modifies the class object.
```

### A3 — line 1306 — broken parallel in a bullet list

Four bare dunder names, then a fifth item that swells into a full sentence
with an attached clause. Making the list uniform and moving the
explanation into its own sentence (the paragraph already does this for
the next group of dunders, "The rest, from `__class__` to
`__static_attributes__`, is the bookkeeping every class carries") reads
more consistently.

CURRENT
```text
- `__dataclass_fields__`
- `__match_args__`
- `__replace__`
- `__hash__`, set to `None`
- The generated `__init__`, `__eq__`, and `__repr__`,
  which give `Fraggle` a constructor, equality, and a `repr()` for free.
```

PROPOSED
```text
- `__dataclass_fields__`
- `__match_args__`
- `__replace__`
- `__hash__`, set to `None`
- `__init__`, `__eq__`, and `__repr__`

The generated `__init__`, `__eq__`, and `__repr__` give `Fraggle` a constructor, equality, and a `repr()` for free.
```

## Tier B

### B1 — lines 563, 909 — fragmented headers

Both section openers restate the heading in a rhetorical throat-clear
before the real content lands one sentence later. Precedent from
chapters 46/47 treats this as a per-instance call, not a rule, so these
are genuinely arguable rather than clear cuts. I lean toward applying
both: neither loses any information, and both get to the point faster.

**line 563**

CURRENT
```text
## Writing a Metaclass

When the simpler hooks are not enough, write a metaclass.
A metaclass is a subclass of `type`.
You attach it with the `metaclass=` keyword in the class header.
Python then uses your metaclass, instead of `type`, to build the class.
```

PROPOSED
```text
## Writing a Metaclass

A metaclass is a subclass of `type`,
used when the simpler hooks are not enough.
You attach it with the `metaclass=` keyword in the class header.
Python then uses your metaclass, instead of `type`, to build the class.
```

**line 909**

CURRENT
```text
## When You Still Need a Metaclass

After all this, when is a metaclass the right tool?
When you need to change the class object rather than react to its creation:
```

PROPOSED
```text
## When You Still Need a Metaclass

Use a metaclass when you need to change the class object rather than react to its creation:
```

### B2 — lines 6, 54, 758, 1293 — "itself" flourish, borderline

Same tic as A2, but each of these sits closer to a real contrast (the
class also being an object, the instance versus the class that did
change, the class versus the method-level fix, the class versus the
instance inspected two rows down), so the case for keeping each is
stronger than in A2. I lean toward cutting all four anyway, since in
each case the surrounding sentence already carries the contrast without
help from the word. Delete individual rows you want left alone.

**line 6**

CURRENT
```text
So, classes are themselves objects.
```

PROPOSED
```text
Classes are also objects.
```

**line 54**

CURRENT
```text
The instance itself never changed; its `__dict__` is as empty as before.
```

PROPOSED
```text
The instance never changed; its `__dict__` is as empty as before.
```

**line 758**

CURRENT
```text
You might expect to parameterize[^parametrize] the class itself,
with `class Singleton[T](type)` and `_instances: ClassVar[dict[type, T]]`.
```

PROPOSED
```text
You might expect to parameterize[^parametrize] the class,
with `class Singleton[T](type)` and `_instances: ClassVar[dict[type, T]]`.
```

**line 1293**

CURRENT
```text
`display_object(Fraggle)` inspects the class object itself.
```

PROPOSED
```text
`display_object(Fraggle)` inspects the class object.
```

## Housekeeping

1. **Listing comment, line 1100** (`utils/display.py`, inside the
   `display_object()` fenced block): the comment reads
   `# For a class, the class itself; for an instance, its class:` and
   carries the same "itself" flourish as the Tier A/B prose findings
   above (`the class itself` says nothing `the class` doesn't). If
   Bruce wants it changed, the fix is dropping "itself" from the
   comment; applying it needs a re-sync (`make verify` does this). The
   code the comment sits next to is unaffected.

## Considered and not flagged

- **Em dashes.** Zero in this chapter, `---` and spaced ` -- ` both
  absent. Nothing to report either way.
- **Italics.** Every italicized term (*classes*, *metaclasses*, *Class
  decorators*, *descriptor*, *data descriptor*, *class object*,
  *metamethods*, *class variable*) introduces that term on first use.
  None is used for bare emphasis.
- **"itself" sites left alone.** Three more hits looked at and kept:
  line 568 ("a metaclass is itself a subclass of `type`") does real work
  setting up why naming it as a base class means something different
  from using `metaclass=`; line 1157 ("storage that lives on the object
  itself") parallels "storage borrowed from the class" earlier in the
  same sentence and the contrast would blur without it; line 1184
  ("which can look like the class defined them itself") is the
  paragraph's actual point, that the dunders only look self-defined but
  are inherited unchanged from `object`.
- **"not only descriptors" (line 472).** Reads like §9's negative
  parallelism at a glance, but it's an ordinary qualifier ("every class
  attribute that defines it, not only descriptors"), not the "not
  only...but" rhetorical pairing the pattern describes. No "but" half,
  no manufactured drama.
- **Word-level AI vocabulary (§7).** No hits: no *delve*, *crucial*,
  *pivotal*, *tapestry*, *landscape*, *underscore* (verb), *fostering*,
  *garner*, or similar. Consistent with the note that this scan is
  usually a dead end in this book.
- **Rule of three (§10).** Several three-item and four-item bullet
  lists (the simpler-hooks list near the top, the `inspect` predicates,
  the metaclass use cases at the end), but each enumerates genuinely
  distinct technical options rather than padding for the appearance of
  thoroughness.
- **Everything else on the pattern list.** No promotional language, no
  vague attributions, no "Challenges" section, no copula avoidance, no
  false ranges, no elegant variation, no hedging, no filler phrases, no
  boldface overuse, no inline-header vertical lists, no emojis, no curly
  quotes, no collaborative-communication artifacts, no knowledge-cutoff
  disclaimers, no sycophantic tone, no aphorism formulas, no
  conversational rhetorical openers, no diff-anchored writing, no
  staccato drama.

## Scan coverage

Full word-level sweep (§7 AI vocabulary, §1-6 content-pattern phrase
lists, §26 hyphenated-pair overuse) came back clean, as did the
structural checks for boldface, vertical lists, emojis, curly quotes,
em dashes, and draft notes. Blank-line hygiene is clean throughout
(no double blank lines before any heading). Structural attention went
to person (one real cluster, applied), italics (clean), fragmented
headers (two borderline sites), broken parallels (one site), and the
CLAUDE.md "itself" rule (checked every instance individually rather
than as a blanket word search, since several genuinely earn their
place). A rerun can skip the word-level sweep and focus on anything
merged into this chapter later.
