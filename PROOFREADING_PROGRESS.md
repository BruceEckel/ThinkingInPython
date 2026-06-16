# Proofreading Progress

Checkpoint for the prose proofreading pass. On restart, read this first, find
the first unchecked chapter, and continue from there. Update the checkboxes and
the "Last updated" line before ending each iteration.

Last updated: iteration 5 done (chapters 13-15), committed on branch
`proofread/prose-pass`.
Next action: proofread chapters 16-18.

## Policy

- Work 2-3 chapters per iteration.
- AUTO-FIX (in both Markdown and, if a code block changes, the matching
  Examples/ file): spelling, doubled words, `it's`/`its` and similar, spacing,
  and the global style rules: no em-dashes (`--` or the character), break
  run-ons into short sentences, italics only to introduce a new term.
- DO NOT silently rewrite voice. For confusing sentences or awkward phrasing,
  append an entry to `PROOFREADING_FINDINGS.md` (chapter, original, proposed
  rewrite) for the user to approve later. Do not change the prose.
- Only touch prose. Do not change code blocks except to fix a comment typo;
  if a code block changes, sync the matching `Examples/` file.
- After each iteration: run `uv run python tools/extract_examples.py` (drift
  must stay in sync), update this file, then commit. Stage explicitly
  (`git add Markdown PROOFREADING_PROGRESS.md PROOFREADING_FINDINGS.md` plus any
  touched `Examples/` paths). Do NOT `git add -A` (an unrelated `_TODO.md` edit
  is in the tree and must not be committed).

## Chapters

- [x] 01 Introduction
- [x] 02 A Python Tour
- [x] 03 Containers and Control Flow
- [x] 04 Functions
- [x] 05 Modules and Packages
- [x] 06 Classes
- [x] 07 Initialization and Cleanup
- [x] 08 Static Type Checking
- [x] 09 Testing
- [x] 10 Data Classes as Types
- [x] 11 Functional Error Handling
- [x] 12 Decorators
- [x] 13 Comprehensions
- [x] 14 Metaprogramming
- [x] 15 Rethinking Objects
- [ ] 16 The Pattern Concept
- [ ] 17 Messenger
- [ ] 18 Singleton
- [ ] 19 Application Frameworks
- [ ] 20 Fronting for an Implementation
- [ ] 21 State Machines
- [ ] 22 Iterators
- [ ] 23 Factory
- [ ] 24 Function Objects
- [ ] 25 Changing the Interface
- [ ] 26 Observer
- [ ] 27 Multiple Dispatching
- [ ] 28 Visitor
- [ ] 29 Pattern Refactoring
- [ ] 30 Simulation

When all are checked, stop the loop (no further ScheduleWakeup). The user
reviews PROOFREADING_FINDINGS.md and decides which rewrites to apply.
