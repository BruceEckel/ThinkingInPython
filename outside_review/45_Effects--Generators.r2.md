<!-- outside review of Chapters/45_Effects--Generators.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `45_Effects--Generators.md` chapter:

**1. Section: All Three Channels (Misdescribed channel types)**

* **Target Text:** "The inner generator yields one question and returns one answer,
so both channels carry an `Answer`."
* **Issue:** In `ask()`, the yield channel carries a `Question`, whereas the send channel and return channel carry an `Answer`. Saying that yielding one question and returning one answer results in "both channels carry an `Answer`" confuses the yield channel with the send channel.
* **Instruction:** Rephrase to specify that the generator receives and returns an answer: "The inner generator receives one answer and returns one answer, so both the send and return channels carry an `Answer`."

**2. Section: The Driver You Already Use (Misdescribed dictionary state)**

* **Target Text:** "`to_send` holds the value each job receives on its next turn:
`None` until the runner has answered that job's most recent request."
* **Issue:** In `task_runner_send.py`, the runner computes each answer synchronously and stores it immediately via `to_send[job] = answer(request)` before requeuing the job. `to_send[job]` is `None` solely when initialized by `task()` to prime an unstarted generator, never while waiting between turns for an answer.
* **Instruction:** Clarify that `None` serves only as the initial priming sentinel: "`to_send` holds the value each job receives on its next turn: `None` initially to prime a fresh job, and the runner's answer on every turn after."

**3. Section: The Driver You Already Use (Inverted question direction)**

* **Target Text:** "Giving each job a question combines turn-taking and answering in one loop:"
* **Issue:** In `task_runner_send.py`, the jobs yield requests (e.g., `"download: headers?"`) to the runner, and the runner answers them. Stating that the runner gives each job a question reverses the direction of the interaction.
* **Instruction:** Change the phrasing to reflect that the runner answers questions posed by the jobs: "Answering each job's requests combines turn-taking and answering in one loop:"

## Verdicts

Second run, on the Flash model. Applied in commit 78579f99, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The sentence named the yield and the return channels and then said "both channels carry an `Answer`", so a reader could pair "both" with the yield channel, which carries a `Question`. It now reads "The inner generator receives one answer and returns it, so its send and return channels both carry an `Answer`."
2. Applied, with a different fix. A probe of `task_runner_send.py` that printed each value popped from `to_send` showed `None` on each job's first turn and the runner's answer on every later one, so "`None` until the runner has answered that job's most recent request" implied a recurring `None` that never occurs. The line now reads "`None` for a fresh job, then the runner's answer to that job's latest request."
3. Applied, with a different fix. In `task_runner_send.py` the jobs yield the requests and the runner answers them, so "Giving each job a question" reversed the direction. The sentence now opens "Letting each job ask a question", which keeps the parallel with "`drive()` ... answers questions" in the line above.
