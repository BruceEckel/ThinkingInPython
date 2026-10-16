> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/34_Patterns--Composite_and_Interpreter/README.md`,
2026-10-16.
The prose carried few AI-writing tells. The fixes that went in directly
are mostly "and" joining clauses with different subjects, italics used
for emphasis, and bold step labels echoed word for word by the sentence
after them. No finding needed Bruce's judgment, so this file holds no
live block and serves as the applied-directly record.
Claims touched by an edit were read against their listings first: the
`Neg` rewrites in exercise 3's `simplify()`, exercise 7's
`to_query()`/`to_shape()` loops in the chapter, exercise 8's
`work += [Op.ADD, right, left]`, and exercise 9's `@abstractmethod`.
Every bold-label line that ran to 90-120 columns was rewrapped to the
file's hand-wrap of about 70; the Hint paragraphs and the trap-first
openings, which break by clause, were left in that form.
`tip verify-ch CH=34 ISOLATED=1` passed, 27 of 27.

## Applied directly

Line numbers are those of the edited file.

- Line 47, pointer: "That `Directory` case descends" became "The
  copied `Directory` case descends", since "That" had to reach back
  past the two `find()` calls to the copied `walk()`.
- Line 104, italics for emphasis: "continues *into* a matched
  directory" lost the italics.
- Lines 346-347, "and" joining different subjects: "`int.__truediv__()`
  returns `NotImplemented` for a `Var`, and Python finds no reflected
  method" became two sentences, the second with "then".
- Lines 511-512, §34 "real": "`simplify()` gains real rewrites. For
  `Neg`, it folds..." became "`simplify()` gains two rewrites for
  `Neg`. It folds...", which counts the two the sentence then names.
- Lines 520-521, "and" joining different subjects, and an unstated
  step: "A quotient of two `int`s is usually a fraction, and a `Num`
  holds an `int`" became "A `Num` holds an `int`, and a quotient of two
  `int`s is usually a fraction, which no `Num` can hold", so the reason
  for keeping the division is on the page.
- Line 525, contrast hidden by "and": "`simplify()` rewrites a tree,
  and `evaluate()` computes the tree's value" became two sentences.
- Line 532, same rule: "The compiler accepts it, and Python raises
  the `ZeroDivisionError`" became two sentences.
- Line 682, italics for emphasis: "the precedence its *parent*
  requires" lost the italics.
- Line 690, italics for emphasis: "at the *same* precedence" lost the
  italics.
- Lines 900-904, "and" joining different subjects: "Exercise 3 adds
  `Neg` and `Div` to `Expr`, and differentiating a `Div` needs the
  quotient rule. That rule produces..." became "Exercise 3 adds `Neg`
  and `Div` to `Expr`. Differentiating a `Div` needs the quotient rule,
  which produces...". The exercise reference is unchanged.
- Lines 1051-1053, consequence joined by "and": "so this `Num` holds a
  string, and every walker mishandles it" became "so this `Num` holds a
  string. Every walker mishandles that `Num`."
- Lines 1055-1058, same rule: "so it declines the string, and Python
  falls back to `str` concatenation" became two sentences, the second
  with "then".
- Lines 1155-1157, vague "whole" and a missing referent: "The whole
  walker is the same loop with a different body" became "`to_html()`
  runs the same `for piece in template` loop as those two walkers with
  a different body". The chapter's `to_query()` and `to_shape()` both
  open with that loop.
- Lines 1159-1161, §34 "real" plus emphasis italics, and a vague
  "the characters": "`html.escape()` replaces the characters, so the
  exercise's real content is *where* `to_html()` calls it" became
  "`html.escape()` does the replacing, so the exercise comes down to
  where `to_html()` calls it".
- Line 1168, positional pointer: "The f-string on the last line
  produces" became "The f-string produces"; the listing has one
  f-string.
- Lines 1380-1382, contrast joined by "and": "combines two values when
  its two calls return, and a stack version must arrange that moment"
  became two sentences.
- Line 1385, italics for emphasis: "its children's values *after* the
  children" lost the italics.
- Lines 1391-1393, "and" joining a claim and its consequence: "makes
  `left` pop first, and that order matters" became two sentences.
- Lines 1398-1400, consequence joined by "and": "leaves `case _`
  reachable, and the type checker then rejects" became two sentences.
- Lines 1542-1547, label echoed by its first sentence: "**Move the
  operation onto the classes.** Moving the operation back onto the
  classes undoes ..." became "... The open design undoes ...". The same
  paragraph's "adding a *new operation*" lost its emphasis italics.
- Lines 1549-1551, label echoed by its first sentence: "**Enforce the
  contract on plugins.** The `@abstractmethod` enforces the contract on
  the plugin. Python raises a `TypeError` when..." became "Because
  `disk_usage()` is an `@abstractmethod`, Python raises a `TypeError`
  when you instantiate a subclass that leaves it abstract."
- Line 1558, italics for emphasis: "The four node types *are* the
  grammar" lost the italics.
- Lines 97-99, 231-234, 243-244, 507-509, 518-519, 681-682, 883-885,
  891-893, 1064-1067, 1074-1076, 1151-1154, wrapping: bold-label lines
  ran to 90-120 columns and were rewrapped with no change to the
  wording.

## Considered and declined

- The trap-first opening of each Solution step followed by bold labels
  that walk the same fix (exercise 2's `RecursionError` at lines
  170-172 and 245-247; exercise 6's forward guard at lines 976-983 and
  1064-1067): the Solutions files' usual shape, where the opening shows
  the wrong version failing and the labeled paragraphs walk the
  listing. Not a treadmill.
- Line 896, "into the much more readable `(x + x)`": "much" is an
  intensifier by shape, but the comparison is the point of running the
  result through `simplify()`, and the two `#:` lines sit just above.
- Line 1060, "The message comes from `str`, which is the right
  source": a judgment, followed at once by its two reasons.
- Lines 1060-1062, "and no method in this expression language accepts
  a `str`": the two clauses are parallel reasons for the same verdict,
  additive.
- Line 1075, "the type it really returns": §34 by shape, but the
  contrast is named in the same sentence (`NotImplemented`), the
  "real/actual" keep.
- Line 1088, "An interpreter exists to handle that case.": a short
  closing beat that ties the runtime check to the chapter's pattern,
  not an aphorism formula.
- Lines 1531-1532, "The type checker does warn the plugin author":
  the emphatic "does" answers the expectation the previous sentence
  sets up (the union lives in your file), and the next sentence names
  the diagnostic.
- Line 688, "is simple and always safe": "always" states the guarantee
  that the next two sentences qualify (one redundant pair, never a
  missing one). A watch-list absolute that states a guarantee stays.
- Lines 1402-1413, the three `sys.setrecursionlimit()` drawbacks in one
  paragraph: the paragraph answers one question, the exercise's "Name
  its drawbacks", and the "First, Second, Third" inventory is what the
  exercise asks for.
