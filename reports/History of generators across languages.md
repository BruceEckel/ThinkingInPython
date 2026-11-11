# Generator features spread by citation, not osmosis

The generator has two documented roots and one documented hub.
The roots are IPL-V (1959 to 1961), whose designers used the word first, and CLU (designed September 1975), which introduced a single resumable routine with a `yield` statement after its designers saw Alphard's generator ([Liskov 1992](https://www.cs.tufts.edu/~nr/cs257/archive/barbara-liskov/clu-history.pdf)).
The hub is Python: PEP 255 (2001) credits Sather, CLU through Sather, and Icon, and then JavaScript 1.7 (2006), PHP 5.5 (2012), ES6 (2012 to 2015), and PHP 7 (2015) each credit Python in a designer's own words.
**`yield from` as a spelling and as a two-way coroutine call originates in Greg Ewing's PEP 380 (February 2009), which cites no other language, but one-way delegation is older**: Icon's `suspend expr` was in print in April 1981, Cω's flattened streams and the `yield foreach` paper date from 2005, and F#'s `yield!` from 2007.
From PEP 380 the lineage is stated outright: Brendan Eich wrote "PEP-380 is the basis" of ES6's `yield*` in May 2012, and the PHP 7 RFC names Python 3.3 and ES6 as its models.
Two-way send, exception injection, close, and return values were assembled inside Python from earlier Python proposals (PEP 288, PEP 325), with Ruby the only outside language named.
The direction of credit reverses for async/await: F# (2007) to C# 5 (2012), by the F# authors' account, and C# to Python, which PEP 492 states.
Many links that the secondary literature repeats, such as CLU to C# iterators, CLU to Ruby blocks, and C# to JavaScript async functions, have no designer's sentence behind them in the research notes, and this report labels each of them as inferred or unverified.

## How to read the evidence labels

Every claim of influence below carries one of four statuses.
*Stated* means a primary source by the borrowing design's authors says it, and the researchers read that text.
*Snippet only* means the researchers saw a search-result summary and could not open the document, so the wording can be a paraphrase.
*From memory* or *unverified* means a researcher recalled the fact and found no source to open.
*Inferred from timing* means the dates and the shapes agree and no source states the link.
The research notes are dated 2026-11-11, and three of their corrections to common assumptions are used here.
The author of PHP's Generator Delegation RFC is Daniel Lowrey, with Bob Weinand as contributor, and the RFC page shows no role for Andrea Faulds ([PHP RFC: Generator Delegation](https://wiki.php.net/rfc/generator-delegation)).
PEP 288 has the status Withdrawn, where PEP 325 and PEP 340 are Rejected ([PEP 288](https://peps.python.org/pep-0288/)).
The earliest located statement of the cost of recursive iterators is Grant Richins's pair of blog posts of March and April 2004, and Wes Dyer's 2007 post and Eric Lippert's 2009 comment are later ([Toub 2004](https://learn.microsoft.com/en-us/archive/blogs/toub/recursive-iterator-performance)).

## 1959 to 1995: `yield` enters with CLU, and every later design cites a predecessor

### Two older senses of "generator" precede the resumable routine

The word comes from IPL-V.
Griswold, Hanson, and Korb wrote in 1981: "An early language that has generators is IPL-V [31], in which a generator is a subroutine that calls a processing routine to operate on each object in a data structure" ([Generators in Icon, section 5](https://drh.github.io/documents/generators-in-icon.pdf)).
That generator drives the loop and calls the consumer, which is the reverse of the modern direction of control.
The Sather authors trace the idea to the same language: "The idea of generalizing iteration control structures goes back to early work such as the generators of IPL-V [12] or the generators and 'possibility lists' of Conniver [9]" ([Murer et al. 1995, section 4.1](https://steveomohundro.com/wp-content/uploads/2009/03/murer_omohundro95_iteration_abstraction_in_sather.pdf)).
The researchers did not read the IPL-V manual, so IPL-V's definition reaches this report through those two later papers and through the earlier report's reading of Newell and Tonge's 1960 article ([Newell and Tonge 1960](https://iiif.library.cmu.edu/file/Newell_box00004_fld00298_doc0001/Newell_box00004_fld00298_doc0001.pdf)).

The mechanism comes from the coroutine.
Conway's paper of July 1963 defines coroutines as "subroutines all at the same level, each acting as if it were the master program when in fact there is no master program", and its footnote says "the coroutine idea was concurrently developed by him and Joel Erdwinn" ([Conway 1963](https://www.melconway.com/Home/pdf/compiler.pdf)).
Conway's definition is symmetric and has no yielded sequence.
The date 1958 for the coinage, and the unpublished Erdwinn and Merner paper "Bilateral Linkage", come from Knuth's history note in The Art of Computer Programming.
The researchers could not open that note, so both facts are unverified here and rest on Wikipedia's citation of Knuth ([Wikipedia, Melvin Conway](https://en.wikipedia.org/wiki/Melvin_Conway)).
Simula 67 gave coroutines language support through `call`, `detach`, and `resume`, per Knuth and Ruskey ([arXiv cs/0404058](https://arxiv.org/abs/cs/0404058)).
Griswold's 1981 paper says "Languages that support coroutines frequently use the term generator to describe a particular coroutine usage. SIMULA [1] is the oldest of such languages" ([Generators in Icon, section 5](https://drh.github.io/documents/generators-in-icon.pdf)).
Whether Simula's own documents use the word is unverified.

Conniver (McDermott and Sussman, 1972 to 1974) had a named pair for "yield and stay alive" against "yield and finish".
The Sather authors describe it: a generator "yields new values and has the option of maintaining its state ('AU_REVOIR') or of quitting ('ADIEU'), similar to the yield and quit statements in Sather" ([Murer et al. 1995, section 4.1](https://steveomohundro.com/wp-content/uploads/2009/03/murer_omohundro95_iteration_abstraction_in_sather.pdf)).
No source in the notes says CLU drew on Conniver.

### Alphard to CLU is stated, and CLU's contribution is the `yield` statement

The first link in the modern chain has a first-person statement and dates.
Liskov writes: "Iterators were inspired by a construct in Alphard called a 'generator' [Shaw, 1976; Shaw, 1977]. We first learned about this in the summer of 1975 when we visited the Alphard group at CMU. We were intrigued by generators since they solved some problems with data abstractions, but we thought they were too complicated. Russ Atkinson designed iterators on the airplane going back to Boston after this meeting and described them in a design note in September 1975" ([A History of CLU, section 3.10](https://www.cs.tufts.edu/~nr/cs257/archive/barbara-liskov/clu-history.pdf)).
By her account an Alphard generator was "a group of operations" that a `for` statement calls, and a CLU iterator is "a single operation that yields its results incrementally".
**The suspending routine with a `yield` statement is therefore CLU's, and the object with start, next, and done operations is Alphard's.**
That CLU introduced the keyword is an inference, and a safe one: every source the researchers read that mentions the word traces it to CLU, and none says "CLU introduced `yield`" in so many words.
Atkinson's 1975 design note was not found, so whether it already used the word is unverified.
The Alphard papers were not read in full (the report is snippet only, and Alphard "was never implemented" per Wikipedia), so the description of Alphard is Liskov's.

CLU also fixed two properties that later designs argued with.
An iterator runs only in a `for` statement, one per loop, because "we limited the expressive power of the mechanism so that we could implement it using a single stack".
And the loop's exit ends the iterator: "if the loop body causes the loop to terminate, the iterator terminates" ([A History of CLU, sections 3 and 3.10](https://www.cs.tufts.edu/~nr/cs257/archive/barbara-liskov/clu-history.pdf)).
That sentence is the earliest finalization rule in this lineage.

### Icon is a parallel line, and Sather credits CLU

Icon's generators come from SNOBOL4 and SL5, by the designers' account, and the 1981 paper cites CLU and Alphard only to contrast them: "In each of these languages, generators are only accessible in a specific context: a particular type of for statement" ([Generators in Icon, section 5](https://drh.github.io/documents/generators-in-icon.pdf)).
Icon's `suspend e` "is similar to `return e`, except that the procedure activation is left in suspension so that it may be resumed", and "The result of the suspend expression itself is the null value", so nothing travels in.
Three Icon features matter for the per-feature lineage.
`suspend e` produces every result of `e`, which makes `suspend walk(t.ltree | t.rtree)` a delegation to a sub-generator, in print in April 1981.
`return e` ends a procedure with a final value.
And co-expressions (Wampler and Griswold, 1982 to 1983) add first-class resumable expressions, with `expr @ x` transmitting a value into co-expression `x`.
The transmission semantics are snippet only (the technical report returned a 404), though Object Icon's documentation confirms `val@ce` in a descendant ([Object Icon](https://objecticon.sourceforge.net/Coexpressions.html)).
Griswold's HOPL II history of Icon was not retrieved, so Icon's internal dating is incomplete.

Sather's credit is explicit: "The name 'iterator' and the initial design were derived from the iterator construct in the CLU language" ([Murer et al. 1995, section 1](https://steveomohundro.com/wp-content/uploads/2009/03/murer_omohundro95_iteration_abstraction_in_sather.pdf)).
Sather removed three CLU limits and added "hot" arguments, "which are reevaluated each time the control is passed back to the iterator", so that an iterator can "'consume' a sequence of values".
That is the first `yield`-style routine in the notes that receives a new value from its consumer at each resumption, through its parameter and not through the `yield`.
Sather also has `quit`, which ends the calling loop, and it bans `yield` inside a `protect` statement, an early form of Python's 2001 ban on `yield` in `try`/`finally`.
The year iterators entered Sather 1 (1993 or 1994, from memory) was not confirmed.

Lua's designers and de Moura and Ierusalimschy's classification place these designs on three axes.
CLU and Sather iterators and Icon generators are constrained constructs, and the Python generator of 2001 is first-class and not stackful: "it can only suspend its execution when its control stack is at the same level that it was at creation time" ([Revisiting Coroutines, section 2.3](https://www.cs.tufts.edu/~nr/cs257/archive/roberto-ierusalimschy/revisiting-coroutines.pdf)).
The same passage names the cost that delegation syntax later addresses: "it is necessary to create a hierarchy of auxiliary generators that yield in succession until the original invocation point is reached."

## 2001 to 2016: Python cites three languages once, then builds each feature from its own PEPs

### `yield`: Sather, CLU, and Icon are credited for the idea

PEP 255 (created 18 May 2001, Python 2.2, released 21 December 2001) has one crediting sentence: "Some other high-level languages provide pleasant solutions, notably iterators in Sather [2]_, which were inspired by iterators in CLU; and generators in Icon [3]_, a novel language where every expression *is a generator*" ([PEP 255](https://peps.python.org/pep-0255/)).
Its references are the Sather paper, the Icon site, and Stackless.
CLU has no reference of its own.
The PEP credits an idea ("a kind of function that can return an intermediate result ... but maintaining the function's local state") and not a syntax.
Who proposed the word `yield`, and whether it was taken from CLU and Sather, is not confirmed in any primary source the researchers read; the 2001 mailing-list threads were not read for that question.
Later outside writers go further than the PEP: Russ Cox wrote in 2023 that "Python's generators appear to be almost exactly copied from CLU" ([Cox, "Coroutines for Go"](https://research.swtch.com/coro)), which is his reading and not a Python designer's statement.
A.M. Kuchling's "What's New in Python 2.2" credits Icon alone ("especially Icon") and states the one novelty: "a generator's state is represented as a concrete object (the iterator) that can be passed around" ([What's New in Python 2.2](https://docs.python.org/3/whatsnew/2.2.html)).
PEP 255 also positions generators as "a useful subset of Stackless functionality", and PEP 219 and PEP 220, the Stackless proposals of August 2000, are Deferred and Rejected.

### Generator expressions: Haskell is credited one step back

PEP 289 (Raymond Hettinger, created 30 January 2002, Python 2.4) names no other language; the researchers searched its source for "haskell" and found nothing ([PEP 289](https://peps.python.org/pep-0289/)).
It calls generator expressions a "generalization of list comprehensions".
The foreign credit sits in "What's New in Python 2.0": "The idea of list comprehensions originally comes from the functional programming language Haskell" ([What's New in Python 2.0](https://docs.python.org/3/whatsnew/2.0.html)).
The same note records that Greg Ewing wrote the first list-comprehension patch, nine years before he wrote PEP 380.
An assumption that PEP 289 was rejected and revived has no primary text behind it; the current PEP says only "ACCEPTED", and an earlier rejection notice is from memory.

### Send, throw, and close: PEP 288, PEP 325, and Ruby's look

PEP 342 (Guido van Rossum and Phillip J. Eby, created 10 May 2005, Python 2.5) states its sources itself.
It is "basically a combination of ideas from" two PEPs: from PEP 288, "generator exceptions (in fact the ``throw()`` method name was taken from :pep:`288`)" and "a concept from an earlier revision of :pep:`288`, the *yield expression*", and from PEP 325, the `close()` method and finalization ([PEP 342](https://peps.python.org/pep-0342/)).
Its acknowledgements say "Raymond Hettinger (:pep:`288`) and Samuele Pedroni (:pep:`325`) first formally proposed the ideas of communicating values or exceptions into generators, and the ability to close generators."
The earlier revision of PEP 288 that held the yield expression was not located.
`send()` was named in PEP 342 (Oren Tirosh's `feed()` was declined), and `GeneratorExit` is new there.
The only language PEP 342 names is Ruby: "the syntactic extensions to yield make its use very similar to that in Ruby. This is intentional", with the caveat that "Blocks in Python are not compiled into thunks".
The PEP's own editorial note says the passage "seems out of place now", so the Ruby credit is for the look of `yield` as an expression in a block protocol, a remnant of PEP 340.
PEP 342 does not mention Icon co-expressions, Sather's hot arguments, Conniver, or Lua, whose `resume` and `yield` had exchanged values in both directions since Lua 5.0 in April 2003 ([Lua version history](https://lua.org/versions.html)).
Any link from those designs to `send()` is therefore a resemblance and not a documented lineage.
The proximate cause of the 2005 timing is the `with` statement: PEP 343 says "With :pep:`342` accepted, it is possible to write a decorator", and What's New 2.5 says generators with `try...finally` are "actually necessary in order to implement the `with` statement" ([PEP 343](https://peps.python.org/pep-0343/); [What's New in Python 2.5](https://docs.python.org/3/whatsnew/2.5.html)).

### Return values and `yield from`: no foreign citation at all

PEP 255 had noticed the return value in 2001 and deferred it: "In Icon, ``return expr`` means both "I'm done", and "but I have one final useful value to return too, and this is it". At the start, and in the absence of compelling uses for ``return expr``, it's simply cleaner to use ``yield`` exclusively for delivering values" ([PEP 255](https://peps.python.org/pep-0255/)).
PEP 380 supplied the use in 2009 (lightweight threads whose helpers return results) without citing Icon.
Between the two, frameworks worked around the gap: Twisted's `inlineCallbacks` (announced 16 February 2007, "requires Python 2.5") needed a `returnValue()` helper, a detail that is snippet only ([twisted-python 2007](https://twisted.org/pipermail/twisted-python/2007-February/014869.html)).
The next section takes delegation in full.

### async/await and async generators: Python credits C# and its own PEP 380

PEP 492 (Yury Selivanov, created 9 April 2015, accepted 5 May 2015, Python 3.5) is the first PEP in this line to credit other languages as a group: "async/await is not a new concept in programming languages: * C# has it since long time ago [5]_; * proposal to add async/await in ECMAScript 7 [2]_; see also Traceur project [9]_; * Facebook's Hack/HHVM [6]_; * Google's Dart language [7]_; * Scala [8]_; * proposal to add async/await to C++ [10]_" ([PEP 492](https://peps.python.org/pep-0492/)).
The mechanism is inherited, not borrowed.
PEP 492 says `await` "uses the `yield from` implementation with an extra step of validating its argument", and Van Rossum wrote on 24 April 2015, rejecting Ewing's competing PEP 3152: "We must see `await` as a refinement of `yield from`, not as an alternative" ([python-dev 2015-April/139503](https://mail.python.org/pipermail/python-dev/2015-April/139503.html)).
PEP 525 (async generators, Python 3.6, released 23 December 2016) cites only PEP 255, and it drops `yield from` inside async generators because "it would require a serious redesign of the generators implementation" ([PEP 525](https://peps.python.org/pep-0525/)).
PEP 492 does not say which language's design `async for` and `async with` followed.
One path by which C# experience reached Python earlier is circumstantial: PEP 3156 (asyncio, 2012) thanks Steve Dower and Dino Viehland and lists Dower's "wattle" counter-proposal among its influences, and their Microsoft affiliation is from memory ([PEP 3156](https://peps.python.org/pep-3156/)).

## Delegation is older than `yield from`, and the two-way form is Python's

### Four one-way forms precede PEP 380

The research notes correct the common account that PEP 380 invented delegation.
Icon's `suspend expr` (1981) re-suspends every result of a generator expression and forwards values outward only.
Sather writes delegation as a loop, `loop yield left.inorder! end` ([Murer et al. 1995, figure 2](https://steveomohundro.com/wp-content/uploads/2009/03/murer_omohundro95_iteration_abstraction_in_sather.pdf)).
The documented chain to a dedicated construct starts at Microsoft Research.
Cω (Bierman, Meijer, Schulte, ECOOP 2005) has no keyword: its type system flattens streams, so `yield return FromTo2(b+1,e)` inside a stream method is delegation, and the paper names XPath and XQuery sequences as the model ("Cω streams thus coincide with XPath/XQuery sequences which are also flattened") ([Bierman, Meijer, Schulte 2005](https://gavinbierman.github.io/assets/pdf/ecoop2005-corrected.pdf)).
Jacobs, Meijer, Piessens, and Schulte (FTfJP, May 2005) then proposed `yield foreach expr;` with a linear-time implementation, and stated the link: "Our newly proposed nested iterators, which follow the design of streams in Cω [4], simplify programming of recursive iterators" ([Jacobs et al. 2005](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/specsharp-iterators.pdf)).
Meijer and Schulte are authors of both papers.
F#'s `yield!` arrived with sequence and computation expressions in 2007, and its builder method is named `YieldFrom` ([Syme, HOPL 2020](https://fsharp.org/history/hopl-final/hopl-fsharp.pdf)).
The point release that introduced `yield!` is unconfirmed, and so is whether the method name `YieldFrom` predates Python's keyword, so no direction of influence between F# and Python can be asserted.
Lua needs no delegation at all, because any function called from a stackful coroutine can yield.

### The quadratic cost was stated in the C# world in 2004

The performance argument for delegation has a clear order of statement.
Stephen Toub wrote on 29 October 2004: "As Grant has previously pointed out, the above code will produce O(N) iterator objects", with links whose paths date Grant Richins's posts to 24 March and 8 April 2004, and Toub measured the per-item walk up the chain as "approximately O(N log N)" ([Toub 2004](https://learn.microsoft.com/en-us/archive/blogs/toub/recursive-iterator-performance)).
The researchers did not open Richins's posts; their dates come from those URL paths and their titles ("Recursive iterators (aka perf killers)") from the Jacobs bibliography.
The word "quadratic" appears in the two 2005 papers: Cω says that without flattening "we would be forced to copy the stream produced by the recursive invocation, leading to a quadratic instead of a linear number of yields".
Wes Dyer's post of 23 March 2007 credits the Jacobs paper by name under the heading "One Possibility for Language Improvement (not in Orcas)", so it is a popularization and not the first statement ([Dyer 2007](https://learn.microsoft.com/en-us/archive/blogs/wesdyer/all-about-iterators)).
Ewing's first proto-PEP message of February 2009 says the re-yielding chain "can cause what ought to be an O(n) operation to become O(n**2)", with no citation ([python-ideas thread](https://mail.python.org/archives/list/python-ideas@python.org/thread/QYKLE5SBGTV2ZEA3LD3GL7GOXMUL57DL)).
Independent rediscovery is the simplest reading, and it is an inference.
An earlier complexity statement in the Sather papers remains possible; the notes hold only a sentence about "the optimization of recursive iters".

### PEP 380 adds forwarding and a result, and cites only Python

Ewing posted "Proto-PEP on a 'yield from' statement" to python-ideas on 12 or 13 February 2009 (the two researchers' notes differ by a day), and the PEP is dated 13 February 2009 ([python-ideas 2009-February/002883](https://mail.python.org/pipermail/python-ideas/2009-February/002883.html)).
The motive is refactoring: "A Python generator is a form of coroutine, but has the limitation that it can only yield to its immediate caller" ([PEP 380](https://peps.python.org/pep-0380/)).
The only precedent the PEP names is Python's own: "Proposals along similar lines have been made before, some using the syntax `yield *` instead of `yield from`", and "previous proposals have focused only on yielding values".
Those earlier `yield *` proposals were not located.
The researchers found no citation of C#, F#, Icon, or Cω in the PEP or in the messages they read, but they read the opening message and a few replies, not the whole February to April 2009 traffic.
"Nobody cited another language" is therefore unverified until the full archive is read.
**What is new in PEP 380 is the two-way half**: `send()`, `throw()`, and `close()` pass through to the subgenerator, and the subgenerator's `return` value becomes the value of the `yield from` expression.
None of the earlier constructs had an inbound channel to forward.
`throw()` and `close()` forwarding entered after Bruce Frederiksen's review; Ewing replied on 13 February 2009, "I'd forgotten about that feature!" ([python-ideas 2009-February/002892](https://mail.python.org/pipermail/python-ideas/2009-February/002892.html)).
Van Rossum's first reaction to the return value was hostile ("I really don't like overloading return this way", 17 February 2009), and he accepted the PEP on 25 or 26 June 2011 ("PEP 380 is pretty much approved") ([python-ideas 2009-February/002951](https://mail.python.org/pipermail/python-ideas/2009-February/002951.html); [python-dev 2011-June/112010](https://mail.python.org/pipermail/python-dev/2011-June/112010.html)).
Python 3.3 shipped it on 29 September 2012 ([What's New in Python 3.3](https://docs.python.org/3/whatsnew/3.3.html)).

### The spread from PEP 380 is stated for JavaScript and PHP, and inferred for Dart

| Date | Design | Construct | Precedent named | Status of the link |
|---|---|---|---|---|
| April 1981 | Icon | `suspend expr` | none (follows from goal-directed evaluation) | origin, read in the 1981 paper |
| 2005 | Cω | `yield return` of a stream | XPath/XQuery sequences | stated |
| May 2005 | Jacobs et al. | `yield foreach` | Cω | stated |
| 2007 | F# | `yield!` | Haskell comprehensions and monads, for computation expressions in general | stated for the general design, not for `yield!` |
| Feb 2009 | Python PEP 380 | `yield from` | earlier Python `yield *` proposals | stated; no foreign citation found |
| May 2012 | ES6 | `yield*` | PEP 380 | stated by Eich |
| March 2015 | PHP 7.0 | `yield from` | Python 3.3 and ES6 | stated in the RFC |
| March 2015 | Dart 1.9 | `yield*` | none found | inferred from spelling and timing |
| 2017 | Kotlin 1.1 | `yieldAll()` | C# and Python for `yield` in general | no citation for delegation |
| 2021 to 2022 | C++23 | `co_yield ranges::elements_of(g)` | cppcoro `recursive_generator` | stated; no other language named |
| Oct 2023 | Rust RFC 3513 | none, future work | "Python has the ability to `yield from` an iterator" | stated |

For JavaScript, Brendan Eich wrote on es-discuss on 10 May 2012: "PEP-380 is the basis", and "The * means to exhaust the yield operand's value, otherwise you're just yielding that value" ([es-discuss, "Recursion in generators?"](https://esdiscuss.org/topic/recursion-in-generators)).
In September 2013 he defended generator return values with a link to PEP 380 ("We deliberated long and hard, after going through a design state without return expr;"), and in January 2014 he wrote "PEP-380 is worth a read, IMHO, for anyone who values Python's experience" ([es-discuss, return value thread](https://esdiscuss.org/topic/proposal-generator-returning-a-value-should-throw-syntaxerror)).
The Harmony generators proposal page itself could not be fetched, so whether its own text cites PEP 380 is unverified, and Dave Herman's authorship date is from the brief.
A Mozilla bug sentence, "Harmony is extending generators to allow them to return values, similarly to Python's PEP 380", is snippet only, and its bug number (666404) is the researcher's best match.
ES6's star matches the spelling PEP 380 rejected; no source says TC39 took it from the older Python proposals.

For PHP, the Generator Delegation RFC (Daniel Lowrey, version 0.2.0 dated 1 March 2015, vote 25 to 0) says "Python 3.3 generators support the `yield from` syntax" and "Javascript ES6 generators support the `yield*` syntax", argues that "Sharing common vernacular for similar features lowers cognitive barriers", and records that "The original version of this RFC proposed a `yield *` syntax", dropped because `*` "would break backwards compatibility" ([PHP RFC: Generator Delegation](https://wiki.php.net/rfc/generator-delegation)).
PHP took the whole PEP 380 package, forwarding and return value.

C++23 converged on the 2005 implementation idea (a stack of frames, with the consumer resuming the leaf) and cites only its own library line: "Earlier works in [CppCoro] implemented this feature in a distinct recursive_generator type" ([P2502R2](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2502r2.pdf)).
Its delegation forwards values only, and the expression has type void.
C# itself never shipped the construct its research group designed.
Lippert wrote in a comment on his 13 July 2009 post that "'yield foreach' is an awesome feature that I would love to do; it is certainly in the top fifty, but has never made it into the top ten" ([Lippert 2009](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-two-why-no-ref-or-out-parameters)).
Matt Warren's gist says "Eric Meijer did a lot of thinking about this problem back during the development of C# 3.0" and that the code-generator change "was the major stumbling block" ([Warren gist](https://gist.github.com/mattwar/8660692f56c2a15478fbbfd557934a06)).
Cyrus Najmabadi of the design team wrote in csharplang discussion 5303 as late as 19 May 2025: "We're not going to add a language feature just to have it immediately warn you the moment you use it" ([csharplang discussion 5303](https://github.com/dotnet/csharplang/discussions/5303)).
The status as of late 2026 rests on that last comment.

## Outward from Python, and back in through async/await

### JavaScript 1.7 and PHP 5.5 copy Python by name

Brendan Eich's post of 19 February 2006 says he was "infusing JS with Pythonic generators and iterators, including array comprehensions", asks "Why borrow from Python for iteration, generators, and comprehensions?", and answers "we would rather follow than lead" ([Eich 2006](https://brendaneich.com/2006/02/python-and-javascript/)).
The fetch tool returned those sentences as fragments, so reread the post before quoting it at length.
Legacy generators in Firefox 2 had `next`, `send`, `throw`, and `close`, ended by a `StopIteration` exception; that method list and the `TypeError` on sending a value to a newborn generator are snippet only.
Dave Herman confirmed two of the borrowings in a Mozilla bug the researchers read: `StopIteration` "was the original Python design and the original ES4 design as well", and "As in Python (see PEP-255), disallow return v; in generators" ([Mozilla bug 666399](https://bugzilla.mozilla.org/show_bug.cgi?id=666399)).
Eich's post predates Python 2.5's release, so JavaScript 1.7 copied the PEP 342 design while it was in development; the release dates in that comparison are from memory, and the 2006 post names no PEP number.

ES6 kept the semantics and changed the surface.
`function*` marks the generator, the protocol returns `{value, done}` objects in place of throwing `StopIteration` (a change Andy Wingo dates to TC39 discussions in March 2013), `send()` folded into `next(value)`, and `close()` became `return(value)` ([Wingo 2013](https://www.wingolog.org/archives/2013/05/08/generators-in-v8)).
The removal of `send()` and `close()` is snippet only.
Comprehensions went the other way: array and generator comprehensions, "a well-loved feature of Python" in Kevin Smith's words, were deferred in June 2014 and cut from the draft, and Eich summarized that "'defer' or 'cut' ... won" ([es-discuss, "Comprehensions, Where Art Thou?"](https://esdiscuss.org/topic/comprehensions-where-art-thou)).
The removal in draft revision 27 (August 2014) is snippet only.

Nikita Popov's PHP Generators RFC (5 June 2012, vote 24 to 1) lists PEPs 255, 289, 342, 380, and 3152 first among its resources and shipped `send()` and `throw()` in the first version ([PHP RFC: Generators](https://wiki.php.net/rfc/generators)).
It also records a deliberate departure: "coroutines do not have to be primed with a `next()` call before they can be used", which "is required in Python".
The 2015 Generator Return Expressions RFC (Daniel Lowrey, vote 33 to 0) cites "Python 3.3 added the ability to return expressions in sub-generators" and ES6's `{value, done}` ([PHP RFC: Generator Return Expressions](https://wiki.php.net/rfc/generator-return-expressions)).
PHP 5.5 has no `close()` method, and destruction of a generator runs its `finally` blocks.
The release versions' dates (PHP 5.5.0 in 2013, 7.0.0 in December 2015) are unverified.

### C# iterators and Ruby blocks have no designer's credit to CLU in the notes

C# 2.0 iterators (2005) are pull-only, compiled to a state-machine class, with `Dispose()` running pending `finally` blocks as the counterpart of `close()`.
Eric Lippert described the scope: "We decided that the sweet spot for the high-level scenario-driven design of the feature was iterators over collections", and coroutine uses "certainly did not drive the design of the feature" ([Lippert, "Iterator Blocks, Part One"](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-one)).
The two-word `yield return` is a compatibility device: Eric Gunnerson wrote that it "meant that C# 2.0 would compile all C# code without change" ([Gunnerson 2006](https://learn.microsoft.com/en-us/archive/blogs/ericgu/why-yield-return-rather-than-yield)).
**The researchers found no sentence from Hejlsberg or another C# 2.0 designer crediting CLU, Icon, Sather, or Python.**
The claim that C# iterators descend from CLU is common in secondary sources (a 2017 MSDN Magazine column, snippet only) and stays ungrounded.

Ruby's `yield` calls the caller's block, which is CLU-style internal iteration.
Matz wrote on ruby-list on 30 January 1996 that the idea is not unique to Ruby and that CLU has it too ([ruby-list:102](https://blade.ruby-lang.org/ruby-list/102)).
That post says CLU has iterators, not that Ruby took them from CLU.
The stronger statement ("He got the idea from a 1970s language called CLU") is a blogger's paraphrase of a 2019 talk ([AppFolio 2019](https://engineering.appfolio.com/appfolio-engineering/2019/7/3/rubys-roots-and-matzs-leadership)).
External, generator-style iteration arrived with Fibers and `Enumerator#next` in Ruby 1.9 ([NEWS for Ruby 1.9.1](https://docs.ruby-lang.org/en/3.0/NEWS-1_9_1.html)).
Go is the one modern design that states a CLU credit outright: "Like many ideas in programming, iterators date back to Barbara Liskov's CLU language" ([Go blog 2024](https://go.dev/blog/range-functions)).

### Lua, Kotlin, C++, and Rust cite their sources in design documents

Lua 5.0 (11 April 2003) took the coroutine branch.
Its designers credit Scheme ("always a source of inspiration to us"), Thatcher Ulrich's December 2001 patch, and Grim Fandango's cooperative multitasking, and they call Python's 2001 generators "a restricted form of coroutines" ([The Evolution of Lua](https://www.lua.org/doc/hopl.pdf); [Coroutines in Lua](https://www.lua.org/doc/jucs04.pdf)).
`coroutine.close` arrived in Lua 5.4 in 2020.
Kotlin's design document cites `yield` "in C#, Python", async/await "in C#, JS and other languages", Go for channels, and Haskell for lazy lists, and it makes generators and `yieldAll` library functions over general suspension ([KEEP coroutines](https://github.com/Kotlin/KEEP/blob/master/proposals/coroutines.md)).
The C++ proposals cite "languages like C# and Python" for generator functions (N3858, January 2014) and PEP 289 for generator expressions (N4134, October 2014) ([N3858](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n3858.pdf); [N4134](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2014/n4134.pdf)).
Rust's RFC 3513 (October 2023) traces the idea to "the Alphard language from circa 1975", "later refined into the idea of iterators in the CLU language", and Icon, and its `gen` blocks were still unstable when the tracking issue was read on 2026-11-11 ([RFC 3513](https://rust-lang.github.io/rfcs/3513-gen-blocks.html); [rust-lang/rust#117078](https://github.com/rust-lang/rust/issues/117078)).
Dart 1.9 (March 2015) shipped `sync*`, `async*`, `yield`, and `yield*` together and its announcement credits no language; the design paper by Meijer, Millikin, and Bracha could not be fetched ([Dart 1.9 announcement](https://news.dartlang.org/2015/03/dart-19-release-youve-been-await-ing-for.html)).
That Dart was first to ship sync generators, async functions, and async generators in one release is a researcher's inference from dates, and Hack's async generators have an unverified date that could be earlier.

### async/await: F# to C# is the F# authors' claim, and C# to Python is stated

Don Syme dates `async { ... }` to 2007 (announced 10 October 2007) and credits Haskell's monadic syntax, the OCaml community, Scala's `react`, and C# 2.0 iterators, which "featured an implicit inversion of control-flow" ([Syme, HOPL 2020](https://fsharp.org/history/hopl-final/hopl-fsharp.pdf)).
He claims the reverse influence too: "This would still be influencing C# years later, in C# 5.0 (async/await) and 8.0 (async sequences), and in turn influence many other languages."
A 2011 paper's sentence that "an adapted version of this approach has recently been announced for a future version of C#" is snippet only, and the researchers retrieved no first-person credit to F# from a C# designer.
C# to Python is stated in PEP 492, and C# to TypeScript in TypeScript's 2015 proposal (snippet only).
**C# to ECMAScript async functions is common attribution with no TC39 sentence found.**
JavaScript and Python reached `await` through generators that already had an inbound channel (task.js and co, then `yield from` and asyncio), while C# reused the iterator state-machine rewrite; the claim about how task.js and co use `yield*` is from general knowledge.
Async generators follow in Python 3.6 (2016), ES2018 (which keeps `yield*` inside async generators, where Python's PEP 525 omits `yield from`), and C# 8 (2019, ship date not opened) ([tc39/proposal-async-iteration](https://github.com/tc39/proposal-async-iteration)).

## The lineage per feature, with the status of each link

| Feature | Earliest form in the notes | Enters Python | Documented borrowers | Links that are inferred or unverified |
|---|---|---|---|---|
| `yield` construct | CLU, September 1975, after Alphard (stated by Liskov); Icon `suspend`, 1981, a parallel line | PEP 255, 2001; credits Sather, CLU via Sather, Icon (stated) | JS 1.7 (Eich, stated); PHP 5.5 (stated); C++ N3858, Kotlin, Rust RFCs (stated surveys); Go credits CLU (stated) | who chose the word `yield` for Python; CLU to C# 2.0; CLU to Ruby (weak) |
| Two-way send | Conniver's message to a resumed generator, 1972; Icon co-expression `@`, 1982 (snippet only); Sather hot arguments; Lua 5.0, 2003 | PEP 342, 2005; credits PEP 288's yield expression and Ruby's look (stated) | JS 1.7 `send()` (snippet only); ES6 `next(value)`; PHP 5.5 `send()` (stated) | any link from Conniver, Icon, Sather, or Lua to `send()` |
| Exception injection | none found before Python | PEP 288 (2002, Withdrawn) names `throw()`; PEP 342 specifies it (stated) | JS 1.7 and ES6 `throw()`; PHP 5.5 `throw()` (stated) | Ruby `Fiber#raise`, 2.7 (unverified); Lua has no `throw` (unverified) |
| Close and finalization | CLU: loop exit terminates the iterator; Sather `quit` | PEP 325 (2003, Rejected in favor of 342); PEP 342 `close()` and `GeneratorExit`; PEP 533 Deferred | JS 1.7 `close()` (snippet only); ES6 `return(value)`; C# `Dispose()` runs `finally`; Lua 5.4 `coroutine.close` | C# and Lua forms have no stated source |
| Return value | Icon `return e`, 1981 | noted and deferred in PEP 255; PEP 380, 2009 | ES6 (Eich cites PEP 380, stated); PHP 7.0 (cites Python 3.3 and ES6, stated) | Icon to PEP 380 (PEP 380 does not cite Icon) |
| Delegation | Icon `suspend expr`, 1981; Cω and `yield foreach`, 2005; F# `yield!`, 2007 | PEP 380, 2009, shipped 2012; cites only Python proposals | ES6 `yield*` (stated); PHP 7.0 (stated); Rust lists it as future work (stated) | Dart `yield*` from JS; F# and Python in either direction; Kotlin `yieldAll` |
| Generator expressions | Haskell list comprehensions, credited for Python 2.0 list comprehensions | PEP 289, Python 2.4; no language named | JS 1.7 comprehensions (Eich, stated), cut from ES6 in 2014; C++ N4134 cites PEP 289 (stated) | JS 1.8 generator expressions (from memory); Julia's version (unverified) |
| async/await | F# async workflows, 2007; C# 5, 2012 | PEP 492, 2015; credits C# first (stated); `await` refines `yield from` (stated) | TypeScript cites C# 5 (snippet only); Rust RFC 2033 cites C#, JS, Python (stated) | F# to C# (F# authors' claim; no C# designer's statement found); C# to ECMAScript |
| Async generators | Dart 1.9, March 2015 (first located with a firm date) | PEP 525, 2016; cites only PEP 255 | ES2018; C# 8, 2019 | priority among Dart, Hack, and F# libraries (unverified dates) |

Exception injection is the rarest feature outside Python and JavaScript; PHP 5.5 is the only verified case in the survey of other languages.
Every design after 2005 that calls itself a generator or sequence builder (F#, Dart, Kotlin, C++23 `std::generator`, Rust `gen` blocks) left the inbound channel out, and two-way transfer elsewhere appears only where a general coroutine sits underneath (Lua, Ruby Fibers, Rust's unstable `Coroutine` trait).

## Conclusion

The record splits generator features into two kinds.
The outbound half (a routine that suspends and hands out a value, and the delegation that flattens one such routine into another) was invented several times, in CLU, Icon, Cω, and F#, with a citation trail only inside each family.
The inbound half (`send`, `throw`, `close`, a return value, and delegation that forwards all four) has one origin, Python between 2002 and 2009, and it spread only by explicit copying, to JavaScript and PHP.
That asymmetry explains why `yield from` reads as a Python invention: the spelling and the coroutine-call semantics are Python's, and the flattening is older by 28 years.
It also suggests which features were needed and which were chosen. Languages that wanted lazy sequences rebuilt one-way generators on their own, and languages that wanted coroutines either started from a general mechanism (Lua, Kotlin) or adopted async/await, the one feature Python took from others.

For a chapter that states this history, the safe sentences are the ones with a designer's quotation behind them: Alphard to CLU, CLU to Sather, Sather and Icon to Python, Python to JavaScript and PHP, PEP 380 to `yield*`, and C# to Python's `await`.
The sentences to hold back or qualify are the ones the notes could not ground: the 1958 coinage of "coroutine", who chose the word `yield` for Python, CLU as the source of C# iterators and Ruby blocks, and C# as the source of JavaScript's async functions.
Four sources would settle most of them: Knuth's history note, Griswold's HOPL II paper on Icon, the archived Harmony generators proposal, and "JavaScript: The First 20 Years".
