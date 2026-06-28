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
