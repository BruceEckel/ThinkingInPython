> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Chapters/26_Patterns--Surrogate.md`, 2026-10-16.
The chapter has been through several review rounds and reads cleanly:
no §7 vocabulary, no chatbot artifacts, and its watch-list hits all fall under the recurring keeps in `readability_db.md`.
Four small fixes went in directly, three of them restatements and one ambiguous pointer.
One block remains, about a cross-reference paragraph whose purpose only Bruce can confirm.

## Applied directly

- Line 329, treadmill (a short sentence the next one restates): "`__getattr__()` handles reads. Python calls it as the fallback for a read, and sends..." -> "Python calls `__getattr__()` as the fallback for a read and sends...".
- Line 487, §32 recap (the heading's words repeated as the section's last beat): cut "A surrogate is not its implementation." between "gives up both." and the advice to check for the method. Close alternative: keep it as a deliberate echo of the heading.
- Line 515, ambiguous pointer: "the `WeakValueDictionary` in its [Watching Objects Without Holding Them] section" -> "in that chapter's [...] section" ("its" could point at the `weakref` module or at Cleanup). Link target unchanged.
- Line 605, treadmill: cut "When a surrogate's `__getattr__()` raises something other than `AttributeError`, `hasattr()` raises that exception instead of returning `False`.", which restated the paragraph's opening rule after its application to `guest`; "The surrogate fails `isinstance()`..." -> "A surrogate fails `isinstance()`...", since its antecedent "a surrogate" went with the cut sentence.

## Line 514: the `weakref` cross-reference paragraph

§ portability / tangent.
After the paragraph on `weakref.proxy()`, a second paragraph points at chapter 10:

> The `weakref` module supplies the `weakref.finalize()` and `weakref.ref()` that [Cleanup](...) uses, and the `WeakValueDictionary` in that chapter's [Watching Objects Without Holding Them](...) section.
> Neither section needs `weakref.proxy()`.

The paragraph tells the reader where else the `weakref` module appears, then says those places do not use the function this section names.
It adds nothing about surrogates, and its last sentence is a negative that leaves the reader asking why it is mentioned.
If its purpose is to stop a reader from expecting `weakref.proxy()` in chapter 10, a shorter form keeps that: fold it into the paragraph above as "[Cleanup](10_Foundations--Cleanup.md#reliable-alternatives) uses other parts of the `weakref` module, not `weakref.proxy()`."
Recommended: cut the paragraph, since the paragraph above already says `weakref.proxy()` solves none of the four uses, which closes the topic.

[] Reject

## Considered and declined

- Line 216, "Python calls it only after normal lookup fails." The "only after" restriction is the definition of the fallback; the "only when/if" shape was ruled fine 2026-10-04.
- Line 209, "The double underscore on `self.__implementation` matters." A short beat among long sentences that the next sentence pays off; recurring keep.
- Line 438, "`isinstance()` checks only the proxy's own class." "only the X" is a ruled-fine shape, and the restriction is the claim.
- Line 481-483, "Both workarounds satisfy the runtime check. Neither satisfies a type checker. Inheritance satisfies both checks." Three short parallel sentences, but each carries a distinct claim the paragraph then uses; not staccato drama.
- Line 676-678, the smart-reference summary ("The same few lines serve lazy initialization ..., access checks ..., or call tracking ..."). A rule-of-three by shape, but the three items are the three proxy kinds the chapter just demonstrated, so it is a synthesis, not padding.
- Line 781, "Only the surrogate's current implementation changes." Partly restates the sentence under `state_demo.py`, but it closes the figure walkthrough by naming the one thing that changes; sentence-initial "Only" is ruled fine.
- Line 894 (exercise 5), "a reference to the actual connection": "actual" contrasts with the proxy named in the same sentence (§34 keep), and exercise imperatives are exempt.
- Line 868, "simpler and just as flexible": a comparison, not an empty "just".
- The `in order to implement the *copy-on-write* idiom` keep in `readability_db.md` no longer applies: the smart-reference list item now reads "which makes *copy-on-write* possible", with the causal link intact.
