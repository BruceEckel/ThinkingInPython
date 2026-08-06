[[Reviewed]]
# Deep review: 21_The_Pattern_Concept.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Give the dissolution thesis its own section, and make its mechanism cover all four chapters that cash it in

**Kind:** structure + teaching
**Where:** section "What Is a Pattern?", final paragraph (lines 80-91)

**Problem:** three things go wrong at once in the chapter's most important paragraph.

*It cannot be linked to.* This paragraph is the argument that chapters 23, 24, 27, and 28 rest on. Chapter 23 already tries to point at it: "This is the dissolution described in [The Pattern Concept](21_The_Pattern_Concept.md)." That link lands on the top of the chapter, and the reader has to hunt through four screens of prose to find the two sentences the link meant. There is no heading to anchor to.

*Its stated mechanism is wrong for three of the four cases.* The paragraph says "When a language **later** absorbs the feature, the pattern dissolves into it," then "Python has absorbed several." That is true of Iterator, which arrived as a protocol in Python 2.2. It is not true of anything else the paragraph names. Python did not later absorb first-class functions, so *Strategy* and *Command* did not dissolve by absorption; they were never needed, because a Python function has been an object since the first release. The same holds for Factory (a class is an object) and Singleton (a module is imported once and cached). Norvig's own breakdown groups his 16 patterns by enabling feature (first-class types, first-class functions, macros, method combination, multimethods, modules), and only one of those six is a feature any of these languages acquired late.

*It sets up half the Part.* It names Iterator, *Strategy*, and *Command*, so chapters 23 and 28 have an anchor here. Chapter 24 (a module is already a singleton) and chapter 27 (the `dict` is the factory) have none, and those two are the most surprising dissolutions in the book.

**Proposal:** split at line 80 into a new section and rewrite the paragraph. Everything above line 80 stays in "What Is a Pattern?" (chapter 37 links to that anchor for the vector of change, so the heading text must not change).

> ## When a Pattern Dissolves
>
> A pattern is often a sign of something missing in a language.
> Programmers wrote the same scaffolding often enough that it acquired a name.
> It exists only because the language does not write it for them.
>
> The missing piece can arrive in two ways.
> Sometimes a language grows the feature and the pattern dissolves into it^[Peter Norvig made this observation in his 1996 talk "Design Patterns in Dynamic Programming": 16 of the 23 GoF patterns become invisible or simpler in a dynamic language.].
> Iterator is the clear case.
> It was implicit in the `for` loop from the start,
> and Python 2.2 made it a protocol the language calls on your behalf.
> More often the language had the piece all along,
> and the pattern was written for one that didn't.
> *Strategy* and *Command* shrink to passing a function,
> because a Python function is an object
> ([Function Objects](28_Function_Objects.md) shows both).
> A [Factory](27_Factory.md) becomes a dictionary, because a class is an object too.
> [Singleton](24_Singleton.md) becomes a module,
> because Python imports each module once and caches it.
>
> This is why the chapters ahead keep asking the question
> [Rethinking Objects](20_Rethinking_Objects.md#guidelines) posed:
> how much of each pattern's machinery does Python still need,
> and how much of it becomes functions, data, and protocols?

**Alternative:** keep the paragraph inside "What Is a Pattern?" and only fix the mechanism and the two missing chapters. That leaves the inbound links from 23/24/27/28 pointing at the whole chapter.

**Cost:** a new anchor, `#when-a-pattern-dissolves`. Chapter 23's line 503 link should gain it, and chapters 24, 27, and 28 could gain one where they open with "Python already provides this." Those are edits to other chapters, so the coordinator applies them; nothing breaks if they are skipped. The new `#guidelines` anchor on the chapter-20 link resolves today (`## Guidelines`, line 962). `heading_links.py` gates all of it. The Iterator link at line 73 stays where it is, in the paragraph above the split.

---

## 2. The chapter ends on a list, so the argument never lands as an instruction

**Kind:** structure
**Where:** end of "Design Principles" (line 212)

**Problem:** the last thing the reader sees is twelve named principles and one sentence about holding them in their head. The chapter's actual claim, that a pattern earns its place only when its problem is present and that Python has already solved part of several, is left forty lines back. A chapter whose job is to frame an entire Part should close by telling the reader what to do with the twenty chapters that follow. Chapter 20 ends with exactly such an instruction ("For each pattern, ask whether you need the objects and the inheritance"), which means the new closing must add something rather than repeat it.

**Proposal:** add a short closing section after the principles list. It picks up *Subtraction* from the list directly above it, so the section it follows is doing work rather than trailing off.

> ## Reading the Chapters Ahead
>
> Each chapter in this part takes one pattern and asks three questions of it.
> What varies and what stays the same?
> That names the problem the pattern exists to solve.
> How much of the answer does Python supply on its own?
> That decides how much is left for you to write.
> What remains after you subtract the rest?
> That remainder is worth learning, and it is usually the intent rather than the structure.
>
> A pattern that subtracts to nothing was not a mistake.
> It was the right answer for a language missing the piece Python has.

**Cost:** one new heading and anchor. Nothing links to the end of this chapter today.

---

## 3. The evolution ladder and dissolution are the same axis, and the chapter never says so

**Kind:** teaching
**Where:** end of "Pattern Evolution" (line 118)

**Problem:** "Pattern Evolution" walks a pattern up four stages, from idiom to design pattern. Dissolution walks it back down: a pattern the language builds in becomes an idiom again. These are one idea seen from two ends, they sit in adjacent sections, and a reader is left to notice the connection unaided. Making it explicit is what turns the four stages from a taxonomy into a claim about where a pattern comes from and where it goes.

**Proposal:** append to "Pattern Evolution", after "They tend to be subtle and appear over time.":

> The ladder runs downward too.
> A pattern a language builds in drops back to stage one,
> and the programmers who arrive next learn it as syntax rather than as a design.
> Stepping through a container is stage one in Python
> and was stage four in the *GoF Design Patterns* examples.

**Cost:** none. Reads correctly whether or not proposal 1 lands, since dissolution is introduced before this section either way.

---

## 4. The chapter has no exercises

**Kind:** exercise
**Where:** end of chapter

**Problem:** every chapter in this Part has exercises except this one. The only other chapters without them are the catalog (39) and the toolkit tour (41), both reference material. This chapter makes three claims a reader can practice without writing a line of code (find the vector of change, subtract what the language supplies, subtract until something breaks), and it asks for none of them.

**Proposal:** add three code-free exercises. Each is answerable from this chapter alone.

> ## Exercises
>
> 1.  Pick a program you have written that changed more than once.
>     Name its vector of change: the thing that shifted every time.
>     Say which part of the design absorbed the change,
>     and which parts you edited by hand.
> 2.  Take a pattern you know from another language and list its parts:
>     the classes, the interfaces, and the methods its usual form requires.
>     Cross out every part Python supplies without your writing it.
>     Describe what is left in one sentence.
> 3.  Apply *Subtraction* to a design of your own.
>     Remove one class, one interface, or one level of inheritance,
>     and say what stopped working.
>     If nothing did, leave it out.

**Cost:** no code, so nothing to extract, sync, or gate. Exercise 3 assumes proposal 2 has not renamed *Subtraction*.

---

## 5. Norvig's 16 of 23 is a Lisp and Dylan count, and Python's line falls elsewhere

**Kind:** teaching
**Where:** footnote at line 84

**Problem:** the footnote gives "16 of the 23 GoF patterns become invisible or simpler in a dynamic language" with no qualification, and the sentence before it is about Python. A reader takes 16/23 as Python's number. Norvig's talk was about Lisp and Dylan, and the seven he leaves out are Singleton, Composite, Decorator, Adapter, Bridge, Prototype, and Memento. Singleton being on the *surviving* side is the interesting part: chapter 24 opens by showing that a Python module already is one. Python dissolves at least one pattern Norvig's list keeps, which strengthens the chapter's thesis instead of weakening it, and the chapter currently gets no use out of it. (Checked against Norvig's slides: the 16 are grouped under first-class types, first-class functions, macros, method combination, multimethods, and modules.)

**Proposal:** extend the footnote:

> ^[Peter Norvig made this observation in his 1996 talk "Design Patterns in Dynamic Programming": 16 of the 23 GoF patterns become invisible or simpler in a dynamic language. He counted for Lisp and Dylan, and Python's line falls in a different place. Singleton is one of the seven he leaves standing, and [Singleton](24_Singleton.md) shows that a Python module already is one.]

**Alternative:** leave the footnote and put the Singleton observation in the body of the dissolution section, where it would be read rather than skipped.

**Cost:** a cross-reference to chapter 24 from inside a footnote. `heading_links.py` checks footnote links the same as any other.

---

## 6. The evolution ladder shows Python examples for its two ends and neither middle

**Kind:** teaching
**Where:** section "Pattern Evolution" (lines 110-113)

**Problem:** stage one gets `with open(...)` and stage four gets Template Method. Stages two and three, the two the reader is least able to picture, get nothing. The difference between "a clever design for this problem" and "a design general enough to reuse" is the whole middle of the ladder, and a reader cannot check their understanding of it against anything.

**Proposal:** insert between the two existing examples:

> A dictionary mapping one program's shape names to its shape classes is a specific design, stage two.
> The same dictionary, filled by each subclass as it is defined so that adding a type never edits the factory,
> is a standard design, stage three ([Factory](27_Factory.md) builds both).

**Cost:** a third link to chapter 27 in this chapter. Chapter 27's "The Pythonic Factory: a Dictionary" builds both forms, so the description matches what the reader will find.

---

## 7. *Structural* is the only taxonomy entry with no chapter behind it

**Kind:** teaching
**Where:** section "Pattern Taxonomy", list item 2 (lines 132-133)

**Problem:** *Creational* names Singleton and factories with links, and *Behavioral* names Observer, State Machines, and Visitor with links. *Structural* gets "designing objects to satisfy particular project constraints," which is the vaguest of the three descriptions and points nowhere. The reader then meets Bruce's complaint that *Structural* is not a useful category, with no examples in hand to judge that against.

**Proposal:** append to item 2:

> [Surrogate](26_Surrogate.md), [Changing the Interface](29_Changing_the_Interface.md),
> and [Flyweight](35_Flyweight.md) cover the structural patterns in this book.

**Cost:** three cross-references. All three chapters exist and are structural in GoF's own classification.

---

## 8. Twelve named principles, one link, and none of the names appear again in the book

**Kind:** teaching
**Where:** section "Design Principles" (lines 172-210)

**Problem:** the reader is handed twelve principles by name and told to hold them in their head, and only one (*Make things as immutable as possible*) says where the book demonstrates it. Grepping the rest of `Chapters/` for "Law of Demeter", "least astonishment", "Once and once only", "Simplicity before generality", "Reflexivity", "Managed Coupling", "Orthogonality", and "Subtraction" returns nothing outside this chapter. The names never recur, so the list reads as aphorisms rather than as a map into the Part.

**Proposal:** link the three that the book clearly demonstrates, matching the treatment *Make things as immutable as possible* already gets.

- *Simplicity before generality*: append "[Pattern Refactoring](37_Pattern_Refactoring.md#choosing-the-lightest-construct) works through a case of this, one requirement at a time."
- *Independence* or *Orthogonality*: append "[Rethinking Objects](20_Rethinking_Objects.md#prefer-composition-to-inheritance) makes the composition case for it."
- *Make functions pure whenever you can*: link to [Pure Functions](40_Functional_Foundations.md#pure-functions).

**Alternative:** leave the list as a standalone reference, on the same footing as chapter 39's catalog, and accept that the names are for recognition rather than for use.

**Cost:** three cross-references, two of them forward into chapters 37 and 40. All three anchors exist today. I deliberately left *Law of Demeter*, *Reflexivity*, and *Subtraction* unlinked; nothing in the book treats them squarely enough to point at.

---

## 9. The opening announces examples the chapter does not contain

**Kind:** prose
**Where:** lines 13-14

**Problem:** "I introduce the basic concepts of design patterns, along with examples." This chapter has no listings, which is deliberate and right for a framing chapter, but the sentence tells the reader otherwise on page one of the Part. The sentence before it, "A significant portion of those examples provides inspiration for much of this part of the book," hedges twice ("a significant portion", "much of") to say something simple.

**Proposal:** replace both lines with:

> Many of those examples inspired the ones in this part of the book.
> This chapter introduces the concepts; the chapters after it supply the code.

**Cost:** none.

---

## 10. Small prose items

**Kind:** prose
**Where:** various

- line 64: "You've already seen some design patterns in this book." "already" is on the watch list, and the sentence carries the same meaning without it: "You have seen some design patterns in this book."
- lines 65-71: inheritance and composition are presented as patterns "built into the language," which is the dissolution argument arriving twenty lines before the paragraph that makes it. One clause would connect them, for example ending line 66 with "(albeit one built into the language, which is a case worth returning to)". Skip this if proposal 1 lands and you would rather keep the two passages independent.
- lines 35-36: "Instead, a pattern embodies a complete idea within a program. Thus it can sometimes appear at the analysis phase or high-level design phase." The "Thus" does not follow from "complete idea"; completeness is not what makes a pattern visible during analysis. Either supply the missing step or drop the "Thus".
- line 131: "you'll see examples of [factories](27_Factory.md)" is the only lowercase pattern name in the chapter. Every other one is capitalized as a proper noun. Suggest "[Factory](27_Factory.md) methods and factory classes".
- line 130: "counts as a creational pattern" against *Creational* italicized in the critique below it. Pick one form.
- line 212: "while walking through and analyzing your design" says one thing twice. "while analyzing a design" is enough. If proposal 2 lands, this sentence closes the principles list rather than the chapter, which suits it better.

**Cost:** none of these touch code or anchors.

---

## Already fixed directly (no decision needed)

- Nothing. The chapter contains no code, no broken cross-reference, no banned phrase, and no false factual claim that a small edit would fix. The one place where it states something not quite true (Python "absorbed" first-class functions) is the substance of proposal 1, so I left it rather than making a partial fix that the proposal would then rewrite again.

## Verified clean (no action)

- `heading_links.py` and `banned_phrases.py` both pass. All eight outbound links resolve, as do the three inbound ones (23:503, 29:258, 37:407), and both anchored inbound links point at material this chapter genuinely contains: `#what-is-a-pattern` holds the vector of change that chapter 37 cites, and chapter 29's claim that "the remaining difference is intent" is stated at lines 161-162.
- No listings, so no `ty`, `ruff`, `pytest`, or `#:` marker surface. Prose-only is consistent with the book's other two framing chapters, 01 and 39; I did not propose adding a listing, since chapters 23, 24, 27, and 28 each open with the concrete version of this chapter's claim.
- Facts checked and correct: the 1994 publication and the four authors; sample code in C++ with some Smalltalk; 23 patterns under three purposes; Iterator implicit in `for` before Python 2.2 and an explicit protocol from 2.2 (PEP 234); the Norvig talk's title, year, and 16-of-23 figure; the Saint-Exupéry attribution, which is correctly hedged with "generally attributed to" and is in fact right.
- The book's own regrouping claims at lines 155-160 all hold: chapter 26 does treat Proxy and State as one front-object structure, chapter 28 does treat Command, Strategy, and Chain of Responsibility as one function-passing structure, and chapter 34 does treat both of its patterns as one recursive-data structure.
- Section order passes the assumes/introduces test: nothing in an earlier section depends on a later one, and every transition has a stated reason rather than "this is also about design."
- Watch-list sweep over the whole chapter found five hits (`already`, `itself` x2, `happen`, `only` x4). Only the first is worth touching (proposal 10); "talk only to itself" is reflexive and required, and "Coupling happens" is doing real work.
- Semantic Line Breaks are clean throughout; no em-dashes were added or removed.
