# The Theory Behind Generators: Control State, Coroutines, Continuations, Iteration, Laziness, and Effects

Scope: how computer science characterizes a generator and why it is a useful abstraction.
History (Conway, CLU, Icon, the Python PEPs) belongs to other researchers and appears here only where a theory source cites it.
Every quotation below was copied from the text of the source named beside it, extracted from the PDF or HTML on 2026-11-05, unless the bullet says "unverified" or names a secondary route.
PDF extraction joins hyphenated line breaks, so a quotation may differ from the printed page in a hyphen or a ligature, never in a word.

## 1. de Moura and Ierusalimschy, "Revisiting Coroutines": the classification and where Python generators fall

### Takeaway
The paper classifies coroutines on three axes (symmetric or asymmetric control transfer, first-class or constrained, stackful or not) and places Python generators as first-class asymmetric coroutines that are not stackful: "only the main body of a generator can suspend."
Its central result is that *full* coroutines (first-class and stackful) match one-shot continuations in expressive power, and full asymmetric coroutines match one-shot partial continuations; Python generators fall outside "full", so the equivalence does not cover them, and a 2025 paper qualifies the equivalence itself.

### Cited Findings
- Edition used.
  The quotations come from the PUC-Rio technical report: "Revisiting Coroutines", Ana Lúcia de Moura and Roberto Ierusalimschy, PUC-RioInf.MCC15/04, June 2004.
  The journal version is ACM TOPLAS 31(2), 6:1-6:31, 2009, doi 10.1145/1462166.1462167 (citation as given in Kobayashi and Kameyama's reference list).
  I did not read the TOPLAS text, so its wording may differ.
  Source: [de Moura and Ierusalimschy 2004, tech report PDF](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Abstract: "This paper defends the revival of coroutines as a general control abstraction. After proposing a new classification of coroutines, we introduce the concept of full asymmetric coroutines and provide a precise definition for it through an operational semantics. We then demonstrate that full coroutines have an expressive power equivalent to one-shot continuations and one-shot partial continuations. We also show that full asymmetric coroutines and one-shot partial continuations have many similarities, and therefore present comparable benefits. Nevertheless, coroutines are easier implemented and understood, specially in the realm of procedural languages."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Conway's definition, as the paper reports it (section 1): "It is attributed to Conway, who described coroutines as “subroutines who act as the master program”, and implemented this construct to simplify the cooperation between the lexical and syntactical analyzers in a COBOL compiler [Conway 1963]."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Marlin's two-part characterization of a coroutine, quoted in section 1: "“the values of data local to a coroutine persist between successive calls”;" and "“the execution of a coroutine is suspended as control leaves it, only to carry on where it left off when control re-enters the coroutine at some later stage”."
  The authors add: "Apart from the capability of keeping state, we can identify three main issues that distinguish coroutine facilities: • the control-transfer mechanism, which can provide symmetric or asymmetric coroutines; • whether coroutines are provided in the language as first-class objects, which can be freely manipulated by the programmer, or as constrained constructs; • whether a coroutine is a stackful construct, i.e., whether it is able to suspend its execution from within nested calls."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Symmetric versus asymmetric (section 2.1): "Symmetric coroutine facilities provide a single control-transfer operation that allows coroutines to explicitly pass control between themselves. Asymmetric coroutine mechanisms (more commonly denoted as semi-symmetric or semi coroutines [Dahl et al. 1972]) provide two control-transfer operations: one for invoking a coroutine and one for suspending it, the latter returning control to the coroutine invoker. While symmetric coroutines operate at the same hierarchical level, an asymmetric coroutine can be regarded as subordinate to its caller, the relationship between them being somewhat similar to that between a called and a calling routine."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Which kind suits which job (section 2.1): "coroutine mechanisms intended for implementing constructs that produce sequences of values typically provide asymmetric coroutines. Examples of this type of construct are iterators [Liskov et al. 1977; Murer et al. 1996] and generators [Griswold and Griswold 1983; Schemenauer et al. 2001]."
  Schemenauer et al. 2001 is PEP 255.
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Symmetric and asymmetric are equally expressive but not equally easy (section 2.1): "it is easy to demonstrate that we can express any of these constructs in terms of the other" and "asymmetric coroutines behave like routines, in the sense that control is always transfered back to their invokers. Since even novice programmers are familiar with the concept of a routine, control sequencing is simpler to manage and understand. Moreover, asymmetric coroutines allow the development of more structured programs."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- First-class versus constrained (section 2.2): "In some implementations of coroutines, typically intended for particular uses, coroutine objects are constrained within a textual bound and cannot be directly manipulated by the programmer."
  On CLU: "CLU iterators are confined within a for loop that can invoke exactly one iterator. This restriction imposes a considerable limitation to the use of the construct; parallel traversals of two or more data collections, for instance, are not possible."
  On Icon: "Icon generators are confined within an expression and can only be invoked by explicit iteration or goal-directed evaluation. Icon generators are easier to use than CLU and Sather iterators, but they are not powerful enough to provide for programmer-defined control structures. This facility is only provided when coroutines are implemented as first-class objects, which can be freely manipulated by the programmer and invoked at any place."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Stackfulness and Python (section 2.3): "Stackful coroutine mechanisms allow coroutines to suspend their execution from within nested functions; the next time the coroutine is resumed, its execution continues from the exact point where it suspended."
  Then: "In Python [Schemenauer et al. 2001], a function that contains an yield statement is called a generator function. When called, this function returns an object that can be resumed at any point in a program, so it behaves as an asymmetric coroutine. Despite constituting a first-class object, a Python generator is not a stackful construct; it can only suspend its execution when its control stack is at the same level that it was at creation time. In other words, only the main body of a generator can suspend."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- What Python generators cannot express (section 2.3): "Python generators and similar non-stackful constructs permit the development of simple iterators or generators but complicate the structure of more elaborate implementations. As an example, if items are produced within recursive or auxiliary functions, it is necessary to create an hierarchy of auxiliary generators that yield in succession until the original invocation point is reached. This type of generator is also not powerful enough to implement user-level multitasking."
  The conclusion repeats it: "restricted forms of coroutines support the implementation of simple iterators and generators, but are not powerful enough to constitute a general control abstraction; in particular, they cannot be used as a concurrent construct."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Full coroutines (section 2.4): "two issues determine the expressive power of a coroutine facility: whether coroutines are first-class objects and whether they are stackful constructs. In the absence of these facilities, a coroutine mechanism cannot support several useful control behaviors, notably multitasking, and, therefore, does not provide a general control abstraction. We then introduce the concept of a full coroutine as a first-class, stackful object, which, as we will demonstrate later, can provide the same expressiveness as obtained with one-shot continuations."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- The result, stated in the introduction: "contrary to common belief, coroutines are not far less expressive than continuations. Instead, when provided as first-class objects and implemented as stackful constructs — that is, when a full coroutine mechanism is implemented — coroutines have equivalent power to that of one-shot continuations."
  In section 4: "We have just shown that full asymmetric coroutines can be used to express both one-shot continuations and one-shot partial continuations, which allow us to argue that full asymmetric coroutines have equivalent expressive power to those abstractions. However, expressing one-shot continuations and subcontinuations with coroutines and the reverse operations may not be equivalent in terms of efficiency."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- The pairing of each continuation kind with a coroutine kind (section 6): "full asymmetric coroutines can provide not only symmetric coroutines but also one-shot continuations and one-shot partial continuations, and discussed the similarities between one-shot continuations and full symmetric coroutines, and between one-shot partial continuations and full asymmetric coroutines."
  Section 4.3 spells out the correspondence: "Full asymmetric coroutines can be regarded as independent subcomputations. Invoking a subcomputation controller is similar to suspending an asymmetric coroutine. Invoking a one-shot subcontinuation corresponds to resuming an asymmetric coroutine. Like subcontinuations, asymmetric coroutines can be composed: they behave like regular functions, always returning control to their invoker."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Why continuations lost to coroutines in usability (section 1): "Apart from efficiency issues, the concept of a continuation as a representation of the rest of a computation is difficult to manage and understand, specially in the context of procedural languages. The abortive nature of a continuation invocation complicates considerably the structure of programs".
  Section 4.3: "Most of the complexity involved in the use of continuations arise from the fact that they represent the whole rest of a computation."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- A generator as a special case of producer/consumer (section 5.2): "A generator is a control abstraction that produces a sequence of values, returning a new value to its caller for each invocation. Actually, generators are nothing more than a particular instance of the producer–consumer problem, with the generator behaving as the producer."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Qualification of the equivalence result, 2025.
  Kobayashi and Kameyama, "Expressive Power of One-Shot Control Operators and Coroutines" (APLAS 2025), abstract: "We verify the folklore that one-shot effect handlers and one-shot delimited-control operators can be macro-expressed by asymmetric coroutines, but not vice versa. We explain why a previous informal argument fails, and how to revise it to make a valid macro-translation."
  Contributions: "3. We show that the converse direction does not hold: asymmetric coroutines cannot be macro-expressed by either one-shot delimited-control operators or one-shot effect handlers."
  On de Moura and Ierusalimschy: "this correspondence relies heavily on mutable states that can store higher-order functions, which, in our view, obscures the raw expressive power of these control operators."
  They call their own negative result "counter-intuitive, since effect handlers are considered a universal tool for expressing various computational effects, such as coroutines. This gap arose due to the strictness of macro-translations, which adheres to Felleisen’s original notion. We conjecture that, under a suitably relaxed definition of macro-translations, EFF one can macro-express REF and AC."
  Source: [Kobayashi and Kameyama 2025, arXiv 2509.11901](https://arxiv.org/abs/2509.11901)

### Inferences
- Python generators sit at: asymmetric (yes), first-class (yes), stackful (no).
  "Half a coroutine" therefore names two restrictions at once: control returns to the resumer (asymmetric, which the paper calls equivalent in power to symmetric), and suspension is limited to the generator's own frame (stackless, which the paper says costs real power).
  The second restriction is the one that matters for expressiveness; the first costs nothing in power and gains structure.
  The chapter's "half a coroutine" fits the paper's own vocabulary ("semi coroutines", after Dahl et al. 1972), but a reader who knows the paper will expect the stackless limit to be named too.
- The one-shot-continuation equivalence is proved for *full* (stackful) coroutines.
  A Python generator is a strictly weaker object: it captures one frame, not the stack up to a delimiter.
  "A suspended generator is a one-shot continuation" is accurate only in the restricted sense James and Sabry give (section 2): a one-shot delimited continuation whose delimiter is the generator's own frame.
- PEP 380's `yield from` is the language's answer to the "hierarchy of auxiliary generators that yield in succession" the paper describes: it automates the hierarchy rather than removing it, so every function in the chain still has to be a generator.

### Gaps
- I read the 2004 technical report, not the 2009 TOPLAS article; wording and section numbers may differ in the journal version.
- "Coroutines in Lua" (de Moura, Rodriguez, Ierusalimschy, JUCS 2004) failed to download from lua.org; I have no quotation from it.

## 2. Generators and continuations: the "rest of the computation" up to a boundary, used once

### Takeaway
A continuation is "the remainder of a computation from a given point" (Bruggeman, Waddell, Dybvig 1996); a delimited (partial) continuation is that remainder only up to a delimiter, and it composes like a function instead of aborting.
James and Sabry (2011) show that the `yield` operators of mainstream languages are one-shot or linearly used restrictions of delimited continuations; one-shot is the natural restriction because "most continuations are, in fact, invoked only once" and because a computation that resumes twice would run its cleanup twice.

### Cited Findings
- Definition of a continuation and the one-shot motivation, Bruggeman, Waddell, and Dybvig, "Representing Control in the Presence of One-Shot Continuations", PLDI 1996, pp. 99-107, doi 10.1145/231379.231395.
  Abstract: "Traditional first-class continuation mechanisms allow a captured continuation to be invoked multiple times. Many continuations, however, are invoked only once. This paper introduces one-shot continuations, shows how they interact with traditional multi-shot continuations, and describes a stack-based implementation of control that handles both one-shot and multi-shot continuations. The implementation eliminates the copying overhead for one-shot continuations that is inherent in multi-shot continuations."
  Introduction: "Continuations represent the remainder of a computation from a given point in the computation. When a continuation is invoked, control returns to the point in the program at which the continuation was captured. Traditional continuation mechanisms allow a continuation to be invoked multiple times. In our experience, however, most continuations are, in fact, invoked only once. In particular, this is true for continuations used to implement threads."
  The introduction lists coroutines among the control features continuations implement: "loops, nonlocal exits, nonblind backtracking [22], nondeterministic computations [10, 14], and coroutines [7]."
  Source: [Bruggeman, Waddell, Dybvig 1996 (copy hosted on a personal site; provenance of the copy unverified, text matches the ACM citation)](https://stanleymiracle.github.io/blogs/compiler/docs/chez-pub/22-call1cc.pdf)
- de Moura and Ierusalimschy describe Bruggeman's implementation in coroutine terms (section 4.2): "When a one-shot continuation is captured, the current stack segment is “encapsulated” in the continuation and a fresh stack segment is allocated to replace the current stack segment. In terms of symmetric coroutines, this corresponds to creating a new coroutine and transferring control to it. When a one-shot continuation is invoked, the current stack segment is discarded and control is returned to the saved stack segment."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Partial (delimited) continuations, de Moura and Ierusalimschy section 1: "Unlike traditional continuations, partial continuations represent only a “continuation slice” [Queinnec 1993], or the continuation of a subcomputation [Hieb et al. 1994]. Partial continuations are not abortive; they are composed with the current continuation and thus behave like regular functions."
  Section 4.3: "A subcontinuation represents the rest of an independent partial computation (a subcomputation) from a given point in that subcomputation."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Project Loom's design document gives the clearest working definition of a delimited continuation, and names Python generators as a use: "Here we will think of delimited continuations as sequential code that may suspend (itself) and resume (be resumed by a caller). Some may be more familiar with the point of view that sees continuations as objects (usually subroutines) representing "the rest" or "the future" of a computation. The two describe the very same thing: a suspended continuation, is an object that, when resumed or "invoked", carries out the rest of some computation. A delimited continuation is a sequential sub-program with an entry point (like a thread), which we'll call simply the entry point (in Scheme, this is the reset point), which may suspend or yield execution at some point, which we'll call the suspension point or the yield point (the shift point in Scheme). When a delimited continuation suspends, control is passed outside of the continuation, and when it is resumed, control returns to the last yield point, with the execution context up to the entry point intact."
  On stackless versus stackful continuations: "The continuations discussed here are "stackful", as the continuation may block at any nested depth of the call stack (in our example, inside the function bar which is called by foo, which is the entry point). In contrast, stackless continuations may only suspend in the same subroutine as the entry point. Also, the continuations discussed here are non-reentrant, meaning that any invocation of the continuation may change the "current" suspension point. In other words, the continuation object is stateful."
  And: "to also add continuations as a user facing abstraction, as continuations have other uses, too (e.g. Python's generators)."
  Source: [Ron Pressler, "Project Loom: Fibers and Continuations for the Java Virtual Machine" (proposal document)](https://cr.openjdk.org/~rpressler/loom/Loom-Proposal.html)
- James and Sabry, "Yield: Mainstream Delimited Continuations", Theory and Practice of Delimited Continuations (TPDC) 2011.
  Abstract fragments, as reposted by Claus Reinke on the es-discuss list (April 2011) and read through a summarizing fetch, so each fragment is verbatim but the full abstract is not: "Many mainstream languages have operators named yield that share common semantic roots"; the generalized yield "turns out to be a delimited control operator of comparable expressive power to shift-reset"; "The mainstream variants of yield turn out to be one-shot or linearly used restrictions" (of delimited continuations).
  Source: [es-discuss thread "FYI: Yield: Mainstream Delimited Continuations in TPDC2011"](https://esdiscuss.org/topic/fyi-yield-mainstream-delimited-continuations-in-tpdc2011); paper listed at [legacy.cs.indiana.edu/~sabry/papers/yield.pdf](https://legacy.cs.indiana.edu/~sabry/papers/yield.pdf) (that URL returned an HTML page to my download, so I did not read the PDF)
- Why one-shot is also a correctness property, not only an efficiency one: Dolan et al. (Multicore OCaml) make continuations linear for resource safety.
  "Systems programming generally involves the manipulation of scarce resources such as file handles, connections and locks. Such resources are inherently linear, stateful values: once a file handle is closed, it cannot be used again."
  "As well as the performance advantages mentioned above, this is the other major reason that our continuations are linear. By preserving the linearity of computations (operations that are begun once do not complete twice), we allow resource-manipulating code to work correctly in the presence of effects. Some interesting examples of programming with effects and handlers (such as backtracking) are incompatible with this approach, since they rely on continuations to be usable more than once."
  "We observe that many effect handlers do not resume the continuations more than once, and support only linear continuations by default, which can be implemented efficiently [9]."
  Source: [Dolan, Eliopoulos, Hillerström, Madhavapeddy, Sivaramakrishnan, White, "Concurrent System Programming with Effect Handlers" (TFP 2017; revised Feb 2018 copy)](https://kcsrk.info/papers/system_effects_feb_18.pdf)
- de Moura and Ierusalimschy on what one-shot loses: multi-shot continuations implement Prolog-style backtracking "and are used as examples of scenarios where one-shot continuations cannot be used [Bruggeman et al. 1996]. However, this type of control behavior can be easily implemented with full asymmetric coroutines used as generators".
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- Haynes, Friedman, and Wand, "Continuations and Coroutines", ACM Symposium on LISP and Functional Programming 1984, pp. 293-298; Indiana University TR158.
  The extended journal version is "Obtaining Coroutines with Continuations", Computer Languages 11(3/4), 1986, pp. 143-153 (bibliographic record only).
  Source: [Utah bibliography entry for Haynes, Friedman, Wand 1986](https://ftp.math.utah.edu/pub/tex/bib/idx/complngs/11/3/143_153.html)

### Inferences
- The precise sense in which a suspended Python generator is "the rest of the computation": the generator object holds one frame (locals plus the instruction pointer) and nothing below it.
  Resuming it with `send()` runs the remainder of that frame's body until the next `yield` or the end, then hands control back to whoever resumed it.
  The delimiter is the generator's own frame boundary; the caller's stack is never captured.
  This is Loom's "stackless continuations may only suspend in the same subroutine as the entry point", and James and Sabry's "one-shot or linearly used" restriction of a delimited continuation.
- Why one-shot: a Python generator object *is* its continuation, and the object is mutated in place by each resumption (Loom's "non-reentrant ... the continuation object is stateful").
  There is no copy to resume a second time.
  Bruggeman gives the efficiency reason (no copying) and Dolan gives the semantic reason (a `finally` block, or a `with` block's exit, would run twice).
- The usability argument for coroutines over continuations ("they represent the whole rest of a computation", "abortive") is the argument for a delimited, composable form, which is what a generator is.

### Gaps
- I could not read the Haynes, Friedman, and Wand 1984 paper or its abstract; a search summary attributes to the 1986 version the claim that first-class continuations "provide a general control abstraction for sequential computation" and implement coroutine mechanisms "using only continuations and functional abstraction". That wording is **unverified**.
- I could not read the full text of James and Sabry 2011; claims beyond the three abstract fragments (for example, their four-way taxonomy of yield variants or their treatment of Python specifically) are not covered here.

## 3. The state-machine view: what a compiler does to a generator, and why writing the machine yourself is bad

### Takeaway
Every source that compiles generators (C#, regenerator, Rust, Kotlin, C++20) lowers the function to a state machine whose state field is the old instruction pointer and whose other fields are the live locals.
The sources agree on what is wrong with writing that machine by hand: the control state becomes a named variable the programmer must maintain, the code is "turned inside out", and a change that would be a loop in the direct version becomes new states and transitions.

### Cited Findings
- Tatham, "Coroutines in C" (2000, updated 2005-03-07), states the producer/consumer problem: "Structuring a large program is always a difficult job. One of the particular problems that often comes up is this: if you have a piece of code producing data, and another piece of code consuming it, which should be the caller and which should be the callee?"
  His two fragments: "Each of these code fragments is very simple, and easy to read and understand. One produces a character at a time by calling emit(); the other consumes a character at a time by calling getchar(). If only the calls to emit() and the calls to getchar() could be made to feed data to each other, it would be simple to connect the two fragments together so that the output from the decompressor went straight to the parser."
  Threads as the heavyweight answer: "In many modern operating systems, you could do this using pipes between two processes or two threads. emit() in the decompressor writes to a pipe, and getchar() in the parser reads from the other end of the same pipe. Simple and robust, but also heavyweight and not portable."
  The rewrite: "The conventional answer is to rewrite one of the ends of the communication channel so that it's a function that can be called."
  The verdict: "And that's the point, really. Both these rewritten functions are thoroughly ugly compared to their originals. Both of the processes taking place here are easier to read when written as a caller, not as a callee. Try to deduce the grammar recognised by the parser, or the compressed data format understood by the decompressor, just by reading the code, and you will find that both the originals are clear and both the rewritten forms are less clear. It would be much nicer if we didn't have to turn either piece of code inside out."
  Knuth's answer: "His answer is to throw away the stack concept completely. Stop thinking of one process as the caller and the other as the callee, and start thinking of them as cooperating equals."
  On his macro implementation: "The worst part of it is that the set of labels must be maintained manually".
  Source: [Simon Tatham, "Coroutines in C"](https://www.chiark.greenend.org.uk/~sgtatham/coroutines.html)
- Tatham, "Philosophy of coroutines" (initial version 2023-09-01, updated 2025-03-25), names the control state as the program counter: "This function actually contains the same state machine as the previous version – but it’s entirely implicit. If you want to know what each piece of code will do when its next input byte arrives (say, during debugging), then in the state-machine version you answer it by asking for the value of state – but in this version, you’d answer it by looking at a stack backtrace".
  "In other words, each of the three state values TOP_LEVEL, EXPECT_RUN_LENGTH and EXPECT_OUTPUT in the state-machine code corresponds precisely to one of the three calls to stream.getbyte() in this version. So there’s still a piece of data in the program tracking which of those ‘states’ we’re in – but it’s the program counter, and doesn’t need to be a named variable with a set of explicit named or numbered state values."
  On extending the code: adding a feature to the state machine means "values in your state enumeration, coming up with names for them, checking the names weren’t already used, renaming other states if their names had become ambiguous, carefully writing transitions to and from existing states, etc. You can just casually write a loop, and the programming language takes care of the rest."
  On "inside out": "(I tend to think of the state-machine style as ‘turning the function inside out’, in a more or less literal sense: the calls to a ‘get byte’ function ought to be nested deeply inside the code’s control flow, but instead, we’re forced to make them the outermost layer, so that ‘now wait for another byte’ consists of control falling off the end of the function, and ‘ok, we’ve got one now, carry on’ is at the top.)"
  The payoff: "Using coroutines, you can write the code in this latter style, with the explicit state machine replaced by the implicit program counter, even if the rest of the program needs to work by passing each output byte to a function call. In other words, you can write this part of the program ‘the way it wants to be written’ – the way that is most convenient for the nature of what the code has to do. And you didn’t have to force the rest of the program to change its structure".
  (The quotation stops where my extract ended mid-sentence.)
  On threads as the modern alternative: "Each side really would be making a function call to provide an output byte or read an input byte, and there would be no contradiction, because the call stacks of the two threads are completely independent."
  On Python: "I talk about generators as if they were the coroutine system in Python, but in fact, they’re one of two".
  Source: [Simon Tatham, "Philosophy of coroutines"](https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/coroutines-philosophy/)
- Raymond Chen, "The implementation of iterators in C# and its consequences (part 1)", August 12, 2008: "Like anonymous methods, iterators in C# are very complex syntactic sugar. You could do it all yourself (after all, you did have to do it all yourself in earlier versions of C#), but the compiler transformation makes for much greater convenience. The idea behind iterators is that they take a function with yield return statements (and possible some yield break statements) and convert it into a state machine. When you yield return, the state of the function is recorded, and execution resumes from that state the next time the iterator is called upon to produce another object."
  On the generated class: "The enumerator class is auto-generated by the compiler and, as promised, it contains two internal members for the state and current object, plus a member for each parameter (including the hidden this parameter), plus a member for each local variable. The Current property merely returns the current object. All the real work happens in MoveNext."
  Source: [Raymond Chen, The Old New Thing](https://devblogs.microsoft.com/oldnewthing/20080812-00/?p=21273)
- Nystrom on the same C# transformation: "the compiler itself automatically generates a little hidden class exactly like our ConcatEnumerator up there. The actual runtime (the CLR) doesn’t have any support for yield return. It’s done purely by automatically generating code at compile time. It’s a large, delicious lump of syntactic sugar."
  Source: [Bob Nystrom, "Iteration Inside and Out, Part 2" (2013-02-24)](https://journal.stuffwithstuff.com/2013/02/24/iteration-inside-and-out-part-2/)
- Protothreads (Dunkels, Schmidt, Voigt, Alonso, SenSys 2006), abstract: "While event-driven programming can keep the memory overhead down, it enforces a state machine programming style which makes many programs difficult to write, maintain, and debug. We present a novel programming abstraction called protothreads that makes it possible to write event-driven programs in a thread-like style, with a memory overhead of only two bytes per protothread. We show that protothreads significantly reduce the complexity of a number of widely used programs previously written with event-driven state machines. For the examined programs the majority of the state machines could be entirely removed. In the other cases the number of states and transitions was drastically decreased. With protothreads the number of lines of code was reduced by one third."
  Source: [Dunkels et al., "Protothreads: Simplifying Event-Driven Programming of Memory-Constrained Embedded Systems"](https://dunkels.com/adam/dunkels06protothreads.pdf)
- Regenerator (Facebook) README: "This package implements a fully-functional source transformation that takes the syntax for generators/`yield` from ECMAScript 2015 or ES2015 and Asynchronous Iteration proposal and spits out efficient JS-of-today (ES5) that behaves the same way."
  Source: [facebook/regenerator README](https://github.com/facebook/regenerator)
- Rust RFC 2033 (experimental coroutines, 2017): "the feature of "stackless coroutines" in the compiler is precisely targeted at generating the state machine we wanted to write by hand above, solving our problem!"
  And: "The stackless coroutine feature can be used not only for futures but also other language primitives like iterators."
  The section heading itself is "State machines as "stackless coroutines"".
  Source: [Rust RFC 2033](https://github.com/rust-lang/rfcs/blob/master/text/2033-experimental-coroutines.md)
- Kotlin coroutines design (KEEP): "The strength of generators is in supporting arbitrary control flow, such as `while` (from the example above), `if`, `try`/`catch`/`finally` and everything else".
  Among use cases: "Communication protocols: implement each actor as a sequence rather than a state machine".
  Source: [Kotlin KEEP, "Coroutines" design document](https://github.com/Kotlin/KEEP/blob/master/proposals/coroutines.md)
- C++ (Gor Nishanov, P1364R0, 2018): "Fibers (sometimes called stackful coroutines or user mode cooperatively scheduled threads) and stackless coroutines (compiler synthesized state machines) represent two distinct programming facilities with vast performance and functionality differences."
  Source: [P1364R0, "Fibers under the magnifying glass"](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1364r0.pdf)
- Leijen, on what the compiler-transform route costs the language designer: "For iterators and async-await it is more complicated and I also need to implement special compiler transformations to turn regular code into stack restoring state machines etc. I also need to take special care that all of these features interact as expected, e.g. ensure that finally blocks from my exception handling code are not forgotten in the state machines for the iterator code. It is possible to do this, but it is a difficult road to travel. Moreover, I need to do all of this again for the next control flow abstraction that comes along."
  Source: [Daan Leijen, "Structured Asynchrony with Algebraic Effects", MSR-TR-2017-21](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/05/asynceffects-msr-tr-2017-21.pdf)

### Inferences
- The state-machine sources give the most concrete answer to "what problem did people hit": a component whose natural form is a loop that *pulls* input (or *pushes* output) has to be rewritten as a callback when another component owns the loop.
  The rewrite moves control state from the program counter into a variable, and the code "inside out".
  A generator lets the compiler do that rewrite, so the source stays in the direct form.
- Python's CPython does not compile generators to a state machine; it keeps the frame object alive on the heap and resumes it.
  The state-machine view is still exact as a model: the frame's instruction offset is the state field.
  (This is my inference from CPython's design; no source above states it for CPython.)

### Gaps
- I did not read the C# 2.0 specification's iterator-block section or Eric Lippert's iterator-block posts; Chen and Nystrom cover the same transformation.
- I did not fetch a primary statement of C++20's coroutine lowering beyond P1364's one-line characterization.

## 4. Internal versus external iteration (push versus pull)

### Takeaway
Internal iteration puts the producer in charge of the loop (it calls the consumer's callback); external iteration puts the consumer in charge (it calls `next()`).
Each side writes well when it owns the call stack, and only one side can own the one stack; converting push to pull needs a second stack or a reified frame, which is what a coroutine, a generator, a thread, or a continuation supplies.

### Cited Findings
- Nystrom, part 1 (2013-01-13), the two chunks of code: "When you’re iterating, you have two chunks of code in play: The code responsible for generating the series of values. The code that takes each value and does something with it. With external iterators, (1) is the type implementing the iterator protocol and (2) is the body of the for loop. In that style, (2) is in charge. It decides when to invoke (1) to get the next value and can stop at any time by breaking out of the loop. Internal iterators reverse that power dynamic. With an internal iterator, the code that generates values decides when to invoke the code that uses that value."
  Source: [Bob Nystrom, "Iteration Inside and Out"](https://journal.stuffwithstuff.com/2013/01/13/iteration-inside-and-out/)
- Nystrom, part 1, on why interleaving breaks internal iteration: internal iterators cannot interleave two sequences "unless you’re willing to reach for some heavy weaponry like threads or continuations. You’re up a creek sans paddle. This is, I think, a big reason why most mainstream languages do external [iterators]".
  "(It’s also probably why languages that do internal iterators also have continuations.)"
  Source: [Nystrom, part 1](https://journal.stuffwithstuff.com/2013/01/13/iteration-inside-and-out/)
- Nystrom, part 1, the diagnosis: "It appears we’re at a stalemate. External iterators rock for some things, internal at others. Why is there no solution that’s great at all of them? The issue boils down to one thing: the callstack. You probably don’t think about it like this, but the callstack is a data structure. Each stack frame—every function that you’re currently in—is like an object. The local variables are the fields in that object. You get another bit of extra data for free too: the current execution pointer. The callstack keeps track of where you are in your function."
  On the hand-written tree iterator: "When we converted that function to an external iterator, that fifty lines of boilerplate was just a reification of the data structures the callstack gave us for free. The IterateState class is exactly what each call frame stored. The tree field in it was the tree parameter in the printTree function. The step field was the execution pointer. The stack in TreeIterator was the callstack. The lesson here is that stack frames are an amazingly terse way of storing state. You don’t realize how much it’s doing for you until you have to write it all out by hand."
  On ownership: "It’s a question of who gets to control the callstack." And: "Whoever gets put on top of the stack is in the weaker position, because it must return all the way to the other one between each generated value. In some use cases, the generator of values needs that power (recursively walking a tree), and internal iterators work great."
  Source: [Nystrom, part 1](https://journal.stuffwithstuff.com/2013/01/13/iteration-inside-and-out/)
- Nystrom, part 2 (2013-02-24), the summary and the cure: "With external iterators, the code consuming values has control over the stack, so it works well with problems where most complexity is in consuming values. For example, short-circuiting or interleaving multiple iterators is trivial in an external iterator. Conversely, internal iterators put the code generating values in control. They excel when generating values is complicated, like walking a tree and iterating over the nodes. Now we’ll see some techniques to deal with each style’s shortcomings. The basic idea is reification. If you’ve got some data on the callstack that you want to hang onto, you need to find a place to store it."
  On generators: "Iterators/generators reify a stack frame for you, but they only reify one. If you want to have your iteration logic call other methods which also yield, you have to manually reify every level yourself by walking the sequence at each level."
  On Ruby fibers, which convert any internal iterator to an external one: "It doesn’t reify a stack frame like generators, it reifies the whole stack."
  Closing: "I don’t think this is a coincidence. If you look at iteration, it actually is about concurrency. You’ve got two “threads” of behavior: one that’s generating values and one that’s consuming them. You need to run these two threads together and coordinate them. That is concurrency. We’re just so used to it, that we don’t think of it that way."
  Source: [Nystrom, "Iteration Inside and Out, Part 2"](https://journal.stuffwithstuff.com/2013/02/24/iteration-inside-and-out-part-2/)
- Kiselyov, "Generators: the API for traversal, iteration and non-determinism" (okmij.org, page last updated June 8, 2026).
  Framing: "Generators, sometimes called iterators -- which abstract over control as functions abstract over operations -- took time to spread."
  History in brief: "By mid-1970s, they were connected to backtracking (generally, non-determinism) and modular on-demand processing; and by the end of 1970s, recognized as the most general control construct in programming languages. Also recognized by the end of 1970s was the simple version of generators: less expressive but strikingly elementary to implement, with no special run-time."
  Pull: "Pull generator is an object representing the current state of traversal of a collection -- with the method/property to obtain the current element, and the method, typically called something like next, to advance the traversal".
  Push needs no runtime: "push generators do not require any special run-time, heap allocation or any GC. They can be compiled for the single standard stack, and implemented even in C".
  The trade-off: "push and pull generators are two different ways to abstract out the traversal of a collection: one may say, push generators are top-down and pull generators are bottom up." "Both generators support nesting, but only pull generators support zipping, or side-by-side enumerating of several collections, with the constant per-element processing cost." "Early termination is quite simpler with pull generators."
  On resources: "Resource leaks is a persistent problem with pull generators. Push generator does all the traversal itself, from the beginning, allocating resources, to the end, freeing them. The life time of resources is predictable."
  On conversion: "Every pull generator can be converted to push generator, as we have already seen: every. The other way around is tricky: one generally needs some sort of suspension (coroutine, delimited control, which requires a run-time support). A sufficiently general and polymorphic push generator can be converted to pull without delimited control and run-time support; however, space and time performance per element is no longer be constant."
  On the theory: "push generators are related to fold and F-algebras, and pull -- to unfold and F-coalgebra."
  Zip and the fringe problem: "What pull generators can do, in contrast to push generators, is parallel loops, or zip: traversing two collections side-by-side." and, after the zip code, "We can now determine when two collections first differ, in their traversal order: the variant of the famous same-margin problem." (Sic; the page says "same-margin", evidently the same-fringe problem.)
  Source: [Oleg Kiselyov, "Generators: the API for traversal, iteration and non-determinism"](https://okmij.org/ftp/continuations/generators.html)
- de Moura and Ierusalimschy on the same limitation in constrained iterators: CLU's "parallel traversals of two or more data collections, for instance, are not possible", and for Sather, "asynchronous traversals, as required for merging data collections, have no simple solution."
  Source: [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)

### Inferences
- Python's generator answers the push/pull problem in a specific way: the producer is *written* in push style (it `yield`s from inside its own loops, as an internal iterator would call a callback), but it is *consumed* in pull style (`next()`), so `zip()` and early `break` work.
  The cost is Nystrom's "they only reify one" frame: a recursive producer must re-yield at each level (`yield from`).
- The samefringe problem (do two trees have the same leaves in order?) is the standard test case: it needs two traversals advanced in lockstep, which push iteration cannot do on one stack.
  With generators it is `all(a == b for a, b in zip_longest(leaves(t1), leaves(t2)))`, an inference, not a quotation.

### Gaps
- I did not read the Iterator chapter of *Design Patterns* (Gamma et al., 1994); its definitions of internal and external iterators and its remark about closures and coroutines are **unverified** here.
  The project has the GoF text locally (`C:\git\DesignPatternsCD\markdown\`, per project memory), which is the place to check.
- I did not read Kiselyov's "Towards the best collection API" (LL3 talk); the generators page above covers the same push/pull trade-off and links to it.
- No primary source on the samefringe problem's origin (it is usually credited to Hewitt or to the 1970s Lisp community) was checked.

## 5. Laziness and modularity: Hughes, and generators as on-demand evaluation

### Takeaway
Hughes describes lazy evaluation in operational terms that are a description of a generator pipeline: the producer runs "only ... long enough to deliver the output g is trying to read", then "f is suspended and g is run".
His claim for why it matters is modularity: it separates a producer of candidate answers from the selector and from the termination condition.

### Cited Findings
- Hughes, "Why Functional Programming Matters" (Chalmers memo 1984; revised versions 1989 and 1990), section 4, "Glueing Programs Together": "Recall that a complete functional program is just a function from its input to its output. If f and g are such programs, then (g . f) is a program which, when applied to its input, computes g (f input). The program f computes its output which is used as the input to program g. This might be implemented conventionally by storing the output from f in a temporary file. The problem with this is that the temporary file might occupy so much memory that it is impractical to glue the programs together in this way. Functional languages provide a solution to this problem. The two programs f and g are run together in strict synchronisation. F is only started once g tries to read some input, and only runs for long enough to deliver the output g is trying to read. Then f is suspended and g is run until it tries to read another input. As an added bonus, if g terminates without reading all of f’s output then f is aborted. F can even be a non-terminating program, producing an infinite amount of output, since it will be terminated forcibly as soon as g is finished. This allows termination conditions to be separated from loop bodies - a powerful modularisation. Since this method of evaluation runs f as little as possible, it is called “lazy evaluation”. It makes it practical to modularise a program as a generator which constructs a large number of possible answers, and a selector which chooses the appropriate one. While some other systems allow programs to be run together in this manner, only functional languages use lazy evaluation uniformly for every function call, allowing any part of a program to be modularised in this way. Lazy evaluation is perhaps the most powerful tool for modularisation in the functional programmer’s repertoire."
  Source: [John Hughes, "Why Functional Programming Matters"](https://www.cse.chalmers.se/~rjmh/Papers/whyfp.pdf)
- Hughes on the conventional alternative being one indivisible loop (section 4.1, of the Newton-Raphson FORTRAN): "This program is indivisible in conventional languages."
  Section 5, of the game-tree evaluator: "Since this efficiency depends on an interaction between maximise (the last function in the chain of compositions) and gametree (the first), it could only be achieved without lazy evaluation by folding all the functions in the chain together into one big one. This is a drastic reduction in modularity, but it is what is usually done."
  Section 5, on memory: the lazy pipeline "only constructs parts of the tree as maximise requires them. Since each part can be thrown away (reclaimed by the garbage collector) as soon as maximise has finished with it, the whole tree is never resident in memory."
  The thesis: "We have argued that functional languages are powerful primarily because they provide two new kinds of glue: higher-order functions and lazy evaluation."
  Source: [Hughes](https://www.cse.chalmers.se/~rjmh/Papers/whyfp.pdf)
- Kiselyov's generators page has a section titled "Simple Generators v. Lazy Evaluation", which I located but did not extract.
  Source: [Kiselyov, generators page](https://okmij.org/ftp/continuations/generators.html)

### Inferences
- Hughes's paragraph is the strongest single source for "why", even though it never mentions coroutines: "run together in strict synchronisation", "suspended", and "aborted" describe a generator pipeline in a strict language step for step, and "a generator which constructs a large number of possible answers, and a selector which chooses the appropriate one" uses the word "generator" in the same sense.
  His "While some other systems allow programs to be run together in this manner" admits that coroutine systems provide the same glue for the components that opt in.
- The contrast Hughes draws ("only functional languages use lazy evaluation uniformly for every function call") maps onto the generator's limit: in Python only functions written as generators get this glue, and a producer must opt in with `yield`.
- "Generators are lazy evaluation for a strict language" is therefore supportable as an inference from Hughes, restricted to sequences.

### Gaps
- I found no primary source that states in so many words that generators are "lazy evaluation for a strict language"; treat that phrasing as an inference, not a quotation.

## 6. Generators and algebraic effects: `yield` as an operation, the driver as a handler

### Takeaway
The effects literature treats `yield` as one instance of an effect operation and the consumer as one instance of a handler: Leijen defines `yield` as a one-line effect whose handler decides whether to `resume`, and Plotkin and Pretnar describe operations and handlers as dual ("effect constructors" and "effect deconstructors").
Generators can carry an effect system, but two limits recur in the sources: resumption is one-shot, and every function between the operation and the handler must itself be a generator.

### Cited Findings
- Plotkin and Pretnar, "Handling Algebraic Effects" (LMCS 2013; first version "Handlers of Algebraic Effects", ESOP 2009), abstract: "Algebraic effects are computational effects that can be represented by an equational theory whose operations produce the effects at hand. ... Algebraic effects include exceptions, state, nondeterminism, interactive input/output, and time, and their combinations. Exception handling, however, has so far received no algebraic treatment. ... We further generalise exception handlers to arbitrary algebraic effects. The resulting programming construct includes many previously unrelated examples from both theory and practice, including relabelling and restriction in Milner’s CCS, timeout, rollback, and stream redirection."
  The duality: "Conceptually, algebraic operations and effect handlers are dual: the former could be called effect constructors as they give rise to the effects; the latter could be called effect deconstructors as the computations they provide proceed according to the effects already created."
  Source: [Plotkin and Pretnar, arXiv 1312.1399](https://arxiv.org/abs/1312.1399)
- Pretnar, "An Introduction to Algebraic Effects and Handlers" (MFPS 2015 tutorial): "Algebraic effects are an approach to computational effects based on a premise that impure behaviour arises from a set of operations such as get & set for mutable store, read & print for interactive input & output, or raise for exceptions [16,18]. This naturally gives rise to handlers not only of exceptions, but of any other effect, yielding a novel concept that, amongst others, can capture stream redirection, backtracking, co-operative multi-threading, and delimited continuations".
  How a handler resumes: "whenever read is called, we ignore its unit parameter and capture its continuation in a function k that expects the resulting string and resumes the evaluation when applied."
  On why exceptions are the degenerate case: "Experience with exception handlers offer us no guidance here, because raised exceptions have no continuation".
  Source: [Matija Pretnar, tutorial PDF](https://www.eff-lang.org/handlers-tutorial.pdf)
- Leijen, "Algebraic Effects for Functional Programming" (MSR-TR-2016-29): "we show how algebraic effects generalize over common constructs like exception handling, state, iterators and async-await."
  "In particular, iterators and async-await are complex constructs that can lead to subtle interactions with other features and require complex compilation mechanisms [4]. Being able to generalize over them using a single well-founded abstraction is a huge win."
  Section 2.3, Iterators: "Many contemporary languages, like JavaScript or C#, have special syntax and compilation rules for iterators and the yield statement [43]. Algebraic effects generalize over this where the yield effect can be defined as: effect yield⟨a⟩{ yield( item : a) : () }".
  "Orthogonal to the iterators, we can define handlers that handle the yielded elements. For example, here is a generic foreach function that applies a function f to each element that is yielded and breaks the iteration when f returns False".
  Source: [Leijen 2016 tech report](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/algeff-tr-2016-v2.pdf)
- Leijen, "Structured Asynchrony with Algebraic Effects" (MSR-TR-2017-21), abstract: "Algebraic effect handlers generalize many control-flow abstractions that are implemented specially in most languages, like exception handling, iterators, or backtracking. In this article, we show how we can implement full support for asynchronous programming as a library using just algebraic effect handlers."
  On one-shot resumption: "multi-core OCaml (Dolan et al., 2015) supports a very efficient resume implementation by restricting it to one-shot resumes only."
  Source: [Leijen 2017](https://www.microsoft.com/en-us/research/wp-content/uploads/2017/05/asynceffects-msr-tr-2017-21.pdf)
- Dolan et al. 2017: "Algebraic effect handlers are a modular foundation for effectful programming, which separate the operations available to effectful programs from their concrete implementations as handlers."
  "They achieve the separation between operations and their handlers through the use of delimited continuations, allowing them to pause, resume and switch between different computations. They provide a structured interface for programming with delimited continuations [10], and can implement common abstractions such as state, generators, async/await, promises, non-determinism, exception handlers and backtracking search."
  On the monadic alternative splitting the world in two: "Some of the benefits of direct-style code can be achieved by rewriting direct-style functions into callbacks, using syntactic sugar such as Haskell’s do-notation for monads or F#’s async/await [32]. However, this separates functions which use such rewriting from those that do not, leading to awkward mismatches and code duplication: for instance, Haskell provides mapM, filterM and foldM because the ordinary map, filter and foldl functions do not work with monadic arguments. By contrast, effect handlers do not introduce an incompatible type".
  Source: [Dolan et al.](https://kcsrk.info/papers/system_effects_feb_18.pdf)
- Abramov, "Algebraic Effects for the Rest of Us" (2019): the effect operation as a resumable exception: "This is the part you can’t do with try / catch. It lets us jump back to where we performed the effect, and pass something back to it from the handler." and "This takes a bit of time to get comfortable with, but it’s really not much different conceptually from a “resumable try / catch”."
  On generators as the alternative and their limit: "JavaScript generators are similar: if you’re working with generators, things in the middle also have to be aware of generators."
  "Unlike async / await or Generators, algebraic effects don’t require complicating functions “in the middle”. Our enumerateFiles call could be deep within ourProgram, but as long as there’s an effect handler somewhere above for each of the effects it may perform, our code would still work."
  "You can also get a much higher fidelity effect implementation with generators but that means you’ll have to give up on the “transparent” nature of JavaScript functions and you’ll have to make everything a generator. Which is… yeah."
  Source: [Dan Abramov, overreacted.io](https://overreacted.io/algebraic-effects-for-the-rest-of-us/)
- Kobayashi and Kameyama (2025) prove that one-shot effect handlers can be macro-expressed by asymmetric coroutines, which is the formal backing for building one-shot handlers on coroutines: "2. We also prove that one-shot effect handlers can be macro-expressed by asymmetric coroutines."
  Their asymmetric coroutines are stackful in the sense of de Moura and Ierusalimschy's calculus, which they adopt ("we present the calculus AC for asymmetric coroutines, which are prevalent in modern programming languages").
  Source: [Kobayashi and Kameyama 2025](https://arxiv.org/abs/2509.11901)

### Inferences
- The mapping onto the chapter's model is direct: the generator is the handled computation, a yielded request is an operation (Plotkin and Pretnar's "effect constructor"), the driver is the handler ("effect deconstructor"), and `send()` is `resume`.
  `throw()` is a handler that raises into the continuation, and abandoning the generator (`close()`) is a handler that does not resume, the exception case Pretnar describes as having no continuation.
- The two limits follow from section 1.
  One-shot: a generator object is its own continuation and is consumed by resumption, so a handler for nondeterminism that resumes twice cannot be written on generators (Dolan names backtracking as the casualty).
  Every function in the middle must be a generator: Python generators are stackless, so an operation performed three calls deep reaches the handler only if each frame in between re-yields (`yield from`), the "hierarchy of auxiliary generators" of de Moura and Ierusalimschy, and Abramov's "you’ll have to make everything a generator."
- The formal result that a coroutine can express a one-shot handler assumes a stackful coroutine; for a stackless generator, the `yield from` chain is what supplies the missing stack, one frame at a time.

### Gaps
- I found no paper by Kiselyov specifically on "generators as effects" beyond his generators page; his "Freer Monads, More Extensible Effects" and the Eff/handler papers were not fetched.
- I did not find a primary academic source that implements effect handlers on Python generators; the `stateless` library the book uses is the practical example, and other researchers may cover it.

## 7. The stackless design and its consequence: function color, and why designers chose it anyway

### Takeaway
A stackless coroutine (Python, JavaScript, C#, Rust, Kotlin) saves only the frames that are written to suspend, so suspension spreads up the call chain as a syntactic marker: Nystrom's "function color".
Designers give three reasons for accepting it: tiny per-coroutine memory (only locals live across a suspension), no runtime stack switching (which matters for FFI and embedded targets), and compilation to an ordinary state machine with no special runtime.

### Cited Findings
- Nystrom, "What Color is Your Function?" (2015-02-01): "3. You can only call a red function from within another red function."
  The languages that escape it: "Three more languages that don’t have this problem: Go, Lua, and Ruby. Any guess what they have in common? Threads. Or, more precisely: multiple independent callstacks that can be switched between. It isn’t strictly necessary for them to be operating system threads. Goroutines in Go, coroutines in Lua, and fibers in Ruby are perfectly adequate."
  The root cause: "The fundamental problem is “How do you pick up where you left off when an operation completes”? You’ve built up some big callstack and then you call some IO operation. ... Once operation completes, you need to resume what you were doing. The usual way a language “remembers where it is” is the callstack. That tracks all of the functions that are currently being invoked and where the instruction pointer is in each one. But to do async IO, you have to unwind and discard the entire C callstack."
  "This is where the “red functions can only be called by red functions” rule comes from. You have to closurify the entire callstack all the way back to main() or the event handler."
  "But if you have threads (green- or OS-level), you don’t need to do that. You can just suspend the entire thread and hop straight back to the OS or event loop without having to return from all of those functions."
  Source: [Bob Nystrom, "What Color is Your Function?"](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)
- withoutboats, "Why async Rust?" (2023-10-15), defines the axis: "A stackful coroutine has a program stack in the same way that an OS thread has a program stack: as functions are called as part of the coroutine, their frames are pushed on the stack; when the coroutine yields, the state of the stack is saved so that it can be resumed from the same position. A stackless coroutine on the other hand stores the state it needs to resume in a different way, such as in a continuation or in a state machine. When it yields, the stack it was using is used by the operation that took over from it, and when it resumes it takes back control of the stack and that continuation or state machine is used to resume the coroutine where it left off."
  On color: "Both green threads and stackful coroutine mechanisms can avoid this outcome, because it’s that special syntax that is used to indicate that something special is happening to manage the stackless state of the coroutine".
  Why Rust dropped stackful green threads: "Switching code from executing on a green thread to running on the OS thread stack can be prohibitively expensive for FFI. Go just accepts this FFI cost; C# recently aborted an experiment with green threads for this reason. This was especially problematic for Rust, because Rust is designed to support use cases like embedding a Rust library into a binary written in another language, and to run on embedded systems that don’t have the clock cycles or memory to operate a virtual threading runtime."
  On generators specifically: Rust "can have generators using a yield statement like C#, compiling down to a fast state machine without requiring context switches, virtual functions or even closures. This would eliminate the difficulty of coding recursive traversals by-hand with external iterators."
  Source: [withoutboats, "Why async Rust?"](https://without.boats/blog/why-async-rust/)
- Nishanov, P1364R0 (2018), the memory argument: "Note that stackless coroutines only need to store locals that are live across suspend point which and frequently consume less than 64 bytes, even if they happen to call a function that requires 500k of stack, since a stackless coroutine uses the stack of the thread executing the coroutine."
  And: "Fibers have comparable memory footprint to that of the operating system threads saving about 1% due to not needing to save kernel context and kernel stack."
  Source: [P1364R0](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1364r0.pdf)
- Rust RFC 2033 states the design goal: "We've also ruled out traditional solutions like green threads due to their costs, so we just need a way to easily create the optimal state machine for a future that combinators would otherwise emulate."
  Source: [Rust RFC 2033](https://github.com/rust-lang/rfcs/blob/master/text/2033-experimental-coroutines.md)
- Kiselyov on the cheapest form, the push generator, which needs no suspension at all: it can "be compiled for the single standard stack, and implemented even in C".
  Source: [Kiselyov](https://okmij.org/ftp/continuations/generators.html)
- The stackful side, Project Loom: "Programmers are forced to choose between modeling a unit of domain concurrency directly as a thread and lose considerably in the scale of concurrency a single server can support, or use other constructs to implement concurrency on a finer-grained level than threads (tasks), and support concurrency by writing asynchronous code that does not block the thread running it."
  The goal: "Millions of fibers can be spawned in a single JVM instance, and programmers need not hesitate to issue synchronous, blocking calls, as blocking will be virtually free. In addition to making concurrent applications simpler and/or more scalable, this will make life easier for library authors, as there will no longer be a need to provide both synchronous and asynchronous APIs".
  On expressiveness: "continuations don't add expressivity on top of that of fibers (i.e., continuations can be implemented on top of fibers)."
  On nesting generators inside fibers, the case a stackless design avoids: "code running inside a continuation must be able to suspend not only the continuation itself, but an enclosing one (e.g., suspend the enclosing fiber). For example, a common use for continuations is in the implementation of generators."
  Source: [Project Loom proposal](https://cr.openjdk.org/~rpressler/loom/Loom-Proposal.html)
- Dolan et al. on the color problem in monadic style ("this separates functions which use such rewriting from those that do not, leading to awkward mismatches and code duplication") and the effect-handler answer ("effect handlers do not introduce an incompatible type"), which Multicore OCaml achieves with "a custom stack layout, efficiently supported by the runtime system".
  Source: [Dolan et al.](https://kcsrk.info/papers/system_effects_feb_18.pdf)

### Inferences
- The color of a Python generator function is the cost of stacklessness, and it is the same cost de Moura and Ierusalimschy describe for iterators ("hierarchy of auxiliary generators") and Abramov for effects ("make everything a generator").
  One design decision produces all three observations.
- The designers' reasons for stackless all come from one property: the suspended state is exactly the frame the programmer marked, so its size is known at compile time and nothing else needs to be saved.
  For Python, CPython's C stack interleaves with Python frames, which makes stack switching hard to add (greenlet does it outside the language); I have no primary source for Python's own stated reasons here, and the PEP researchers may.

### Gaps
- I did not find a statement from Python's designers (PEP 255, PEP 342, or Guido van Rossum's writing) explaining the stackless choice in these terms; the history researchers may have it.
- C#'s aborted green-threads experiment is reported by withoutboats; I did not read Microsoft's own write-up.

## 8. The general principle: which formulations the sources support

### Takeaway
The best-supported formulation is that **a function's position in its own control flow is state, and a generator lets that state stay in the program counter and the frame's locals instead of a variable the programmer maintains**.
Tatham, Nystrom, Chen, Dunkels, the Rust RFC, and Kotlin all say this in their own words, and it explains the other formulations: the producer and the consumer can both be written as the caller (Tatham) because the generator's frame outlives each call (Nystrom's "reify a stack frame"), which in continuation terms is a one-shot delimited continuation.

### Cited Findings
- "A function's position in its control flow is state."
  Tatham: "there’s still a piece of data in the program tracking which of those ‘states’ we’re in – but it’s the program counter, and doesn’t need to be a named variable with a set of explicit named or numbered state values." [Tatham, "Philosophy of coroutines"](https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/coroutines-philosophy/)
  Nystrom: "You get another bit of extra data for free too: the current execution pointer. The callstack keeps track of where you are in your function." and "The step field was the execution pointer." [Nystrom part 1](https://journal.stuffwithstuff.com/2013/01/13/iteration-inside-and-out/)
  Chen: "When you yield return, the state of the function is recorded, and execution resumes from that state the next time". [Chen](https://devblogs.microsoft.com/oldnewthing/20080812-00/?p=21273)
  Marlin, as quoted by de Moura and Ierusalimschy, gives both halves: local data persists, and execution carries "on where it left off". [de Moura and Ierusalimschy](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
- "The consumer and the producer both get to be written as the caller."
  Tatham states the problem in these terms ("which should be the caller and which should be the callee?") and the goal: "Both of the processes taking place here are easier to read when written as a caller, not as a callee." [Tatham, "Coroutines in C"](https://www.chiark.greenend.org.uk/~sgtatham/coroutines.html)
  Nystrom states the same conflict as stack ownership: "Whoever gets put on top of the stack is in the weaker position, because it must return all the way to the other one between each generated value." [Nystrom part 1](https://journal.stuffwithstuff.com/2013/01/13/iteration-inside-and-out/)
  Kotlin's "implement each actor as a sequence rather than a state machine" is the same idea applied to protocols. [Kotlin KEEP](https://github.com/Kotlin/KEEP/blob/master/proposals/coroutines.md)
- "Inverting control without inverting the code."
  Tatham: "It would be much nicer if we didn't have to turn either piece of code inside out," and the definition of "inside out" quoted in section 3. [Tatham](https://www.chiark.greenend.org.uk/~sgtatham/coroutines.html); [Tatham philosophy](https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/coroutines-philosophy/)
  Dunkels: event-driven code "enforces a state machine programming style"; protothreads let you "write event-driven programs in a thread-like style". [Protothreads](https://dunkels.com/adam/dunkels06protothreads.pdf)
- "The activation record's lifetime is decoupled from the call stack."
  Nystrom part 2: "Iterators/generators reify a stack frame for you, but they only reify one." and the stack/heap diagram in which the loop body sits on the stack and the "DesugaredIterator" sits on the heap. [Nystrom part 2](https://journal.stuffwithstuff.com/2013/02/24/iteration-inside-and-out-part-2/)
  Nishanov: "a stackless coroutine uses the stack of the thread executing the coroutine" and stores only "locals that are live across suspend point". [P1364R0](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1364r0.pdf)
  withoutboats: "When it yields, the stack it was using is used by the operation that took over from it". [withoutboats](https://without.boats/blog/why-async-rust/)
- "A subroutine is a special case of a coroutine."
  Conway, as reported by de Moura and Ierusalimschy: coroutines are "“subroutines who act as the master program”". [de Moura and Ierusalimschy](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)
  The usual wording ("Subroutines are special cases of more general program components, called coroutines") is attributed to Knuth, *The Art of Computer Programming*, vol. 1, section 1.4.2; **unverified**, I did not read TAOCP.
  Tatham credits Knuth with the solution: "His answer is to throw away the stack concept completely." [Tatham](https://www.chiark.greenend.org.uk/~sgtatham/coroutines.html)
- "Iteration is concurrency."
  Nystrom: "If you look at iteration, it actually is about concurrency. You’ve got two “threads” of behavior: one that’s generating values and one that’s consuming them. You need to run these two threads together and coordinate them." [Nystrom part 2](https://journal.stuffwithstuff.com/2013/02/24/iteration-inside-and-out-part-2/)
  Hughes says the same of lazy evaluation: "The two programs f and g are run together in strict synchronisation." [Hughes](https://www.cse.chalmers.se/~rjmh/Papers/whyfp.pdf)
- "Generators abstract over control as functions abstract over operations."
  Kiselyov: "Generators, sometimes called iterators -- which abstract over control as functions abstract over operations". [Kiselyov](https://okmij.org/ftp/continuations/generators.html)
- "Separate generation from selection and termination."
  Hughes: "This allows termination conditions to be separated from loop bodies - a powerful modularisation." and "a generator which constructs a large number of possible answers, and a selector which chooses the appropriate one." [Hughes](https://www.cse.chalmers.se/~rjmh/Papers/whyfp.pdf)
- "One mechanism instead of many special-purpose ones."
  Leijen: "Being able to generalize over them using a single well-founded abstraction is a huge win." [Leijen 2016](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/algeff-tr-2016-v2.pdf)
  de Moura and Ierusalimschy argue for full asymmetric coroutines "as a convenient general control construct, which can replace both one-shot continuations and multithreading with a single, and simpler, concept." [de Moura and Ierusalimschy](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)

### Inferences
- Ranking by support:
  (1) control position is state, kept in the program counter (six independent sources, from 2000 to 2023, in C, C#, Rust, Kotlin, and embedded C);
  (2) both sides written as the caller, or "not inside out" (Tatham states it as the problem; Nystrom, Dunkels, and Kotlin agree);
  (3) the frame outlives the call (Nystrom, Nishanov, withoutboats; this is the mechanism behind 1 and 2);
  (4) iteration is concurrency, two threads of control run in lockstep (Nystrom, Hughes, de Moura's producer/consumer framing).
  A chapter could state (1) as the principle, (2) as the problem it solves, and (3) as how the generator achieves it, which follows the "new thing, mechanism, relation" order the author's style rules ask for.
- Formulations the sources contradict or qualify:
  "A generator is a coroutine" without qualification: de Moura and Ierusalimschy call it an asymmetric, first-class, *non-stackful* coroutine that is "not powerful enough to constitute a general control abstraction".
  "A generator is equivalent to a one-shot continuation": the equivalence is proved for *full* (stackful) coroutines; a generator is a one-shot *delimited* continuation that captures one frame (James and Sabry's "one-shot or linearly used restrictions").
  Even for full coroutines, Kobayashi and Kameyama (2025) show the equivalence holds only with mutable state in the calculus; without it, asymmetric coroutines are strictly more expressive than one-shot handlers and one-shot delimited control.
  "Symmetric coroutines are more powerful than asymmetric ones": de Moura and Ierusalimschy call this a "common misconception"; the two are equal in power, and asymmetric ones are easier to use.
- The "why" that answers the author's question in one sentence, assembled from the sources: when two pieces of code each want to be the loop that calls the other, a language with one call stack forces one of them to be rewritten as a state machine, so a generator gives the producer its own suspended frame and lets the program counter hold the state the rewrite would have put in a variable.

### Gaps
- The Knuth wording "a subroutine is a special case of a coroutine" is unverified here; the history researchers may have TAOCP.
- I found no source that uses the phrase "inverting control without inverting the code"; it is a fair paraphrase of Tatham and Dunkels, not a quotation.
