When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/18_Performance.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty` and ruff are clean on `build/examples/18_Performance`,
and every timing boolean held under repetition (5 of 5 runs for the
five `timeit` listings, 3 of 3 for the four memory thresholds; none of
them is close to its margin). The measured figures match the cited
ones on this machine: 344 against 48 bytes for frozen against slotted,
325,176 against 80,080 for list against array, bisect about 2,000
times faster than the scan, hashing about 5 times faster than bisect,
the heap about 52 times faster than repeated `min()`. Probes on the
pinned 3.15 beta confirmed the PEP 799 claims (the `profiling`
package layout, the `run`/`attach` CLI subcommands, `cProfile` as an
alias, and `profile`'s deprecation message naming 3.17 for removal)
and both `sys.monitoring` claims (double-claiming a tool id raises a
`ValueError`; `set_local_events()` does not spread to callees).
PyPy's homepage still claims "about 3 times faster" and still trails
at 3.11. `rust/fastcount/src/lib.rs` and `rust/fastcount/demo.py`
match the chapter's listings byte for byte. Two probes overturned
prose instead of confirming it: the JIT arrived in official binaries
in 3.14, not 3.13 (applied below), and NumPy now publishes 3.15
wheels, which triggers the section's own TODO condition (the live
block below).

## Applied directly

- "Try a Faster Platform": the official binaries that include the JIT
  are the 3.14-and-later Windows and macOS ones, not 3.13; the 3.14
  What's New lists "Windows and macOS binary releases now support the
  experimental just-in-time compiler" as a build change, and 3.13
  required a source build with `--enable-experimental-jit`.
- Same paragraph: "a single-digit percentage" is now "roughly 4 to 12
  percent depending on platform", PEP 836's own current numbers; and
  "Whether it stays is still an open question" is now "Whether it
  becomes a supported feature is an open question; PEP 836 lays out
  the path", matching what that PEP is (a roadmap with milestones for
  making the JIT supported, not a keep-or-drop vote).
- Same section: "two or three point releases" is now "two or three
  releases" (3.10 to 3.13 crosses feature releases; a point release
  is 3.10.1), and "the only entry on this whole ladder that requires
  no code change at all" is now "the rare speedup that needs neither
  new code nor new hardware" (a hardware upgrade needs no code change
  either, and "ladder" was never introduced).
- PyPy sentence: added the missing comma ("notably PyPy, which
  claims...").
- Profilers: the table intro now names its source ("this one profiles
  a small script, `prof_demo.py`"), so the table's filename no longer
  appears unexplained beside the `my_program.py` command. The
  alternative was renaming the command's file to match; the generic
  name reads better in the command line.
- Cut the section-closing sentence "If you can narrow the problem
  down to a particular function, there may be techniques that speed
  up the algorithm used in that function": vague, and the next
  section's opening ("A profiler answers a broad question...") is the
  real transition.
- `monitoring.DISABLE` prose: dropped the self-contradicting
  "permanently" from "stop reporting this event at this location,
  permanently, until someone calls `restart_events()`".
- Dropped "already" from "when you already know which function you
  care about".
- `membership.py` prose: "about 22,000 times faster" is now "about
  14,000 times faster", matching the `--numbers` transcript the
  chapter prints one page later for the same listing (ratio
  13,935.56; this machine measured about 12,000). The old number
  contradicted the chapter's own sample run. The alternative was
  cutting the sentence and letting the transcript carry the number.
- Lazy pipeline: "built two million-element lists" is now "built a
  million-element list and a half-million-element list" (`evens`
  holds 500,000 elements, and the old phrasing also misread as two
  lists of a million each).
- Cut "is what" from "`islice()` is what replaces the eager version's
  `evens[:5]`".
- Merged the duplicated NumPy-needs-an-array sentences into one, and
  merged the cliff-into-stream advice ("The cliff is the argument for
  laziness: if a data set can outgrow memory, stream it from the
  start"), dropping "ever".
- Caching: cut the first of two nearly identical `cached_property`
  recommendations; the method-trap paragraph keeps the second, which
  now carries the Classes-chapter link the first one had.
- Memory view: "the view never did" is now "the view copies nothing".
- NumPy parenthetical: "the book's Python 3.15 target has no NumPy
  release yet" is no longer true, so it now reads "a third-party
  dependency the book's build does not yet include"; the TODO comment
  records the verified wheel state and points here.
- Numba prose: "Thus the comparison measures steady-state speed"
  merged into the prior sentence with "so".
- Rust boundary paragraph: "Shipping millions of small Python
  objects" is now "Passing..."; "The list of integers ... crosses
  50,000 times" is now "The list ... carries 50,000 integers across
  the boundary each way" (the list crosses once; the integers are
  what convert), with "follow each crossing" becoming "follow each
  integer"; and the comma-spliced closer is now "The question is not
  the object count on its own but the work done per object crossed".
- Ran `make reflow CH=18` over the edited prose.

## NumPy now installs on the pinned 3.15: convert the section to a tested listing?

The NumPy section's TODO condition has arrived. numpy 2.5.2 publishes
cp315 wheels for every platform including `win_amd64`, it installs
cleanly on the pinned 3.15.0b4 (verified in a scratch venv,
2026-08-11), and the chapter's snippet runs there as written,
measuring a 10.7x speedup against the sample run's 12.9x. Converting
the indented block to a real, fenced, tested example is now blocked
on one decision rather than on PyPI: adding `numpy` to
`pyproject.toml` as a dev dependency, which touches `uv.lock` and
makes the whole book's build depend on it. That is a repo-wide call,
and the sweep instructions said NumPy mentions stay illustrative, so
this review did not make it.

If you want the conversion: add the dependency, fence the block with
a `# vectorize_numpy.py` header, replace the printed ratio with a
threshold boolean in the house style (`NumPy at least 3x faster`
would sit far from the 10-13x measurements), and give the sample
numbers to `report()` under `--numbers` like the chapter's other
measured listings. The Numba and NumPy+Numba sections stay indented
either way (numba 0.66.0 tops out at cp314), as does the Rust demo's
TODO, which needs both. Project memory
(`numpy-numba-blocked-on-py315`) also goes stale the moment this
lands in either direction: NumPy is no longer blocked, only Numba is.

[] Reject

## Considered and declined

- Converting the Numba or NumPy+Numba sections: still impossible;
  numba 0.66.0 publishes no cp315 wheel (cp314 is its ceiling), so
  those parentheticals remain accurate as written.
- Tightening any timing-threshold boolean: every one held with wide
  margin over repeated runs, and the loose margins are deliberate
  (the hoist listing's prose explains its own).
- "The counts, not a stopwatch, are what this listing measures"
  keeps its cleft: deleting "are what" breaks the sentence rather
  than tightening it.
- The `#:` markers for `heapify()` output depend on CPython's heap
  layout algorithm, not on timing, and are deterministic; no
  hardening needed.
