[[Reviewed]]
# Deep review: 29_Changing_the_Interface.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Show the module façade, don't only assert it

**Kind:** teaching
**Where:** section "Façade" (line ~242), the paragraph beginning "The cleaner Python façade is a *module*."

**Problem:** The Adapter half of the chapter has a Java-shaped section and then an "Adapter in Python" section with a working listing that shows the Python answer. The Façade half has only the Java-shaped listing. The Python answer is four sentences of prose with nothing to run: "the `import` is the façade" is told, never shown. That is the section's central claim and it is the only claim in the chapter with no code behind it. A reader who has just watched `getattr_adapter.py` replace fifty lines of hierarchy with six is entitled to the same demonstration here, and the chapter is 100+ lines shorter than either neighbor (26, 28, 30), so there is room.

**Proposal:** After the "The cleaner Python façade is a *module*" paragraph, add two listings. Verified: runs clean, prints `97.20`, no line over 70, ruff and ty clean (import resolves the same way `test_adapter.py` resolves `getattr_adapter`).

```python
# checkout.py
from dataclasses import dataclass

@dataclass(frozen=True)
class _TaxRule:
    rate: float

@dataclass(frozen=True)
class _Discount:
    fraction: float

class _PriceEngine:
    def __init__(self, tax: _TaxRule, cut: _Discount) -> None:
        self.tax = tax
        self.cut = cut

    def compute(self, amount: float) -> float:
        net = amount * (1 - self.cut.fraction)
        return net * (1 + self.tax.rate)

def total(amount: float) -> float:
    engine = _PriceEngine(_TaxRule(0.08), _Discount(0.10))
    return engine.compute(amount)
```

```python
# checkout_demo.py
import checkout

print(f"{checkout.total(100.0):.2f}")
#: 97.20
```

with a short connecting sentence after the second block, roughly:

> The caller imports one name.
> Three classes and the order they must be assembled in stay behind the underscore,
> and the façade can rearrange them without touching a caller.

Alternative if two listings is too much: keep only `checkout.py` and drop the demo, letting the prose report the result. That costs the runnable `#:` marker, which is what makes the point land.

**Cost:** Two new example files (`Examples/29_Changing_the_Interface/checkout.py`, `checkout_demo.py`); neither basename collides with anything in `Examples/`. Nothing cross-references the Façade section except `39_Pattern_Catalog.md`'s `#façade` anchor, which is untouched. Needs the normal sync + gate loop.

---

## 2. The opening announces two patterns; the chapter delivers four sections

**Kind:** structure
**Where:** the opening paragraph (lines 3-7), against "Telling the Wrappers Apart" (line ~252) and "Retiring the Old Interface" (line ~271)

**Problem:** The intro says "Two of the patterns in *GoF Design Patterns* solve this problem" and names Adapter and Façade. The reader therefore expects a two-pattern chapter and is done after the Façade section. Two more sections follow, and the second of them (deprecation) is not a GoF pattern at all and is arguably the most practically useful material in the chapter. It arrives with no setup, so a skimmer never gets to it.

**Proposal:** Extend the opening by two sentences so the arc is visible, roughly:

> Both wrap something that already exists, which puts them next to Proxy and Decorator,
> and the chapter ends by sorting the four apart.
> Adding an interface is the safe half of the job.
> The other half is telling callers that the interface they have been using is going away.

**Cost:** none. Prose only, no terms defined, no listing affected.

---

## 3. Turn the wrapper map into a table, and reconcile its Proxy line with chapter 26

**Kind:** teaching
**Where:** section "Telling the Wrappers Apart" (lines ~252-269)

**Problem:** Two things. First, the section's payload is a four-way comparison delivered as four consecutive sentences, which is the one shape a reader cannot scan back to when they are actually stuck choosing a name for a wrapper. Second, the Proxy line says a Proxy "keeps the wrapped object's interface," which is GoF's definition. [Surrogate](26_Surrogate.md#proxy) explicitly rejects that half: "It isn't necessary that `Implementation` have the same interface as `Proxy` ... (this statement is at odds with the definition for *Proxy* in *GoF Design Patterns*)." So the book's own Proxy chapter loosens the criterion this chapter then uses to tell Proxy from Adapter. This chapter already notes the GoF definition once (line ~99, on the `ProxyAdapter` name), so the tension is visible to an attentive reader and unresolved.

**Proposal:** Replace the four sentences with a table, and let the Proxy row own the disagreement:

| Wrapper | Interface | What it adds | Remove it and you lose |
| --- | --- | --- | --- |
| [Proxy](26_Surrogate.md#proxy) | same, by GoF's definition | access control | control over when and whether the call gets through |
| [Decorator](14_Decorators.md#the-decorator-pattern) | same | behavior | the added behavior |
| Adapter | changed | nothing | the fit between caller and callee |
| Façade | many narrowed to a few | nothing | the simplicity |

Keep the surrounding prose (intent is what separates them, per [The Pattern Concept](21_The_Pattern_Concept.md)) and add one sentence after the table:

> [Surrogate](26_Surrogate.md#proxy) takes the looser view of the first row:
> a surrogate speaking for its implementation is a Proxy whether or not the interfaces match.
> Under that reading the Adapter is what a Proxy becomes once you stop insisting on the interface,
> which is why the `ProxyAdapter` above answers to both names.

Alternative if the table is unwanted: keep the sentences and add only the reconciling sentence. The reconciliation is the part worth having.

**Cost:** Chapter 26 is the other end of this thread and is being reviewed concurrently; if that review changes 26's stance on the Proxy interface, this table's first row has to follow. GitHub pipe tables are fine here (no colspan, no colored text).

---

## 4. No exercise covers Façade

**Kind:** exercise
**Where:** section "Exercises" (line ~328)

**Problem:** Both exercises come from the chapter's second half: exercise 1 extends `getattr_adapter.py`, exercise 2 extends `deprecating.py`. Façade is a titled section with a named pattern and gets nothing, so the reader never builds one. It is also the section whose Python answer is the least concrete (see proposal 1), which is where practice would help most.

**Proposal:** Add a third exercise. Written against proposal 1's listings; if that proposal is rejected, retarget it at `facade.py`:

> 3.  Rewrite `facade.py` as a module façade.
>     Put `A`, `B`, and `C` behind leading-underscore names in one module,
>     expose three functions that build them, and import only those from a second file.
>     Compare what a caller can see in each version.

**Cost:** `Solutions/29_Changing_the_Interface.md` needs a matching third solution, which I did not write (Solutions is out of scope for this pass).

---

## 5. `@overload` deprecation is a spec claim the book's own checker does not honor

**Kind:** code
**Where:** section "Retiring the Old Interface" (line ~319), the paragraph beginning "`@overload` accepts it too"

**Problem:** The claim is correct per PEP 702 and is implemented by mypy and pyright, but I verified that `ty` 0.0.65 reports nothing for a call that selects a deprecated overload, while it does flag the deprecated *method* in `deprecating.py` (`warning[deprecated]: The function to_string is deprecated`). A reader who follows the chapter's own toolchain tries the finer instrument and gets silence, with no way to tell whether they wrote it wrong. The chapter is otherwise careful to say when a checker's behavior is the reason a listing looks the way it does (the `Any` on `WhatIUse2.op()`, the `# type: ignore` two paragraphs above this one).

Probe used:

```python
@overload
@warnings.deprecated("Pass a Path instead of a str")
def load(source: str) -> bytes: ...
@overload
def load(source: Path) -> bytes: ...
def load(source: str | Path) -> bytes: ...
load("a.txt")   # ty 0.0.65: no diagnostic
```

**Proposal:** Add one sentence to the end of that paragraph:

> Checker support for the per-overload form lags the whole-function form,
> so verify your checker reports it before relying on it.

Alternative: name `ty` and the version. That dates faster and would need re-checking at every `make upgrade-tools`, so I recommend the version-free wording.

**Cost:** none, unless a later `ty` implements it, at which point the sentence is merely conservative rather than wrong.

---

## 6. The `__getattr__` adapter has a footgun that survives being copied into real code

**Kind:** teaching
**Where:** section "Adapter in Python" (line ~171), the paragraph beginning "The forwarding has the limit noted in [Surrogate]"

**Problem:** The chapter hands the reader `getattr_adapter.py` and calls it "the idiomatic Python adapter," which invites copying it. `copy.copy()` and `pickle` both build an instance without running `__init__()`, so `self._adaptee` does not exist, so `__getattr__("_adaptee")` calls itself forever. Verified against the chapter's exact class:

```python
a = Adapter(WhatIHave())
copy.copy(a)    # RecursionError
```

[Surrogate](26_Surrogate.md#proxy) teaches the mechanism ("any attribute on an instance built without `__init__()`") but does not connect it to `copy` or `pickle`, and this chapter cites 26 only for the dunder limit. The reader has the pieces and no reason to put them together until something explodes.

**Proposal:** Extend the existing cross-reference sentence to carry both limits rather than one, roughly:

> That chapter's other trap applies here too:
> `__getattr__()` reading `self._adaptee` recurses forever on an instance built without `__init__()`,
> which is what `copy.copy()` and `pickle` do,
> so an adapter that must be copied or pickled defines `__reduce__()` or guards the lookup.

Alternative: leave it, on the grounds that 26 already states the rule and 29 should not repeat it. I lean against, because the `copy`/`pickle` trigger is not obviously an instance of "built without `__init__()`" to a reader who has not met `__reduce__()`.

**Cost:** none; prose only, and the mechanism is already established in 26 so nothing new is introduced.

---

## 7. `facade.py` is inert scaffolding

**Kind:** code
**Where:** section "Façade", listing `facade.py` (lines ~210-240)

**Problem:** Three classes whose `__init__` bodies are `pass`, three static methods that call them, and three module-level names `a`, `b`, `c` that are assigned and never read. The listing produces no output and carries no `#:` markers, so it is the only listing in the chapter a reader cannot run to learn anything. It is inherited straight from the Java original, where the shape was the whole point; in a book whose stated position two paragraphs later is that this construction is unnecessary in Python, it spends thirty lines establishing a straw man.

**Proposal:** Shrink it to the smallest thing that shows the shape: one hidden class, one exposed class, two static methods, and drop the unused `a`/`b`/`c` bindings in favor of one `print()` with a `#:` marker showing that the caller only ever names `Facade`. Keep the "Other classes that aren't exposed" comment, which is the listing's actual teaching content.

Alternative: leave `facade.py` alone and let proposal 1's `checkout.py` carry the contrast by sitting next to it. This is cheaper and loses little, since the Java shape being clumsy is part of the argument.

**Cost:** Changes `Examples/29_Changing_the_Interface/facade.py`. Nothing imports it and no test covers it.

---

## 8. Split the "Two details" wall

**Kind:** prose
**Where:** section "Adapter", lines ~102-126

**Problem:** One paragraph of fourteen lines announces "Two details," never marks the first, spends nine lines on positional-only parameters and the `Any` escape, then says "Second" and switches to the object-adapter/class-adapter distinction. The second detail is the one with lasting value (it names a GoF distinction the reader will meet again); the first is a `ty` mechanics footnote. As written the important half arrives after the reader has already been asked to hold a lot.

**Proposal:** Break at "Second," into two paragraphs and mark the first detail with "First," so the numbering the sentence promises is visible. Consider also moving the object/class adapter paragraph *before* the positional-only paragraph, so the pattern content leads and the checker mechanics trail.

**Cost:** none. Pure paragraph surgery, no sentence rewritten, no cross-reference affected.

---

## 9. The deprecation-warning paragraph's "so" does not follow

**Kind:** prose
**Where:** section "Retiring the Old Interface" (lines ~309-311)

**Problem:** "The runtime half is a `DeprecationWarning`, which Python hides by default outside of `__main__` and test runners, so the listing records the warnings rather than letting them go to standard error." Both facts are correct, but the second does not follow from the first: the listing *is* `__main__`, so the warning is shown, and the reason for recording it is that a `#:` marker captures stdout and a warning goes to stderr. As written it reads as though the recording works around the hiding.

**Proposal:** Split into two claims:

> The runtime half is a `DeprecationWarning`.
> Python hides those by default outside `__main__` and test runners,
> which is the trap: the caller who most needs the warning is the least likely to see it.
> A warning also goes to standard error, where a `#:` marker cannot capture it,
> so the listing records the warnings instead of printing them.

**Cost:** none.

---

## Already fixed directly (no decision needed)

- line ~116: "It allows an override that cannot substitute for its base to compile." became "... to pass the type checker." The `Any` has no effect on compilation; Python compiles the precisely-annotated version too. Every other use of "compile" in the book (05, 18, 19, 20) means real compilation or another language, so this one also read out of character.

## Checked and correct (no change proposed)

- All four listings run and match their `#:` markers exactly; `ruff`, `ty`, and `pytest` all clean against `build/examples/29_Changing_the_Interface`.
- `heading_links.py` and `banned_phrases.py` both pass.
- Verified with `ty` 0.0.65 that removing the `/` from `WhatIUse.op()` produces `invalid-method-override` naming the parameter rename, and that annotating both parameters precisely produces `invalid-method-override` citing Liskov. Both match the prose.
- Verified that `@warnings.deprecated` on a class warns on construction *and* on subclassing, as the chapter claims.
- Verified `PairCoord` in `20_Rethinking_Objects.md` is a frozen dataclass with two properties adapting `Pair` to `Coord`, as described.
- The Decorator row of the wrapper map matches `14_Decorators.md#the-decorator-pattern` (`Topping` satisfies `Pizza` and adds cost/description). Only the Proxy row is in tension with its source; see proposal 3.
