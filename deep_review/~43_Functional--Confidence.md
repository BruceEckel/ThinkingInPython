When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Deep review of chapter 43, run after the elements-of-style, literal,
positive, straighten, cohesion, and antecedents passes (one commit each on
`claude/prep-43`). Every listing was run and compared with its markers:
`parallel_pure.py` printed `True` on both runs on a 4-core Linux VM, and
`shrinking.py` shrank to `'\x80'` as the marker says. Claims about
`ProcessPoolExecutor`, pickling, the `__main__` guard, and Hypothesis's
defaults were probed on the pinned 3.15.0rc2. The prose pass ran without
the global `~/.claude/CLAUDE.md` watch list, which the cloud session does
not have. `banned_phrases.py`, Vale, and the repo's rules stood in for it.
No prior review of this chapter exists, and `deep_review_db.md` holds no
entry for it. Its "do not narrate tool-version history" rejection applied
to the Solutions file (below).

No finding needed a decision only you can make, so this file has no live
blocks.

## Applied directly

- Automatic Parallelism, the `__main__` guard: "without the guard every
  worker builds a pool of its own" was wrong. Run unguarded on 3.15, each
  worker re-runs the pool code and dies with `RuntimeError`, and the
  parent gets `BrokenProcessPool`. The sentence now says that, as
  chapter 19's `parallel_cpu.py` notes do.
- Automatic Parallelism: "Purity makes the calls safe to run together"
  opened the pickling paragraph right after "Purity makes parallel safe"
  closed the one before. The repeat is cut, and the paragraph opens on
  "Sending the calls to a worker adds requirements of its own."
- "A `functools.partial` pickles, as its wrapped function..." lost its
  stray comma, which the literal pass left behind.
- The Same Law in Hypothesis: "a *Strategy*" became "a *strategy*,
  Hypothesis's name for an input generator". Capitalized italics mark a
  design-pattern name in this book, so the old form read as the GoF
  *Strategy*. Hypothesis spells it lowercase.
- Spectrum, rung 1: the positive pass's "Most code stops here" went back
  to "Most code needs no more". The rewrite turned a sufficiency judgment
  into a claim that most code goes untested.
- Prose passes, adjusted before commit: the literal pass's "makes
  substitution wrong", "a value no type checker verifies", "and checks a
  sample", "short enough to write", and "A full proof is all of that
  work" were restored or reworded. "Short enough to write" would have
  orphaned the "Affordable Proof" heading. Its "and checks a sample" gave
  a property a verb it cannot have. The straighten pass's "the list does
  not [append]" became "the list put in its place appends nothing".
- Solutions exercise 1: the explanation of the distinct-ID count was
  wrong. It said the pool "starts a new one only when every existing
  worker is busy" and "never needs thirty-two processes, so it never
  starts them". Measured with `max_workers=32`, the pool starts one
  process per submitted task when none is idle: four for four tasks.
  Only three of them ran a task, because an early worker takes the next
  task before the last one has started. The paragraph now says that.
- Solutions exercise 7: cut "That agreement is recent", which narrated
  `ty`'s history against the standing rejection.

## The version-pinned `ty` probe (Solutions 43, exercise 7)

`uv.lock` pins `ty` 0.0.83, while the Solutions text says "`ty` 0.0.82".
The version string was left alone, since CLAUDE.md updates all the pinned
claims together on an upgrade. Probe, under the installed `ty` 0.0.83:
with both `@final` stripped from
`build/solutions/43_Functional--Confidence/describe_isinstance.py`,
`reveal_type(result.answer)` in the `Ok` branch reports `float | Unknown`.
The claim holds, so the string can move to 0.0.83 with the rest.

## Considered and declined

- "Rung" appears first in "Style contributes before the first rung", one
  paragraph before the numbered list that sets up the ladder. The
  "spectrum" sentence just above prepares it, and the section's other
  mentions all depend on it. Left alone.
- "Two parallel `withdraw()` calls could both read `balance`" describes
  threads over shared memory, while the listing that follows uses
  processes, which share nothing. The paragraph argues for purity in
  general, and the process pool comes after it, so no reader is misled.
- `parallel_pure.py` records its output in `# Sample run:` comments
  instead of `#:` markers. `run_examples.py` still runs it, but no
  validator compares its output: `faster` is a wall-clock boolean from a
  process pool, on a real `__main__`. Registering it in `timing.txt`
  with real markers is possible, but the comments look deliberate.
- Vale's `House.Weasel` warning on "obviously" in Solutions 43 sits
  inside the `insertion_sort()` docstring, in code, and "obviously
  correct" is the oracle's defining property.
