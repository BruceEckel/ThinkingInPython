> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 29_Patterns--Changing_the_Interface (2026-10-13)

No live blocks: every finding had one sensible answer, so it is applied below.
I checked each claim against its listing and the sections it links in chapters 20, 21, 24, and 26,
re-probed the `ty` claims with `ty` 0.0.86 (the narrow override draws `invalid-method-override`
plus an `invalid-argument-type` at the `ProxyAdapter` call, `use(WhatIHave())` is rejected,
a deprecated overload and a deprecated class are both reported),
and re-ran the recursion-trap and default-warning-filter claims on Python 3.15.0 final.
`tip verify-ch CH=29 ISOLATED=1` passed 27 of 27 before and after.

## Applied directly

Chapter:

- Opening: the paragraph held the two patterns and the deprecation step; split in two.
  "callers keep using the old one until you mark it deprecated" said the mark stops them;
  it now says the mark tells them to switch.
- `adapter.py`: dropped the `# Implement behavior using WhatIHave:` comment, which the sentence after the listing already says.
- "What an Override May Change": "the listing's second call" made the reader count;
  it now names the call and the diagnostic, `invalid-argument-type` (probed).
- "Adapter in Python": "works and no shared base class takes part" is now "works, whatever its base classes";
  "the base class is gone" (passive) is now "`ObjectAdapter` keeps the check ... and drops the base class."
- `checkout_demo.py` prose: "The caller imports one name" was ambiguous (`import checkout` binds one name, the module);
  now "imports the module and calls one function, `total()`."
- "Distinguishing the Wrappers": "says that distinction remains when structures match" left "that distinction" unclear;
  now states chapter 21's point, that the difference remaining between two patterns with one structure is intent.
- The table's last column, "Remove it and you lose", was an imperative-plus-consequence; now "What removing it loses",
  with exercise 4 updated to name the column.
- "Deprecating the Old Interface", teaching: added the `category=FutureWarning` option, which Python shows by default (probed),
  as the answer to the trap the paragraph describes; and a new paragraph on the lookalike most readers meet in existing code,
  a `warnings.warn(..., DeprecationWarning)` call in the body, which supplies the runtime half alone.

Solutions:

- Exercise 1: "`len(adapter)` fails" is now "raises a `TypeError`", matching the marker.
- Exercise 3: "`Facade` is a namespace the language does not treat as one" and "carry it around" were unclear;
  the paragraph now says `Facade` is a class used as a namespace and names what it adds over the module
  (a `class` statement and a `@staticmethod` per function).

## Considered and declined

- **Exercise 2's output does not show which step warned.** Both recorded warnings print the same message.
  Printing a count after each step would need indented `#:` markers inside the `with` block, which the book avoids;
  the prose names the two sources.
- **"The static half is a `ty` diagnostic"** keeps `ty` by name: Pyright and mypy report deprecation only with a rule switched on,
  which the chapter says two paragraphs later.
- **"With no base class above it, `Adapter` is a record."** Reads as an aside, but it sets up the trap paragraph's "because it is a record".
- **Vale passives "is bound" and "is frozen".** Both are adjectives (a bound method, a frozen record).

## For the session

- Nothing cross-chapter. `tip prose CH=29` reported a stale `internal_names` baseline entry,
  `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`, from chapter 15's open work.
- `Examples/29_Patterns--Changing_the_Interface/adapter.py` changed through `verify-ch`'s sync (the dropped comment).
