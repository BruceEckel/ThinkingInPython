> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 33_Patterns--Visitor (second review, 2026-09-29)

This second review follows `~33_Patterns--Visitor.md` (2026-09-25) and the 2026-09-27 fix triage, which cut one sentence here ("The chapter opens with the difference in intent."). The paragraph after the cut still has its subject, so nothing was restored.
This run found nothing that needs your decision, so the file has no live blocks.
Probes on `ty` 0.0.84: `accept(self, visitor: Visitor)` draws `unresolved-attribute` on `visitor.visit`; `nectar(42)` passes; `Gladiolus().accept(Bug())` raises `AttributeError: 'Bug' object has no attribute 'visit'`; Solutions exercise 3 without its `# type: ignore` draws `invalid-argument-type`. Every cross-chapter link was checked against its target (22, 27, 32, 34, 37, 41, 14).

## Applied directly

Chapter:

- "The Price of the Empty Base": "The chapter keeps `Any` because the empty `Visitor` base is what the classic pattern looks like" contradicted the paragraph above it, which says the classic pattern declares `visit()` abstract on the visitor base. Now: "The chapter still keeps the empty `Visitor` base and its `Any`, because showing what the `Any` gives up is part of the point."
- Classic Visitor intro: the sentence before `flower_visitors.py` ended "... below explains why:", so the colon presented the listing as the explanation. The link sentence now ends with a period, and "In the listing, bugs visit flowers:" introduces the code.
- "If you delete the override ... the output depends on the visitor's type alone": the output still names the flower. Now "the visitor's type alone decides which method runs."
- `@overload` sentence: dropped "itself" from "branch on the argument's type itself".

Solutions:

- Exercise 1: `pollinate()` was a `@singledispatch` function with no registrations, which contradicts chapter 37's rule that `singledispatch` is for behavior that differs by type. It is now an ordinary function, and the prose says why only `eat()` dispatches. `eat()` hard-coded "Worm" while `pollinate()` took its agent as an argument; both now take the visitor's name. The answer to "which methods disappear" now names `pollinate()`, `eat()`, and `Chrysanthemum`'s override, not only `accept()`. The `dict` of operations is typed `Callable[[Flower, str], str]` instead of `Callable[..., str]`. "has to explain" became "explains".
- Exercise 2 asks you to count the lines each change costs, and the answer gave no counts. It now says eight lines for `Rose` and six for `thorns()`.
- Exercise 3: "The classic pattern pays that price because its `Visitor` base is empty" had the same error as the chapter sentence above; now "The chapter's version", with "as the classic pattern does" on the abstract-`visit()` fix. "buys the check back" became "restores the check". "Delete it and `ty` reports the mismatch" (imperative plus consequence) now says why the comment is there and names the diagnostic. "The `Visitor` hierarchy stays as the chapter wrote it" now says the listing keeps only the pollinating half.

## Considered and declined

- The declined rewrite from the first review (operations kept in the visitor instead of on `Flower`) stays declined; nothing in this pass changes its case.
- "(chrysanthemums really do produce a natural insecticide)": "really" is the author's voice in an aside. Left.
- "turns a plain function into one that dispatches" and "each operation is a plain function": both draw a contrast (a dispatching function, a method), so "plain" stays.
- The chapter's link to Data Transfer Objects now carries `#a-hand-rolled-messenger`, where `deep_review_db.md` recorded a deliberate anchorless link. The `Any` discussion now sits under that heading in chapter 22, so the anchor is correct.
