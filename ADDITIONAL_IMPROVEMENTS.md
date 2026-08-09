Here's what I'd suggest, in the order I think pays off most. The first one I just measured rather than guessed:

1. Close the exercise/solution gaps, then gate them.
Comparing every chapter's exercise numbers against its solution headings: 15 chapters have a gap. Five have no Solutions/ file at all (21, 44, 45, 46, 47), and others are partial — 47 has one solution for eleven exercises, 19 is missing four (the ones I added), 43 missing three, 38 missing three, 15 missing three, 31 has a solution 9 for a chapter with eight exercises. Some of that drift I introduced this week; most predates it. Project memory already records this as a known ungated problem. I can write the answers, and add a tools/check_solutions.py to make gate so it can never drift silently again.

3. Audit cross-chapter claims, not just anchors. [[Is this something a tool could do?]]
heading_links.py proves a target exists; nothing proves the target says what the sentence claims. In four chapters this week I found links pointing at real sections that describe something else (33 → 37's "price-and-weight example" that is actually a recycling note; 27's "previous example" naming the wrong listing; 21's dissolution thesis cited by chapters where the mechanism didn't match). A sweep of every "see [Chapter]" sentence against its target would catch the rest.

4. Put reflow-check in the gate.
Semantic Line Breaks are enforced by a target nobody runs automatically, so hand-edited prose drifts out of compliance invisibly. Adding the check-only form to verify costs nothing and stops the drift.

5. Hunt nondeterministic #: markers. [[Is this something a tool could do?]]
CLAUDE.md warns that the self-healing gate can silently rewrite a flaky marker, and I hit exactly that with the 777/776 task-memory number this week. Running validate_output.py --update twice and diffing Chapters/ would list every marker that isn't stable, so you can decide which ones need widening.

6. An exercise-coverage pass.
Several reviews independently found exercises clustering on whichever section was most fun to write, leaving whole sections unpracticed. A per-chapter check of which sections have no exercise would turn that into a list.

If you want one: #1, because it is the only item that is both a real reader-facing defect (an answer that answers a different question is worse than no answer) and permanently fixable with a twenty-line checker.
