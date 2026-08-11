[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/46_Stateless.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
`ty` (0.0.70) shows only the three intended `reveal_type` infos, ruff is
clean, all 10 tests pass, and all 30 runnable scripts run. Every quoted
`ty` diagnostic was re-generated on 0.0.70 and matches the chapter
verbatim, including positions: the two `reveal_bound.py` renderings
(`def greet(...)` by name, `bound` by signature), the `unsupplied.py`
invalid-argument-type text (`Expected Generator[Async | Exception, Any,
Unknown], found Generator[Need[Console], Any, None]`), the
`undeclared_need.py` invalid-yield at 7:20, the `protocol_supply.py`
rejection at 5:5, the `scores.py` reveal, and the hypothetical
`value + 1` unsupported-operator with `Literal[1]` against
`int | KeyError`. The prose claims that describe checker behavior without
a quoted block were also probed: dropping `KeyError` from `announce()`'s
annotation points at `yield from score(name)`; dropping `| Need[Log]`
from `greet_all()` draws invalid-yield at `yield from greet_logged(name)`;
`supply(Log())(greet_all)` reveals as `(list[str]) ->
Generator[Need[Console], Any, None]` and wrapping it in
`supply(Console())` leaves `Never`; `chosen` in `default_console.py` is
already `Success[None]`; and `Depend[Console, None]` is rejected at the
annotation (`Console` not assignable to the `Ability[Any]` bound). Every
library claim was verified against the stateless 0.6.1 source: `run()`'s
body is `return asyncio.run(run_async(effect))` with parameter
`Effect[Async, Exception, R]`; `Need` is a frozen dataclass whose `t`
field holds the class; `need()` returns `Depend[Need[T], T]`;
`supply()` scans its arguments in order with
`isinstance(instance, ability.t)`; `as_type` is
`(t: Type[R]) -> Callable[[R], R]`; `handle()` contains
`t = get_origin(t) or t` (exercise 6's evidence); `SuccessEffect.send()`
raises `StopIteration(value)`; the builtin `Console` implements `print()`
and `input()` with `print_line()`/`read_line()` accessors; `read_file()`
carries `@throws(FileNotFoundError, PermissionError)`; the quoted
`sleep()` body matches `stateless/time.py`; and `retry()`/`repeat()`
take a schedule and return a function-to-function decorator, as "An
Effect Runs Once" says. The `real_clock.py` timing boolean
(`elapsed >= 0.03` from three 0.01s sleeps) has a safe margin on Windows
timers. The 11 exercises match `Solutions/46_Stateless.md` in number and
content, and the inbound anchors from 39 and 47 (`#dependency-injection`,
`#waiting-on-a-coroutine`, `#nothing-runs-yet`, `#an-effect-runs-once`,
`#swapping-the-implementation`, `#supplying-an-interface`,
`#the-error-channel`, `#the-effect-type`, `#forgetting-to-supply`,
`#when-two-implementations-match`, `#retrofitting-an-effect`,
`#emptying-the-channels`) all point at headings this review did not
touch. One finding needs a decision; it is the block below.

**ty 0.0.70 now sees through the PEP 695 `type` alias, so the alias-trap
paragraph in "Retrofitting an Effect" is stale.** The probe from project
memory (`type Greeting = Depend[...]` as a generator's return annotation,
with an undeclared `Need[Log]` yield in the body) was re-run on the
pinned ty 0.0.70: all three annotation forms now report `invalid-yield`
at the offending line, the `type` statement included. The check the
paragraph says is off is on. The paragraph currently reads "Under `ty`
(0.0.65 at this writing), a `type` alias as a generator's return
annotation turns the yield check off, and everything this section
demonstrated silently escapes verification." That claim is false on the
pinned toolchain. I applied nothing because the decision ripples across
two chapters and three support files. Chapter 47 says "The five-way union
appears in full rather than as an alias, for the reason given in
[Retrofitting an Effect]" (~line 1363) and its conclusion counts "three
of these checker gaps" with the alias as the third (~line 1981); both
become wrong if this paragraph declares the gap closed. `CLAUDE.md`'s
trap entry, `thinking-in-python-skill.md`'s general statement, and
project memory `stateless-partial-handling-ty-support` carry the same
warning. My recommendation: keep the spelled-out signatures (the written
union is the information the section teaches, and an inference a checker
gained in one upgrade can vanish in another), but rewrite the paragraph
as history plus a verify-first rule, roughly:

> The repeated union invites a `type` alias,
> and the book's own habits normally endorse one.
> Through `ty` 0.0.65,
> a `type` alias as a generator's return annotation turned the yield
> check off,
> and everything this section demonstrated silently escaped
> verification;
> 0.0.70 sees through the alias and reports the same `invalid-yield`.
> These chapters keep writing Effect signatures out in full:
> the union is the information,
> and a checker that loses an inference in an upgrade loses it quietly.
> Before aliasing an Effect signature,
> prove that your checker flags an undeclared Ability through the alias.

Chapter 47's two passages then need the matching edit (its "three
checker gaps" becomes two live gaps plus one the checker has since
closed, or the count drops to two), which is that chapter's review to
coordinate. If you would rather keep the paragraph as a live warning
unchanged, the minimum honest edit is updating "(0.0.65 at this
writing)" to a version the claim is true for, which no current pin
satisfies.

[X] Reject [[Just modernize everything. I don't want a history of "what didn't used to work"]]

(Applied per the instruction above, 2026-08-11, same session: the
Retrofitting paragraph now states 0.0.70 behavior with no version
history and keeps the write-it-out recommendation; ch47's two passages,
CLAUDE.md's trap entry, both `thinking-in-python` skill copies, and the
`stateless-partial-handling-ty-support` memory were modernized to
match. Nothing further to apply from this block.)

## Applied directly

- "The Simplest Effect": "In a synchronous program that happens once, at
  the outermost edge" is now "A synchronous program calls it once, at
  the outermost edge", fixing the doubled "happens" against the previous
  sentence; the deliberate echo of "Where to Call `run()`"'s closing
  advice is kept.
- "Effects Propagate": "and in a `for` comprehension it is the `<-`
  binding, where Python's is `yield from`" now joins with a semicolon
  ("binding; Python's is `yield from`"), removing the odd "where"
  conjunction.
- "Builtin Dependencies": dropped "at all" from "You might not need to
  define one at all", and "three classes of its own to depend on" is now
  "three dependency classes of its own" (clause-final stranded
  preposition).
- Same section: "check what the library already declares first" is now
  "first check what the library declares" ("already" plus a trailing
  "first" fighting over the same sentence).
- "Supplying an Interface", teaching addition: after "the Protocol needs
  `@runtime_checkable`", added "Without it, the first request raises a
  `TypeError`, because `isinstance()` refuses a protocol that is not
  runtime-checkable." Probe-verified: omitting the decorator dies inside
  `supply()`'s handler with `TypeError: Instance and class checks can
  only be used with @runtime_checkable protocols`. The near-miss a
  reader writing their own Protocol Ability would hit first.
- "Dependency Injection": "Stateless checks happen before the program
  runs" is now "Stateless checks come before the program runs" ("happen"
  watch word).
- Same section: "describes failing in exactly this way" is now
  "describes failing this way" ("exactly" as intensifier).
- "A Default Binding": dropped "ever" from "before `fallback` ever sees
  a request", and "a genuine default, null logger or no-op console" is
  now "a null logger or a no-op console" (articles mark the apposition,
  so it no longer scans as a three-item list).
- "Declaring Is Not Handling": dropped "ever" from "before the driver
  ever sees it".

## Considered and declined

- **"A dictionary matches that key exactly" keeps its "exactly".** The
  word carries the real contrast the DI section is drawing: dict-key
  lookup against `supply()`'s `isinstance()` scan, where a subclass
  registration is invisible. A precise logical match, the case the style
  rule allows.
- **"a driver encountering one can do nothing but stop" stays.** The
  modal "can do nothing but X" means there is no alternative; it is the
  style guide's own keeper example.
- **`catch()`, `throws()` named in "An Effect Runs Once" before the
  error channel is taught.** They appear only as examples of the
  functions-not-Effects API shape, beside the known `supply()`. Forward
  links there would clutter a paragraph about design, and both get full
  sections later in the same chapter.
- **The `Unknown` in quoted ty messages goes unglossed.** ty's `Unknown`
  is part of its diagnostic vocabulary from chapter 8 (Static Typing)
  onward; re-explaining it here would interrupt the
  unsupplied-dependency point.
- **Solution 3's heading "Catching an error that is already handled" is
  loose.** The `ValueError` that `catch(ValueError)` moves was declared,
  not yet handled; the solution body states this precisely. A Solutions
  heading rename is not worth the churn.
