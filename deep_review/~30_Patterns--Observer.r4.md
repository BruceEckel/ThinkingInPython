> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 30_Patterns--Observer (2026-10-13)

This run read the chapter and its Solutions file against the deep-review passes,
`deep_review_db.md`, the r3 review (2026-10-09), and both outside-review verdict files.
The chapter's editing pass is closed, so the edits from that pass that r3 left alone are judged here by the style rules.
Tools: `ty` 0.0.86 and Python 3.15.0 under `uv run`.
Four `ty` probes confirmed the claims they test.
A pull `Display` whose `subject` is a `Thermometer` draws `invalid-argument-type` at `attach()`.
`station.celcius = 25.0` passes on `WeatherStation` and draws `unresolved-attribute` on `thermometer.py`'s `Thermometer`.
`fields(cls)` inside `__init_subclass__()` draws `invalid-argument-type`.
A synchronous function passed to `AsyncBroadcaster.connect()` draws `invalid-argument-type`.
`async_thermometer_demo.py` and `gather_orphan.py` matched their markers on three direct runs each.
`tip verify-ch CH=30 ISOLATED=1` passed 27 of 27 before and after the edits.
There are no live blocks.

## Applied directly

Chapter, teaching:

- "Push or Pull": the paragraph said the pull observer must declare `subject` as a `Thermometer`, then jumped to "add an `isinstance()` check or a second type parameter" without saying why the narrower declaration fails. It now says the narrower `update()` no longer matches `Observer[float]`, so the type checker rejects `t.attach(Display())` (probed). Exercise 2 states the same fact, so the chapter now sets up the exercise.
- "The Pythonic Observer": "`Broadcaster.announce()` calls `responder(data)`, so a function serves as a responder" now names the contrast with `Subject.notify()`'s `observer.update(self, arg)`: a responder is any callable, not an object with an `update()` method.
- "Lapsed Listeners": weak references "do not keep the responder alive" was wrong for `weak_responder.py`, where the broadcaster holds `weak` strongly and only the `Plot` is weak. Now "let Python collect the object a responder calls".
- "Setting the Responders at Construction": "The broadcaster holds strong references to its responders" stated a fact with no consequence; it now says each responder stays alive as long as the broadcaster does. "The tuple freezes its contents" became "a tuple can neither gain nor lose items" (a tuple holds its contents; the style guide's own example).
- "Thermometer" composition paragraph: "An object can hold multiple attributes, so it can publish more than one kind of change" now says several `Broadcaster` attributes, which the reasoning needs.

Chapter, paragraph splits (one concept per paragraph):

- "Push or Pull" at "Each observer depends on the subject's interface" (push/pull contrast, then pull's typing consequence).
- "Why `notify()` Copies the List" at "With the copy" (the failure, then what the copy guarantees).
- "Easier Names" at "GoF's method names are a second obstacle".
- "The Pythonic Observer" at "`announce()` passes the data alone" (renaming, then push and the one-argument payload), and at "Notification runs one way" (the `None` alias, then why return values have no consumer).
- "Lapsed Listeners" at "Long-lived broadcasters need" (the problem, then the remedy that introduces the listing).

Chapter, prose:

- "*Chain of Responsibility* is the pattern for a design that needs an answer" repeated the sentence before it; now one sentence joined by a colon.
- "*GoF Design Patterns* supplies the premise under broadcast communication" is "states the premise of".
- "changes how the broadcaster is written" is "changes how you write the broadcaster".
- "connects the same way as all responders" is "the same way the other two do".
- "If a responder raises an exception, it stops the loop": "it" could be the responder; now "the exception stops".
- "Using `WeakMethod`, you store the instance and the function": `WeakMethod` does the storing; now its subject.
- "Three earlier sections handle a consequence" is "each handle".
- "This issue is revisited in [Deciding What Matters]" is "[Deciding What Matters] returns to this issue".
- "appends its function to the `thermometer` list" is "to `thermometer`'s list of responders".
- "reject a plain function" is "reject a synchronous function" (the contrast is sync against async).
- "Even though `alarm` is connected before" is "Although `alarm` connects before" (watch word `even`, passive).
- "It only manipulates `Grid`s; they are displayed independently by `grid_view.py`" is "It manipulates `Grid` values, and `grid_view.py` displays them separately".
- "the controller's job is contained within the view" is "the view also does the controller's job".
- "the views and the controller never directly interact; they communicate through a model" is "communicate through the models"; the exclusion is already the sentence two lines later ("No view holds a reference to the controller").
- "The meaning of the keys is only defined in the controller" is "The controller alone defines what the keys mean".
- "The same flexibility is created in the other direction" is "works in the other direction".
- "Testing benefits from this design decoupling" is "The decoupling also simplifies testing".
- "both the Controller and the View" lowercased: they are roles, not class names, here.
- "The notification code can be separated from the measuring code in different ways" is "Three designs in this chapter separate the notification code from the measuring code" (the list has three bullets).
- "a question of *how much*" / "*which kind*": italics for emphasis, against the italics rule. Now "when responders filter by how much a value changed" / "by which kind of change arrived".
- Exercise 11: "what it costs that `Broadcaster` does not" (commerce figure, R2) is "which new problems it brings that `Broadcaster` avoids". The Solutions quote regenerated.

Solutions:

- Exercise 2: "The `assert` is the cost", "The cost is at the other end", and "That is pull's bargain ... each observer pays by knowing what it is watching" (R2 commerce figures) now state the consequence: the `assert` runs on every notification; "The restriction moves to the other end"; "Under pull, the subject decides nothing about what its observers read, so each observer must know what it is watching."
- Exercise 6: "`_flood()` is a plain graph search (depth-first, using a stack)" is "a depth-first graph search, using a stack" (filler "plain").
- Exercise 11: "costs three things", "The first of those costs", "the shared-registry cost in tests", "The import cost" now say problems, matching the reworded exercise.

## Considered and declined

- "which is the behavior you want when a responder counts readings" (`tip watch-words` T3 `want`): a human subject, the case the 2026-10-03 sweep accepted elsewhere.
- Solutions "and never computes one" (exercise 9) and "the part a validating descriptor never needs" (exercise 10): each `never` is the claim.
- "A responder's choice is limited to what it reads" (vale passive): the limit is the claim, and every positive rewrite tried needed "and nothing more".
- "Using decorators, we can simplify and automate the attachment of responders": Bruce's "we", left as written.
- The remaining vale passives ("is keyed by coordinate", "are dropped", "is defined inside `show()`", "is discarded without a report", and the rest) read naturally with no better actor.

## For the session

- `tip watch-words` and `tip positional` still list chapter 30 as NEW by design. After this run the NEW set is the three items under "Considered and declined"; all three are keeps, so the session can accept them when chapter 30 joins the baselines.
- Nothing found in other chapters.
