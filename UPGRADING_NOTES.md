Upgrading to newer version: I think the solution might to put some kind of marker at the end
  of the filename slugline. Perhaps something like '# interesting_feature.py {3.15}'. Then the build system could
  isolate files that couldn't be run with the 3.14 interpreter.
  I envision only using no marker vs. "{3.15}", however if it seemed valuable, every example could have a marker
  indicating the earliest version of the language that would run that example. I'm not sure how much of a benefit that
  would be.

I'd lean toward "optional marker that, when present, names the minimum version" rather than a hard-coded {3.15} flag. They cost about the same to parse, but they age differently:

- With a binary {3.15} meaning "needs the new thing," the marker goes stale the day 3.15 becomes the baseline. Then every {3.15} is either wrong or needs a sweep to remove.
- With {3.15} meaning "minimum 3.15," the build compares the marker against whatever the current baseline is. When you bump the baseline to 3.15, those examples just quietly become runnable, no renaming. When 3.16 ships something fun, you write {3.16} and nothing else changes.

Crucially this does not mean marking every example. Your "no marker = baseline" rule stays exactly as you pictured it. The only difference is that the rare marker carries a real version number instead of a boolean. So you get the future-proofing for free and never have to answer "what's the min version of this trivial example" for the 95% that don't need a marker.

I'd skip the "tag every example with its earliest version" idea. It's a lot of per-example research and verification for a fact readers rarely need, and it would rot (a later edit can lower or raise the true minimum without anyone noticing). The sparse-marker approach gives you the one thing that matters (don't run 3.15 code on 3.14) without that burden.

Touchpoints it implies (just naming them, not proposing to build anything)
- The extractor strips {3.15} so the written file is still immutability.py, and records the constraint somewhere the runner can see it. The natural fit is the existing inline-marker family: translate {3.15} into something like the current # extract: no-run convention so run_examples.py reads it the same way it already reads skips.
- The runner gains a third skip category, distinct from no-run (GUI/interactive) and the failure baseline: "skipped, needs 3.15." Reporting it separately keeps the gate honest, green on 3.14 without hiding the example.
- Output validation (#: markers) has to respect the same gate, since you can't verify 3.15 output on a 3.14 interpreter.
- Bonus you might actually want: the same marker is a clean source for a small "3.15+" badge on the rendered listing. Readers benefit from seeing at a glance that a snippet needs a newer Python, and it's basically free once the build is already parsing the marker.

The one real fork is execution, not syntax: when a marked example exists, do you (a) just skip it on the 3.14 gate and verify 3.15 code by hand for now, or (b) have CI install a 3.15 interpreter (uv makes that easy) and actually run the marked ones under it? Given 3.15 is still beta, (a) now and (b) once it stabilizes seems like the low-risk path, and the marker format is identical either way, so choosing later costs nothing.

Yes, {3.15} meaning "at least version 3.15" is what makes sense.
  Upon reflection I realize that the marker should be scoped:
  - On the slugline means "the whole file"
  - It would be nice to be able to mark parts of an example for version isolation.
    If it appears as a comment at the end of an import, only that import is isolated.
    To isolate code portions, could we somehow use a context manager? Such as:
    with 3_15:
         ...


  Agreed on {3.15} = "at least 3.15." On scoping, let me separate two things that feel similar but behave very differently: execution gating and presentation. The slugline marker can do both. Sub-file markers can really only do presentation, and that's the crux of the context-manager idea.

  Why sub-file execution isolation can't work the way the with block implies

  One extracted file is one process: one interpreter, one parse, one run. You can't run part of a file on 3.14 and part on 3.15. So nothing inside the file can carve out a region that "runs on a different version." Worse, if the isolated feature is new syntax (not just a new builtin like frozendict), the 3.14 interpreter fails at parse time, before any runtime construct executes. A with block guards runtime, which is already too late.

  And the specific with 3_15: form has problems even as syntax:
  - 3_15 isn't an identifier (can't start with a digit); it actually parses as the integer 315. You'd need with v3_15: or with since(3, 15):.
  - A context manager can't skip its own body. __enter__ runs, then the body runs regardless. To "skip" the body you need trace-hook hacks (the trick pytest uses), which is fragile magic to put in a teaching book.
  - A real with needs an actual object imported into every example, adding runtime noise to code whose whole point is clarity.

  So the runtime-construct path is a dead end. The good news: you don't need it.

  The reframing: markers are build directives, and they compose

  Make every marker a comment the build reads, never executable Python. Then define one composition rule:


  Make every marker a comment the build reads, never executable Python. Then define one composition rule:

  ▎ A file's effective run-requirement = the max of its slugline marker (if any) and every inline marker in it.

  That single rule makes the scopes you want fall out naturally:

  - Whole file — slugline # immutability.py {3.15}. Use when the file is conceptually a 3.15 piece.
  - One line / one import — trailing comment: import something  # {3.15}. This badges that line in the rendered listing and bumps the file's run-requirement to 3.15. That resolves your "why mark just the import?" question: marking the import does both jobs, so you usually don't also need the slugline.
  - A block — a comment fence instead of a with:
  # {3.15} ─┐
  config = frozendict(debug=False, level=3)
  print(config["level"])
  # ────────┘
  - Same semantics: badges the block, contributes to the file gate. It gives you the visual scoping you liked about with, without pretending to be runtime code or breaking the 3.14 parser.

  Net effect: execution gating is always whole-file (derived), and the inline markers add precise presentation (a subtle "3.15+" badge or highlight on exactly the line/block that's new). That's genuinely useful to a reader, and it's the part the with block was really reaching for: "look here, this bit is the new thing."

  The one case that needs a real decision

  If you ever want a mostly-3.14 example where only a small region is 3.15, and you want the 3.14 gate to still run the rest, the only honest way is to split: the build emits a 3.14 artifact with the region removed (or replaced by the MappingProxyType equivalent) and a separate 3.15 artifact with it. That's powerful but adds real complexity, and it changes what the reader sees versus what runs. I'd avoid it unless a concrete example demands it; the derived-whole-file rule covers the common case without it.

  So my suggested model in one sentence: one marker syntax {3.15} everywhere, always a comment; slugline scopes the file, inline scopes the badge; the runnable requirement is the max.and/or save it as a project memory? I won't implement anything.

   I see your points. Are you suggesting that we use special characters to produce the fence lines here:
    # {3.15} ─┐
    config = frozendict(debug=False, level=3)
    print(config["level"])
    # ────────┘
    Or are those underscores and pipes, or did you put that in to make a point?
    I'd like easier-to-type syntax, perhaps even:
    # {3.15}
    ...
    # -{3.15}
    Consider things that might work for this. Also I'm not wedded to '{' and '}' so if there are better choices for those I'd like to see them.

---

## Agreed design: minimum-version markers for examples

This is the settled design from the brainstorm above. Nothing is built yet.

### The token

A version marker is `[3.15+]`, written inside a comment. It means "this needs
Python 3.15 or later." The trailing `+` carries the "at least" meaning at the
point of use, so a reader understands it without knowing the convention.

- Square brackets, not braces: in Python source `{}` already reads as a set or
  dict literal, while `[3.15+]` reads as a label, like `[TODO]` or `[NOTE]`.
- The token always holds a real version number, never a boolean. It means
  "minimum 3.15," so it does not go stale when the baseline moves. When the
  baseline becomes 3.15, marked files quietly become runnable with no edit. When
  3.16 ships something, you write `[3.16+]`.
- No marker means "runs on the current baseline." The vast majority of examples
  carry no marker. Do not tag every example with its earliest version: that is
  per-example research readers rarely need, and it rots silently when an edit
  raises or lowers the true minimum.

### The three scopes

```python
# immutability.py [3.15+]          <- whole file (on the slugline)

from x import thing  # [3.15+]      <- one line / one import

# [3.15+]                           <- block open
config = frozendict(debug=False, level=3)
print(config["level"])
# [/3.15+]                          <- block close
```

The block close uses a leading slash, the universal "close" signal from HTML and
Markdown. Repeating the version on the close lets the build validate pairing and
catch a missing or mismatched fence. A bare `# [/]` close is an allowed
shorthand. No non-ASCII fence characters: earlier drafts used box-drawing
characters (─ ┐ ┘) purely for decoration, and those are dropped.

### The composition rule

> A file's effective run-requirement is the max of its slugline marker (if any)
> and every inline marker in it.

This separates the two jobs cleanly:

- Execution gating is always whole-file. One extracted file is one process: one
  interpreter, one parse, one run. You cannot run part of a file on 3.14 and
  part on 3.15. So the only thing that decides whether a file runs is its derived
  whole-file requirement.
- Presentation is per-marker. An inline marker badges exactly the line or block
  that is new (a small "3.15+" tag in the rendered listing) and also contributes
  to the whole-file gate. Marking an import therefore does both jobs, so you
  usually do not also need the slugline marker.

Because gating is whole-file, runtime constructs cannot scope a version. A
context manager such as `with v3_15:` is a dead end: it guards runtime, but new
*syntax* fails at parse time first, and a context manager cannot skip its own
body without trace-hook hacks. Markers stay comments, read by the build, never
executable Python.

### Build touchpoints (when this gets implemented)

- The extractor strips the marker so the written file keeps its plain name
  (`immutability.py`), and records the constraint where the runner sees it. The
  natural fit is the existing inline-marker family: translate `[3.15+]` into
  something `run_examples.py` reads the way it already reads `# extract: no-run`.
- The runner gains a third skip category, distinct from `no-run` (GUI or
  interactive) and the failure baseline: "skipped, needs 3.15." Report it
  separately so the gate stays honest, green on 3.14 without hiding the example.
- Output validation (`#:` markers) must respect the same gate, since 3.15 output
  cannot be verified on a 3.14 interpreter.
- Bonus: the same marker is a clean source for the "3.15+" listing badge in the
  site build.

### The one deferred case

A mostly-3.14 example with only a small 3.15 region, where the 3.14 gate should
still run the rest, would require *splitting*: the build emits a 3.14 artifact
with the region removed or replaced (for example by the `MappingProxyType`
equivalent) and a separate 3.15 artifact with it. This is powerful but complex,
and it makes what runs differ from what the reader sees. Avoid it until a
concrete example demands it. The derived-whole-file rule covers the common case.

### Execution strategy (decide later, format is identical either way)

- Now, while 3.15 is in beta: skip marked examples on the 3.14 gate and verify
  3.15 code by hand.
- Once 3.15 stabilizes: have CI install a 3.15 interpreter (uv makes this easy)
  and actually run the marked examples under it.
