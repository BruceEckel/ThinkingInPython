# History of generators in C# and JavaScript, and what each took from other languages

Reading note: each finding is marked **[read]** when I opened the page and saw the text, or **[snippet]** when I saw only a search-result summary of it.
A [snippet] quotation may be paraphrased by the search tool and should be rechecked before it is printed as a quotation.
web.archive.org and stackoverflow.com could not be fetched in this session, which blocked the archived Harmony wiki and Eric Lippert's Stack Overflow answers.

## C# 2.0 iterators: influences, the `yield return` spelling, and the implementation

### Takeaway
C# 2.0 iterators (shipped 2005) are a deliberately narrow feature: the compiler rewrites an iterator block into a state-machine class, and the team chose "iterators over collections" over general coroutines.
The two-word `yield return` exists so that `yield` could be a contextual keyword and every C# 1 program would still compile.
I found no primary-source sentence from a C# designer crediting CLU, Icon, Python, or Sather.

### Cited Findings
- **[read]** Eric Gunnerson (C# team), 2006-03-08: early builds used a bare `yield`. "In the first version of iterators, you would use "yield" when you wanted to "return" a iterator value back." The team had expected generics to need new reserved words and planned a source-fixing tool. Generics ended up needing none, and "This meant that the only new keyword in 2.0 was "yield", and switching to yield return meant that C# 2.0 would compile all C# code without change." Source: [Eric Gu, "Why 'yield return' rather than 'yield'?"](https://learn.microsoft.com/en-us/archive/blogs/ericgu/why-yield-return-rather-than-yield)
- **[read]** Eric Lippert, 2009-07-09, on scope: "Our iterator blocks can be seen as a weak kind of coroutine. We could have chosen to implement full coroutines and just made iterator blocks a special case of coroutines. And of course, coroutines are in turn less general than first-class continuations; we could have implemented continuations, implemented coroutines in terms of continuations, and iterators in terms of coroutines. But we didn't. We decided that the sweet spot for the high-level scenario-driven design of the feature was iterators over collections, and so we concentrated on that." Source: [Lippert, "Iterator Blocks, Part One"](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-one)
- **[read]** Same post, on coroutine use: "Some adventurous people use the fact that iterators are "poor-man's coroutines" as a shortcut to building coroutine-like systems that have only a tenuous connection to the semantics of iterating over the items in a collection, but those are the exception, not the rule. Their scenarios certainly did not drive the design of the feature." Source: [Lippert, "Iterator Blocks, Part One"](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-one)
- **[read]** Implementation, Wes Dyer (C# compiler team), 2007-03-23: the compiler turns the method into a nested sealed class that implements both `IEnumerable<T>` and `IEnumerator<T>`, with an `int state` field, a `current` field, and the locals hoisted to fields. `MoveNext()` is a `switch (state)`: "It looks like a state machine and indeed it is." State -2 means "I'm an IEnumerable", 0 means initialized, -1 means finished. `Reset()` throws a `NotSupportedException`. Calling the iterator method runs none of the body ("iterators are an example of deferred execution"). Source: [Wes Dyer, "All About Iterators"](https://learn.microsoft.com/en-us/archive/blogs/wesdyer/all-about-iterators)
- **[snippet]** Mono had an iterator implementation by April 2003. Miguel de Icaza's 2003-04-22 post reports it and remarks that "the lisp, scheme, icon people probably have better examples" of the idea. This dates the public design to early 2003 at the latest, and it is a remark by an implementer outside Microsoft, not a design credit. Source: [de Icaza blog, 2003-04-22](https://tirania.org/blog/archive/2003/Apr-22.html)
- **[snippet]** A 2017 MSDN Magazine column (Mark Michaelis) says the CLU language "offered many insights into the iterator construct". Secondary, and not a statement by the 2.0 designers. Source: [MSDN Magazine, June 2017](https://learn.microsoft.com/en-us/archive/msdn-magazine/2017/june/essential-net-custom-iterators-with-yield)

### Inferences
- The `yield return` / `yield break` pairing is a compatibility device, not a borrowed syntax: each contextual word is followed by an existing reserved word, so no C# 1 program could have contained the sequence.
- The state-machine rewrite (no CLR support needed) is the reason for most of the restrictions Lippert's series lists (no `ref`/`out` parameters, no `yield` in `finally`, no unsafe code): locals become fields of a heap object.

### Gaps
- No primary source found in which Hejlsberg or another C# 2.0 designer credits CLU, Icon, Sather, or Python. The Artima Hejlsberg interviews (2003) did not surface in searches. The claim "C# iterators descend from CLU" is common in secondary literature and I could not ground it in a designer's sentence.
- The 2002 announcement date (Hejlsberg's OOPSLA 2002 talk on generics, iterators, anonymous methods, partial types) and the 2003 "C# 2.0 specification" document are from memory and were not confirmed in this session.
- ECMA-334 clause text for iterators was not opened.

## Did C# ever get delegation? The `yield foreach` thread

### Takeaway
No. A delegating form was specified in a 2005 Microsoft Research paper, described publicly by the compiler team in 2007 as "not in Orcas", considered again in the C# 3.0 period, and is still an open community request under several spellings. The stated reason it lost is priority, not a design objection.

### Cited Findings
- **[read]** Wes Dyer, 2007-03-23, shows the cost: composing `Concat` iterators n deep makes enumeration quadratic. "Essentially, composing concats together like this causes O(m^2) yield returns to be executed." A recursive tree walk written with nested `foreach ... yield return` has the same problem. Source: [Wes Dyer, "All About Iterators"](https://learn.microsoft.com/en-us/archive/blogs/wesdyer/all-about-iterators)
- **[read]** Same post, section headed "One Possibility for Language Improvement (not in Orcas)": "Bart Jacobs, Erik Meijer, Frank Piessens, and Wolfram Shulte wrote a very interesting paper on a possible language improvement that would improve both the usability and the performance of iterators. The second half of the paper details what they call nested iterators which avoid the multiple evaluation problem of the composed Concats and implicitly keep an internal stack like the modified n-ary tree iterator." His example syntax is `yield foreach sequence1;`, and "A programmer could use yield return, yield break, and yield foreach in the same iterator." With the feature, a recursive `FromTo` is linear where the `foreach` expansion is quadratic. Source: [Wes Dyer, "All About Iterators"](https://learn.microsoft.com/en-us/archive/blogs/wesdyer/all-about-iterators)
- **[snippet]** The paper is Jacobs, Meijer, Piessens, Schulte, "Iterators revisited: Proof rules and implementation", Workshop on Formal Techniques for Java-like Programs (FTfJP), 2005. Confirmed as a bibliographic entry only. Source: [arXiv 2506.20310, reference list](https://arxiv.org/pdf/2506.20310)
- **[snippet]** Matt Warren (C# compiler team) wrote that the idea goes back to the C# 3.0 design: "As far back as during the design for C# 3.0 the design team contemplated a possible language feature to solve the problem of quadratic iterators (the yield foreach syntax) that was never implemented." Source: [Matt Warren's gists](https://gist.github.com/mattwar) (exact gist URL not captured)
- **[snippet]** Eric Lippert, answering "why not" (Stack Overflow, about 2010): the cost is that "we'd have to cut something better." Source: [Stack Overflow, "yield return many"](https://stackoverflow.com/questions/3851997/yield-return-many) (page could not be fetched; wording from a search summary)
- **[snippet]** The request is still open as a csharplang discussion. A participant lists the candidate spellings: "I happen to have proposed yield foreach, but it could be yield from, yield all, yield many, yield*, yield!". Source: [dotnet/csharplang discussion 5303](https://github.com/dotnet/csharplang/discussions/5303)
- **[read]** A commenter on Lippert's 2009 post asked for "chainable iterators -- that 'yield return' could be passed an IEnumerable to fold in", and described the cost of the nested form: "you zip up and down the co-routine's call stack on every iteration step." Source: [Lippert, "Iterator Blocks, Part One", comments](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-one)

### Inferences
- The C# motive for delegation was performance and brevity of flattening (`IEnumerable<T>` of `IEnumerable<T>`), not Python's PEP 380 motive of refactoring a generator that also receives sent values and returns a result. C# iterators have no send channel and no return value, so `yield foreach` would have been a pure flattening construct.
- F# got the construct C# declined: `yield!` in sequence expressions. The csharplang list of spellings includes `yield!` for that reason. (F# detail from memory, not sourced here.)

### Gaps
- I could not open the Jacobs et al. paper (the KU Leuven URL now returns 404, the Microsoft Research page 404, CiteSeer not tried). I cannot quote its abstract, whether it uses the words "yield foreach", or what it says about Cω, Spec#, CLU, or Sather.
- Cω (Comega) streams: Cω's `T*` stream types and automatic flattening of nested streams are the usual ancestor cited for nested iterators. Not confirmed in a primary source here.
- Lippert's exact Stack Overflow wording and date, and any csharplang issue where the language design team formally declined the feature, were not retrieved.

## C# has no send or throw; `Dispose` and `finally` as its close

### Takeaway
A C# iterator is pull-only: `IEnumerator<T>` has `MoveNext()`, `Current`, and `Dispose()`, with nothing that passes a value or an exception in. `Dispose()` runs pending `finally` blocks, which is C#'s counterpart to Python's `close()`. The designer statement on record is Lippert's: coroutine scenarios "did not drive the design".

### Cited Findings
- **[snippet]** Lippert, 2009 ("Why no yield in finally?"): "We generate a Dispose method that checks the current state and executes any pending finally blocks. What the heck is the Dispose method supposed to do when it encounters the yield return in the pending finally block?" Source: [Lippert, "Iterator Blocks, Part Three"](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-three-why-no-yield-in-finally)
- **[read]** A commenter on Part One summarizes the consequence: "finally blocks run if the iterator is abandoned via Dispose. Yielding more items wouldn't be the sanest response to that." (A reader comment, not Lippert.) Source: [Lippert, "Iterator Blocks, Part One", comments](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-one)
- **[snippet]** Lippert's "Push vs Pull" post (2009) discusses the `try`/`catch` restrictions and says the original designers debated them at length. Source: [Lippert, "Iterator Blocks, Part Five: Push vs Pull"](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-five-push-vs-pull)
- **[read]** Scope statement quoted above ("iterators over collections", coroutine uses "did not drive the design"). Source: [Lippert, "Iterator Blocks, Part One"](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/iterator-blocks-part-one)

### Inferences
- Python's rule that a generator must not yield while handling `GeneratorExit` (a `RuntimeError`) and C#'s compile-time ban on `yield return` inside `finally` address the same problem at different times: what a close does when cleanup code tries to produce another value. C# rejects the program; Python raises at run time.
- C# got its two-way channel by a separate feature (`await`, 2012) and never retrofitted one onto iterators.

### Gaps
- No designer statement found that directly addresses "why no send/throw into an iterator". The absence follows from the collection-iteration scope, and that reading is mine.

## C# 5 async/await (2012), its roots, C# 8 async streams (2019), and who credited C#

### Takeaway
C# 5 `async`/`await` reuses the iterator state-machine technique and is widely attributed to F# asynchronous workflows; the F# authors themselves wrote in 2011 that C# had announced "an adapted version" of their approach. Python's PEP 492 names C# first in its list of precedents for the keywords. C# 8 (2019) added `IAsyncEnumerable<T>`, `await foreach`, and async iterators.

### Cited Findings
- **[snippet]** Syme, Petricek, Lomov, "The F# Asynchronous Programming Model" (PADL 2011) says of F# async that "an adapted version of this approach has recently been announced for a future version of C#." Source: [Petricek, paper page](https://tomasp.net/academic/papers/async)
- **[snippet]** Tomas Petricek (2010): "The C# asynchronous programming support and the await keyword is largely inspired by F# asynchronous workflows", and he notes surprise that F# was not credited more visibly in the PDC 2010 announcement. An outside view from an F# contributor. Source: [Petricek, "Asynchronous C# and F# (I.)"](https://tomasp.net/blog/csharp-fsharp-async-intro.aspx)
- **[snippet]** Implementation difference: the C# compiler "uses a similar technique as when compiling iterators and creates a state machine", while F# compiles workflows to higher-order functions (continuations). Source: [Petricek, "Asynchronous C# and F# (III.)"](https://tomasp.net/blog/async-compilation-internals.aspx/)
- **[snippet]** Lippert on the keyword choice (C# 5 design, 2010): "We rejected options of the form "yield with", "yield wait" and so on because we felt that it would be too easily confused with the subtly different continuation behaviour of iterator blocks." Source: [Lippert, "Asynchrony in C# 5 Part Six: Whither async?"](https://learn.microsoft.com/en-us/archive/blogs/ericlippert/asynchrony-in-c-5-part-six-whither-async)
- **[read]** Python credits C#: PEP 492 (2015), section "Why 'async' and 'await' keywords", lists precedents beginning with "C# has it since long time ago", then the "proposal to add async/await in ECMAScript 7", Facebook's Hack/HHVM, Google's Dart, and Scala. Source: [PEP 492](https://peps.python.org/pep-0492/)
- **[snippet]** TypeScript credits C#: the TypeScript async functions proposal (2015) says it is based "primarily on the Async Functions strawman proposal for ECMAScript, and C# 5.0 § 10.15 Async Functions." Source: [microsoft/TypeScript issue 1664](https://github.com/Microsoft/TypeScript/issues/1664)
- **[snippet]** C# 8 async streams have a published proposal covering `IAsyncEnumerable<T>`, `await foreach`, and async iterators. Not opened. Source: [C# 8.0 proposal, async streams](https://learn.microsoft.com/dotnet/csharp/language-reference/proposals/csharp-8.0/async-streams)
- **[snippet]** F# async workflows are dated 2007 (F# 1.9.2.7) in one source and 2010 (F# 2.0, the first supported release) in another; C# shipped the feature in C# 5 (2012) after a 2010-2011 Async CTP. Source: [Petricek, "Asynchronous C# and F# (I.)"](https://tomasp.net/blog/csharp-fsharp-async-intro.aspx)

### Inferences
- The lineage that matters for a generators history: C# iterators (2005) gave the compiler team the state-machine rewrite, and `await` (2012) is that rewrite with a different driver. JavaScript and Python reached `await` by the opposite route, through generators that already had a send channel (task.js and co; `yield from` and asyncio), then added dedicated syntax.

### Gaps
- No first-person credit to F# from Hejlsberg, Torgersen, or Lippert was retrieved. A secondhand report says a Hejlsberg Channel 9 interview makes the link; unverified.
- Cω and Axum as roots of C# async: not confirmed in any source opened here.
- The C# 8 ship date (September 2019, with .NET Core 3.0) and the async-streams proposal text were not opened. Whether the proposal mentions other languages is unknown.
- A TC39 primary source that credits C# for JavaScript async functions was not found (see the async section below).

## Mozilla JavaScript 1.7 and 1.8 (2006-2008): the Python borrowing and what legacy generators supported

### Takeaway
Brendan Eich announced on 2006-02-19 that JavaScript would take iterators, generators, and comprehensions from Python, and JavaScript 1.7 shipped them in Firefox 2 (October 2006). Legacy generators were close copies of Python 2.5's: `next()`, `send()`, `throw()`, `close()`, with a `StopIteration` exception ending iteration, and no star on the function.

### Cited Findings
- **[read]** Brendan Eich, "Python and JavaScript", 2006-02-19: the plan is "infusing JS with Pythonic generators and iterators, including array comprehensions." He poses the question "Why borrow from Python for iteration, generators, and comprehensions?" and the answer includes "we would rather follow than lead." Source: [brendaneich.com, 2006-02](https://brendaneich.com/2006/02/python-and-javascript/) (the fetch tool returned these fragments, not the full paragraphs; reread before quoting at length)
- **[read]** Mark Hammond relayed the post to python-dev on 2006-02-20, quoting the phrases "standing on Python's shoulders" and "borrow from Python for iteration, generators, and comprehensions". Source: [python-dev, 2006-02-20](https://mail.python.org/pipermail/python-dev/2006-February/061472.html)
- **[read]** Eich in the comments of his post (2006-03-28), on the one deliberate difference in iteration: "Python defines iteration by a protocol that different data types can map to keys, values, or even (key, value) pairs" and "JS's objects, even arrays, are more like Python's dicts". Source: [brendaneich.com, 2006-02](https://brendaneich.com/2006/02/python-and-javascript/)
- **[snippet]** JavaScript 1.7 added generators, iterators, array comprehensions, `let`, and destructuring assignment; Firefox 2 was the first browser to support it; `yield` and `let` required an explicit `version=1.7` script type. Source: [archived MDN "New in JavaScript 1.7" (2011 capture, via proxy)](https://pengen.diewe.workers.dev/terngr/novelty-https-web.archive.org/web/20110804222907/https://developer.mozilla.org/en/New_in_JavaScript_1.7)
- **[snippet]** Same archived page, on `send()`: sending `undefined` equals calling `next()`, and sending any other value to a newborn generator throws a `TypeError` (Python 2.5's rule). Source: [archived MDN "New in JavaScript 1.7"](https://pengen.diewe.workers.dev/terngr/novelty-https-web.archive.org/web/20110804222907/https://developer.mozilla.org/en/New_in_JavaScript_1.7)
- **[snippet]** Legacy generator objects had `next`, `send`, `throw`, and `close`; `next` on a finished or closed generator "throws a `StopIteration` object". Source: [Shu-yu Guo, SpiderMonkey legacy-generator notes (gist)](https://gist.github.com/syg/da04f29662c6ec0106b2a6f828ccc038)
- **[snippet]** `close()` forced the generator to shut down and ran active `finally` clauses. Source: [WebPlatform docs, "Iterators and generators"](https://www.webplatform.org/docs/concepts/javascript/iterators)
- **[read]** Dave Herman, in the SpiderMonkey bug for the Harmony syntax, on ending iteration by exception: "This is a generalization of StopIteration, which was the original Python design and the original ES4 design as well." Source: [Mozilla bug 666399](https://bugzilla.mozilla.org/show_bug.cgi?id=666399)
- **[read]** Same bug, on the legacy restriction: "As in Python (see PEP-255), disallow return v; in generators." Source: [Mozilla bug 666399](https://bugzilla.mozilla.org/show_bug.cgi?id=666399)
- **[snippet]** Contemporary reaction, 2006-06-05: "Javascript 1.7 has Python style generators". Jeremy Hylton (a Python core developer) wrote on 2006-02-22 about JavaScript getting iterators and generators via Python. Sources: [Chris Double, 2006-06-05](https://bluishcoder.co.nz/2006/06/05/javascript-17.html); [Jeremy Hylton, 2006-02-22](https://jeremyhylton.blogspot.com/2006/02/generators-in-javascript.html)
- **[read]** Andy Wingo, 2013-10-07: "SpiderMonkey has had generators since Firefox 2 (really!)". Source: [wingolog, 2013-10-07](https://wingolog.org/archives/2013/10/07/es6-generators-and-iteration-in-spidermonkey)

### Inferences
- The timing matters: Python 2.5 (PEP 342, `send`/`throw`/`close`) was released in September 2006, and Eich's post is February 2006, so JS 1.7 copied the PEP 342 design while Python 2.5 was still in development. Firefox 2 and Python 2.5 shipped within weeks of each other. (Python and Firefox release dates are from memory.)
- Legacy JS generators therefore shipped Python's full generator object API, exception-terminated protocol included, seven years before the standard replaced the protocol.

### Gaps
- Generator expressions and expression closures in JavaScript 1.8 (Firefox 3, 2008): not sourced in this session. From memory only.
- Eich's full paragraph around "we would rather follow than lead" should be read in the original; my tool returned fragments. I recall the reasons he gives as Python's years of design experience and the overlap of the two programmer communities, which a search summary also reported.
- No sentence found in which Eich names PEP 342 or Python 2.5 by number in the 2006 post (the fetch reported no PEP numbers in it).

## ES4, then ES6/ES2015: `function*`, `yield*`, the `{value, done}` protocol, PEP 380, and engine ship dates

### Takeaway
ES6 kept Python's generator semantics and changed the surface: a star marks the function (so `yield` need not be reserved in ordinary functions), the iterator protocol returns `{value, done}` objects in place of throwing `StopIteration`, `send()` folded into `next(value)`, `close()` became `return(value)`, and `yield*` is the delegating form whose value is the delegate's return value, as in PEP 380. V8 landed the implementation in May-June 2013 behind a flag, and Firefox 26 (December 2013) shipped it by default.

### Cited Findings
- **[read]** The SpiderMonkey bug "new Harmony syntax for generators" was filed by Dave Herman, the author of the harmony:generators proposal, and closed by Andy Wingo with target milestone mozilla26. Brendan Eich in that bug: "I'm likely to patch all the new generator goodness (yield* and return e;) in Harmony here, or in sub-bugs." Source: [Mozilla bug 666399](https://bugzilla.mozilla.org/show_bug.cgi?id=666399)
- **[read]** Return values first appeared as a special exception. Herman in the same bug: "the returned value is thrown as a special GeneratorReturn value rather than yielded as another yield result." Source: [Mozilla bug 666399](https://bugzilla.mozilla.org/show_bug.cgi?id=666399)
- **[snippet]** A companion Mozilla bug states the PEP 380 link directly: "Harmony is extending generators to allow them to return values, similarly to Python's PEP 380." Source: [Mozilla bug 666404](https://bugzilla.mozilla.org/show_bug.cgi?id=666404) (seen in a search summary attributed to the Mozilla tracker; the bug number is my best match and should be checked)
- **[read]** The protocol change came late. Andy Wingo, 2013-05-08: "the current ES6 draft specification for generators is slightly different from what Firefox ships", after TC39 discussions in March 2013. "The SpiderMonkey JS engine used by Firefox uses an exception to indicate that the iterator is finished", and under the new draft `next` returns an object with `value` and `done` properties. Source: [wingolog, "generators in v8", 2013-05-08](https://www.wingolog.org/archives/2013/05/08/generators-in-v8)
- **[read]** V8: generators landed behind `--harmony` / `--harmony-generators`. "I'm happy to say that it's all upstream now, modulo yield* which should go in soon." "Barring unforeseen issues, this will probably see the light in Chromium 29, corresponding to V8 3.19." Wingo (Igalia) did the work "working closely with V8 hackers Michael Starzinger and Andreas Rossberg". Source: [wingolog, "generators in v8", 2013-05-08](https://www.wingolog.org/archives/2013/05/08/generators-in-v8)
- **[snippet]** `yield*` landed in V8 as a separate change, "Implement yield* (delegating yield)", by Wingo in 2013. Source: [Chromium code review 14582007](https://codereview.chromium.org/14582007/)
- **[snippet]** A September 2014 blink-dev thread (intent to ship) says V8 had generator functions under the flag since June 2013 and that Firefox had shipped ES6 generators since version 26. Source: [blink-dev thread](https://groups.google.com/a/chromium.org/g/blink-dev/c/3DlzFt8Fc8o)
- **[read]** SpiderMonkey: Wingo, 2013-10-07, announces ES6 generators and iteration in Firefox nightlies: "now their generators are standard, and available by default", and "for-of" is "the built-in ES6 language construct for iteration." Source: [wingolog, 2013-10-07](https://wingolog.org/archives/2013/10/07/es6-generators-and-iteration-in-spidermonkey)
- **[read]** The remaining-work list in Wingo's SpiderMonkey patch includes "terminate with done: true instead of stopiteration" and `yield*`; a dependent bug is titled "Implement Generator.prototype.return". Source: [Mozilla bug 666399](https://bugzilla.mozilla.org/show_bug.cgi?id=666399)
- **[snippet]** On es-discuss it was confirmed that `send()` and `close()` were removed from the ES6 design, with `next(value)` taking the role of `send`. Source: [es-discuss, "State of generators?"](https://esdiscuss.org/topic/state-of-generators)
- **[snippet]** A SpiderMonkey note describes the legacy form as the JavaScript 1.7 version "where the star (*) in the function declaration was not necessary". Source: [Generator reference (MDN mirror)](https://reference.codeproject.com/javascript/Reference/Global_Objects/Generator)
- **[read]** A commenter on Wingo's post distinguishes "Python style" coroutines, "where you can only yield from the top-level procedure", and Wingo calls them shallow coroutines. Dave Herman argued for the shallow design on es-discuss. Sources: [wingolog, 2013-10-07](https://wingolog.org/archives/2013/10/07/es6-generators-and-iteration-in-spidermonkey); [es-discuss, "yield syntax"](https://esdiscuss.org/topic/yield-syntax-diverging-from-how-would-shallow-generators-compose-with-lambda)

### Inferences
- What ES6 took from Python: the shallow (one-frame) generator, `yield` as an expression that receives a value, `throw()`, delegation with a result value (PEP 380), and generator `return v` (legal in Python from 3.3, 2012).
- What ES6 changed: (1) `function*` in place of inference from the body, (2) `{value, done}` in place of `StopIteration`, which removes the problem PEP 479 later fixed in Python (a stray `StopIteration` silently ending a generator), (3) `yield*` spelled with a star to match `function*` and to avoid a second contextual keyword, (4) `return(value)` in place of `close()`, so a consumer can supply the completion value, and `for-of` calls `return()` on early exit, where Python leaves an abandoned generator to the garbage collector.
- Chrome 29 was the version Wingo predicted for the flag-gated feature. The on-by-default Chrome release (39, late 2014, from memory) follows the September 2014 blink-dev thread.

### Gaps
- The harmony:generators wiki page itself (wiki.ecmascript.org, archived) could not be fetched, so I have no verbatim quotation of the proposal's own words on Python, PEP 342, PEP 380, the `function*` rationale, or why `yield*` and not `yield from`. My recollection is that the page said the design was based on JavaScript 1.7 generators and Python, and gave the star as the way to make `yield` unambiguous without a body scan and to allow a generator with no `yield`. Treat that as unverified.
- "JavaScript: The First 20 Years" (Wirfs-Brock and Eich, HOPL IV, 2020) was not opened. It is the best single primary account of JS 1.7, ES4, and the Harmony generator design and should be checked for crediting sentences.
- ES4-era proposals (2006-2008) for iterators and generators: only Herman's one-line statement that `StopIteration` was "the original ES4 design" was found.
- TC39 notes for the March 2013 decision to replace `StopIteration` with `{value, done}` were not retrieved; the date rests on Wingo's post.
- Exact Firefox 26 release date (December 2013) and Chrome's on-by-default version are from memory.

## Removal of comprehensions from the ES6 drafts (2014)

### Takeaway
Array comprehensions and generator comprehensions (the Python-derived forms, in ES6 drafts for years and shipped in SpiderMonkey) were deferred at the June 2014 TC39 meeting on Dave Herman's motion, reconfirmed at the July 2014 meeting, and removed from the draft in revision 27 (August 2014). The stated reason was to make room for a generalized comprehension design later, which never arrived.

### Cited Findings
- **[snippet]** Dave Herman presented "A better future for comprehensions" at the June 2014 meeting, proposing to defer comprehensions past ES6 "in order to simplify and generalize the feature". The 2014-06-06 notes carry the item "Follow up on deferring comprehensions". Sources: [Herman slides](https://speakerdeck.com/dherman/a-better-future-for-comprehensions); [TC39 June 2014 notes, contents](https://archives.ecma-international.org/2014/notes/2014-06/toc.html)
- **[read]** Brendan Eich, es-discuss, 2014-08-11: "One of the breakthroughs in removing comprehensions from ES6 was everyone wanting to generalize from 1 (Array) to N>>1", and "TC39 isn't willing to call that right now given how ES6 has slipped." His summary: "So "defer" or "cut" ... won." Source: [es-discuss, "Comprehensions, Where Art Thou?"](https://esdiscuss.org/topic/comprehensions-where-art-thou)
- **[read]** Jason Orendorff, same thread: "The original rationale was to make room for some more extensible comprehension syntax for ES7". Rick Waldron: "Yes, Dave Herman is the champion for this in ES7". Andy Wingo: "we end up in current situation of punting on both of them for now." Source: [es-discuss, "Comprehensions, Where Art Thou?"](https://esdiscuss.org/topic/comprehensions-where-art-thou)
- **[read]** The July 30, 2014 meeting had the agenda item "revisit comprehension decision from last meeting", per Eich's post. Source: [es-discuss, "Comprehensions, Where Art Thou?"](https://esdiscuss.org/topic/comprehensions-where-art-thou)
- **[read]** Kevin Smith, opening that thread, calls comprehensions "a well-loved feature of Python". Source: [es-discuss, "Comprehensions, Where Art Thou?"](https://esdiscuss.org/topic/comprehensions-where-art-thou)
- **[snippet]** An MDN-derived page says generator comprehensions "were initially in the ECMAScript 6 draft, but got removed in revision 27 (August 2014)". Source: [MDN mirror, "Generator comprehensions"](https://svmod.neocities.org/docs/javascript/Operators/Generator_comprehensions)
- **[read]** SpiderMonkey had implemented the ES6-draft forms earlier in 2014. Source: [wingolog, "es6 generator and array comprehensions in spidermonkey", 2014-03-07](https://wingolog.org/archives/2014/03/07/es6-generator-and-array-comprehensions-in-spidermonkey) (title and date seen in search results; body not opened, so this is **[snippet]** strength)

### Inferences
- JavaScript is the one language in this survey that took Python's comprehension syntax, shipped it in an engine for eight years (2006-2014 and after), put it in the standard's drafts, and then declined it. Iterator helper methods (`map`, `filter`, `take` on iterators, standardized much later) fill the role.

### Gaps
- One search summary reported a "Rev21" change log that also lists the removal, which conflicts with revision 27. I did not resolve it. Revision 27 (August 2014) agrees with the June and July 2014 meeting dates and is the better-supported figure.
- The June 6, 2014 resolution text was not read.

## Generators for async (task.js, co), ES2017 async functions, ES2018 async generators and `for await`

### Takeaway
Before `await`, JavaScript used generators as the suspension mechanism for asynchronous code (Q.async, Dave Herman's task.js, co), which is the same step Python took with PEP 342 and PEP 380. Async functions entered ES2017 and async iteration ES2018. I found a C# credit in TypeScript's proposal and in Python's PEP, and none in a TC39 document.

### Cited Findings
- **[read]** Andy Wingo, 2013-05-08, on the demand for generators in V8: "Q.async has been part of Q for a while now, because Firefox has been shipping generators for some time." Source: [wingolog, "generators in v8"](https://www.wingolog.org/archives/2013/05/08/generators-in-v8)
- **[snippet]** Dave Herman wrote task.js on top of generators and argued for shallow generators in that context. Source: [es-discuss, "yield syntax"](https://esdiscuss.org/topic/yield-syntax-diverging-from-how-would-shallow-generators-compose-with-lambda)
- **[snippet]** TC39, 2014-01-30: Luke Hoban (Microsoft) and Mark Miller argued that `await` needs a different precedence from `yield`, and Hoban noted async functions could be combined with `function*`, which needs both keywords. Source: [TC39 notes, 2014-01-30](https://meetings.jquery.org/2014-01-30-tc39/)
- **[snippet]** The async functions proposal repository notes that "a similar proposal was made with Deferred Functions during ES6 discussions." Source: [tc39/proposal-async-await](https://github.com/tc39/ecmascript-asyncawait)
- **[snippet]** TypeScript's 2015 proposal is based "primarily on the Async Functions strawman proposal for ECMAScript, and C# 5.0 § 10.15 Async Functions." Source: [microsoft/TypeScript issue 1664](https://github.com/Microsoft/TypeScript/issues/1664)
- **[snippet]** The async functions specification reached a Stage 3 draft dated 2015-09-28. Source: [Ecma archive, tc39-2015-044](https://archives.ecma-international.org/2015/TC39/tc39-2015-044.html)
- **[read]** Async iteration proposal README: "Async for-of statements are only allowed within async functions and async generator functions". Async generator methods `next`, `throw`, and `return` return promises for `{ value, done }`. "The behavior of `yield*` is modified to support delegation to async iterables." Implementations listed as shipping: JavaScriptCore (Safari Tech Preview 40), SpiderMonkey (Firefox 57), V8 (Chrome 63). The README credits no other language. Source: [tc39/proposal-async-iteration](https://github.com/tc39/proposal-async-iteration)
- **[snippet]** The async iteration spec draft "depends upon the async functions proposal" and adds `for-await-of` plus async generator functions and methods. Source: [tc39.es/proposal-async-iteration](https://tc39.es/proposal-async-iteration)
- **[snippet]** V8's async functions were implemented by Igalia in 2016. Source: [Igalia compilers blog, 2016-05-23](https://blogs.igalia.com/compilers/2016/05/23/awaiting-the-future-of-javascript-in-v8/)

### Inferences
- JavaScript async generators keep `yield*` delegation, which Python's async generators (PEP 525) omit: `yield from` is a syntax error inside `async def`. That is a point where JavaScript carried the PEP 380 idea further than Python did.
- The cross-credit chain as far as primary sources support it: Python (PEP 255/342/380) to JS 1.7 and ES6 generators; F# to C# for async; C# to Python (PEP 492, explicit) and to TypeScript (explicit); C# to ECMAScript by common attribution, not by a TC39 sentence I could find.

### Gaps
- No TC39 proposal text, meeting note, or statement by a champion (Luke Hoban, Brian Terlson) was found that credits C# for async functions. Hoban had worked on C# and F# at Microsoft before TC39 (from memory), which is the usual basis for the attribution.
- Champions and stage dates for async iteration (Domenic Denicola, with Kevin Smith's earlier design, from memory) are not on the README and were not confirmed. No crediting of C#, Dart, or Python found there.
- co (TJ Holowaychuk, 2013) and task.js (2011-2012): dates from memory, not sourced.
- The deferred-functions strawman on the old wiki was not read; it may carry a C# credit.

## TypeScript and CoffeeScript

### Takeaway
One line each is warranted. TypeScript's async functions proposal is the one JavaScript-family document found that names the C# specification as a basis. Nothing was researched on CoffeeScript.

### Cited Findings
- **[snippet]** TypeScript async functions proposal (2015): based "primarily on the Async Functions strawman proposal for ECMAScript, and C# 5.0 § 10.15 Async Functions." Source: [microsoft/TypeScript issue 1664](https://github.com/Microsoft/TypeScript/issues/1664)

### Inferences
- Anders Hejlsberg led both C# and TypeScript, which makes the direct citation of the C# spec section unsurprising.

### Gaps
- CoffeeScript generators (1.9.0, 2015, where a function containing `yield` becomes a generator with no star, the Python and JS 1.7 rule) are from memory and unsourced.
- TypeScript's down-level compilation of generators and async functions to state machines (TypeScript 2.1 and 2.3, from memory) was not sourced.
