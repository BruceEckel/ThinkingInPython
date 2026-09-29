> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: Generators (chapter 45)

This review ran after the six `make rewrite` prose passes (elements-of-style,
literal, positive, straighten, cohesion, antecedents), each committed on its
own. It checked every factual claim against the listings, the chapters the
prose links to, the pinned interpreter, and `ty`. It also checked every claim
in `Solutions/45_Effects--Generators.md`. The prose pass used the skill's
rules, `banned_phrases.py`, and the repo's CLAUDE.md. The global
`~/.claude/CLAUDE.md` watch list is not available in a cloud session, so the
pass ran without it. Every finding had one sensible answer, so none is left
for a decision. The file holds only the record below.

## Applied directly

- **Opening, "The next chapter builds an Effect system":** now a named link,
  `[Stateless](46_Effects--Stateless.md)`. The chapter was split out of 46,
  and a named link fails loudly at `heading_links.py` if the chapters move
  again.
- **"The Driver You Already Use", first line:** same change, for the same
  reason. The closing "the next chapter puts into the type system" stays
  relative. It is correct, and a third link to the same chapter would crowd
  the page.
- **Relative-reference audit (split trap):** every "previous/next chapter",
  "previous section", and "last chapter" in the chapter and its Solutions file
  was checked. The two "next chapter" phrases pointed at 46, correctly. The
  antecedents pass had already replaced "the previous listing/example" with
  listing names. Solutions 45 has none.
- **`drive()` paragraphs:** swapped the `try` paragraph and the "verifies two
  of those three parameters" paragraph. The cohesion pass had split a
  paragraph, which left "those three parameters" one paragraph away from the
  sentence that lists them.
- **The Return Channel, "only a generator supplies a return value":** this
  was false. A hand-written iterator whose `__next__` raises
  `StopIteration(5)` makes `v = yield from It()` bind `5` (checked on the
  pinned 3.15). The rewrite says the expression takes its value from the
  `StopIteration` that ends the iteration, a generator's `return` sets that
  value, and a list's iterator never does.
- **All Three Channels, "so `name` and `town` read like ordinary
  assignments":** now "`interview()`'s three assignments". `friend` is the
  third.
- **`throw()` and `close()` section, new listing `throw_through.py`:** the
  heading and the opening paragraph say `throw()` and `close()` reach the
  innermost generator through `yield from`. The only listing,
  `throw_and_close.py`, has no `yield from`, so the chapter asserted that
  mechanism but never showed it. The new listing splits the work across
  `inner()` and a delegating `outer()`. Its trace shows `inner()` catching
  the thrown `ValueError` and the cleanup lines printing from the inside out.
  It sits between the `throw_and_close.py` explanation and the
  `GeneratorExit` gotcha, and it is synced to `Examples/`.
- **Closing section, the Concurrency link:** "presents `await` ... and does
  not describe the mechanism" was too strong. Chapter 19's
  `{#asyncio-mechanics}` section describes suspension, wake-up conditions,
  and resumption. It now says chapter 19 describes `await` as suspending a
  task until the loop resumes it, without showing the protocol underneath.
- **Closing section, how asyncio resumes a coroutine:** "the loop ... resumes
  the coroutine by sending it back" does not match asyncio. A `Task` resumes
  its coroutine with `send(None)`. The awaited `Future`'s `__await__` then
  returns `future.result()` as the value of the `await`. The rewrite says
  `await` yields a `Future` to the task that drives it, and that the `await`
  expression evaluates to the result. `Future` is already introduced in
  chapter 19.
- **Solutions 45, exercise 3:** "no collector is left to prompt" became "no
  collector remains to prompt". This clears the file's one Vale passive
  warning.

## Verified and left as written

- The nine-errors-in-three-groups claim for `Generator[Answer, Question,
  Result]` (the straighten pass reran `ty` on a copy).
- The `TypeError` text for a non-`None` first `send()`, and
  `threading.synchronized_iterator` existing on the pinned 3.15.
- The anchors this chapter links: 23 `#generators`, 44
  `#effect-management-for-python` (its `coroutines_are_descriptions.py` is
  the "calling runs nothing" demo) and `#effect-management-systems`, 14
  `#decorating-classes` (`register.py`, the registering decorator), 19
  `#sharing-an-iterator-between-threads`, and 31 `#a-vending-machine` (an
  `Enum` state, a transition table, `Quit` from every state, as Solutions
  exercise 7 says).
- "Earlier examples annotate every generator with the short `Iterator`
  form." No chapter before 45 has a `-> Generator` annotation.
- Solutions 45: exercise 4's "without the annotation, the type checker says
  nothing" (`profile = interview()` draws no diagnostic). Exercise 5's claim
  that `ty` rejects `return size` under `Iterator[str]` (`invalid-return-type`,
  expected `None`, found `int`). Exercise 6's quoted `send()` signature
  (typeshed: `def send(self, value: _SendT_contra, /) -> _YieldT_co`). No
  quoted diagnostic's text was touched.

## Considered and declined

- **`interview_generator.py` has three comment placements** (two above the
  line, one trailing). They look like the output of the comment-width fixer,
  not a choice, and the gates pass. Unifying them would change a listing for
  no reader benefit.
- **No exercise covers `throw()`/`close()`.** The section is secondary to the
  chapter's claim. The seven exercises cover the annotation, drivers, the
  three `yield from` channels, and the generator-as-state-machine contrast,
  which is the chapter's arc.
