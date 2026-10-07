> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 30_Patterns--Observer (2026-10-07)

This run found nothing that needs your decision, so the file has no live blocks.
The chapter is in an open editing pass (`edit-start-30`), so the review read the working tree.
Two Opus `verify-claims` agents checked the chapter (about 160 claims) and its Solutions file (74 claims)
against the listings, every linked anchor, the GoF text, the story figure's generator, and live `ty` and runtime probes;
all `#:` markers matched direct runs, and every anchor resolves and covers what chapter 30 credits it with.
`tip verify-ch CH=30` passes 27 of 27, and `tip positional`, `tip stranded`, and `tip watch-words` report no new hit in the chapter
beyond a `you want` and a `never` that is the claim.

## Applied directly

Chapter, corrections:

- `weather_station.py` list item 2: "writes it through `self.__dict__` as the constructor does" was false; the constructor's two assignments go through `__setattr__()`. Now "as the `_responders` property does".
- Same list, item 3: `w.celcius` named a variable the listing does not have. Now `station.celcius`.
- Figure paragraph: "Two kinds of arrow cross into it" had the `connect()` arrows going the wrong way (the generator draws them from the responder into the list, and the `announce()` arrows out). Now "cross the boundary, in opposite directions".
- Return-value paragraph: GoF's broadcast-communication item supplies the premise (every observer receives, each decides whether to handle); the argument about combining return values is the chapter's own. "gives the reason" is now "supplies the premise".
- "composigion" and "the can responder catch".
- Tagging rule (Bruce, 2026-10-07): six positional pointers replaced by the construct itself. `weak_responder.py`'s "first/second `announce()`" are `announce(25.0)` and `announce(30.0)`; "The first line in `__setattr__()`" is "`__setattr__()` begins by reading"; "the last assignment" is `thermometer.celsius = 200`; "The next `announce()`" is `announce(2)`; "The last four lines of `model_view_controller.py`" is "Swapping in `NoKeys` at the end of".

Chapter, prose: "lands" (don't-use list) is "propagates"; two "already" dropped; the `Enum` parenthetical's period moved inside its parentheses; a comma before "then asks `at()`".

Solutions:

- Exercise 2: "the widest type `attach()` can hand it" named the wrong method; `notify()` calls `update()`. Now `notify()`.
- Exercise 6: the competition sketch had two players sharing one `select()` and comparing patches, but `FloodGame` holds one `origin` and one `owned` set, so there was one patch to compare. The sketch now says each player needs an origin and an owned set of their own.

## Considered and declined

- The order of the two closing sections, "What Stays Constant" (a summary) before "Deciding What Matters" (the design argument). The chapter points at "Deciding What Matters" from the Pythonic section as its destination, and the pass is yours and open, so the order reads as a choice.
- "Sending a change and receiving it share one name, `announce()`, where GoF has two": the receiving end has no name at all, which the sentence before it says, so the sentence reads as "one name where GoF needs two" and stands.
- Chapter 10's `#watching-objects-without-holding-them` for "tracing collector": the section covers PyPy and tracing collection, and chapter 10 has no better anchor.
- The hand-written `__init__()` methods (`TwoWay`, `ThresholdThermometer`, `Counter`, `BoxModel`): each exists to call `super().__init__()` on `Broadcaster`, and the `Thermometer` paragraph explains once why a `dataclass` cannot do that.
- `tip box_view`: not a task name, but `tip`'s listing fallback runs a listing named as the first word, so the sentence is right.
