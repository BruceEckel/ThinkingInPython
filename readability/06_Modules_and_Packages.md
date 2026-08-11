# Readability review: 06_Modules_and_Packages

> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

The chapter reads human throughout: sentence lengths vary,
each paragraph advances the mechanism it describes,
and no Tier 1A vocabulary, curly quotes, spaced ` -- `,
or structural tells appear.
The deep review's applied and declined lists were honored:
nothing it settled ("is what" at the documentation-tools sentence,
the end-of-listing markers, the `none`-mode sentence) is re-raised here.
Every remaining finding had one sensible answer,
so everything went into the applied-directly list
and nothing below needs a verdict.

## Applied directly

- Line 40, misplaced "only": "you only want its definitions"
  became "you want only its definitions,"
  matching the deep review's identical fix at "is true only when."
- Line 85, watch-list "already": "every name already bound by a
  `from ... import`" became "every name bound by a `from ... import`";
  "Reloading leaves" supplies the before-the-reload timing.
- Line 86, construction repeated back-to-back: the paragraph's second
  "which is why" (lines 81 and 86) became "so restarting is the
  reliable choice."
- Line 325, stranded preposition: the relative-import gloss
  "the package this module lives in" became
  "the package containing this module."
- Line 382, imperative-plus-consequence: "Assign it at module level
  ..., and `from module import *` imports those and no others" became
  the declarative "You assign it at module level ...";
  the second clause is unchanged.
- Line 464, watch-list "at all": "with no setup at all"
  became "with no setup."
- Line 469, filler verb: "isn't placed in the same directory as the
  Python file that's doing the importing" became "isn't in the same
  directory as the Python file doing the importing."
- Line 470, watch-list "was to": "The original solution to this was to
  set an environment variable called `PYTHONPATH`" became
  "The original solution was the `PYTHONPATH` environment variable."
- Line 477, stranded preposition: "the environment you are working in"
  became "the environment you are using."
- Line 495, dangling participle: "so a run pays only for the modules it
  uses, while still declaring all imports at the top of the file"
  (the run does not declare anything) became
  "while all imports stay at the top of the file."

## Considered and declined

- **"which is why" as the chapter's causal connector** (seven uses
  before this pass: lines 81, 86, 147, 233, 464, 487, 546).
  Uniform-construction density by the structure test, but each use
  connects a listing's observed output to the mechanism behind it,
  the book's standard move. Varied only the one paragraph where two
  sat adjacent (line 86, above); rewriting the rest is churn.
- **"What if your module or package isn't in the same directory ...?"
  (line 469).** §43 rhetorical-question opener by shape, but it frames
  the genuine problem the `PYTHONPATH` section answers rather than
  stalling before a point, and it is first-edition voice. Kept.
- **"check what a run actually put off" (line 550).** Watch-list
  "actually," carrying the observed-versus-declared contrast:
  `sys.lazy_modules` reports what this run deferred, as opposed to
  what the `lazy` keywords marked. Kept.
- **"a lazily imported name nobody touches never loads" (line 568).**
  Watch-list "never," but the claim is that the load occurs at no
  point in the run, which "does not load" would soften; the silent
  missing side effect is the point of the paragraph. Kept.
- **"the same dict Python already searches" (line 144).** Watch-list
  "already," earning its place: the search exists whether or not you
  call `globals()`, the same reasoning that kept 33_Visitor's
  "already" in `readability_db.md`. Kept.
- **"The failure is silent: no error, just a table with a row missing"
  (line 569).** §9 tailing fragment by shape, but the fragment is
  concrete (the specific missing-row consequence), not a vague
  "no guessing" tag. Kept.
- **"The underscore changes one mechanical thing:" (line 379).**
  §69 colon reveal by shape; the colon introduces the one counted
  fact rather than staging a surprise, the definition use
  `readability_db.md` records as clean. Kept.
