# Generators let both loops keep their place

A generator exists because a function's position in its control flow is state, and call and return preserves that state for one side of an exchange.
When a producer and a consumer each have a loop, the side that returns after every item loses its position, and the programmer rebuilds it from a switch, flags, fields, or a stack stored as data.
**A generator's frame survives the return, so the producer's position stays in the instruction pointer and the locals, and both sides keep their loops.**
The problem was in print by April 1960, when the designers of IPL-V wrote that for a generator "two contexts of information in working storage must coexist" and "the strict hierarchy of routines and subroutines is violated" ([Newell and Tonge 1960](https://iiif.library.cmu.edu/file/Newell_box00004_fld00298_doc0001/Newell_box00004_fld00298_doc0001.pdf)).
Conway's 1963 coroutine paper shows the same fault in a subroutine that needs "a switch" to select its part "depending on the situation at the last call" ([Conway 1963](https://www.melconway.com/Home/pdf/compiler.pdf)).
CLU, Icon, and Sather each answered one version of the problem.
In 2001 PEP 255 chose the form that suspends one frame and returns to its caller, because CPython and Jython can each resume a frame object, while a full coroutine needs a stack of its own ([PEP 255](https://peps.python.org/pep-0255/)).
PEP 342, PEP 380, and PEP 492 then added an inbound channel, delegation, and a separate coroutine type, and all three kept the one-frame rule, which is the reason a generator needs a driver.
The theory literature supports one formulation above the others: control position is state, and a generator keeps it in the program counter in place of a variable the programmer maintains.
Of the 13 claims from chapter 45 that the researchers checked, five are confirmed as written, five hold with a precision note, two are partly confirmed, and one is wrong as worded: PEP 255 mentions neither Ralph Griswold nor "models".

## The core idea: a function's position in its control flow is state, and a return discards it

A running function holds two kinds of state.
One is its local variables.
The other is its position: the statement that runs next, inside the loops, branches, and recursive calls that led to that statement.
The call stack stores both, in a frame, for as long as the function has not returned.
A return discards the frame.

That rule is harmless until two pieces of code must take turns.
A producer computes items in a loop of its own, and a consumer processes them in a loop of its own.
One call stack holds one of the two loops open.
The side that calls keeps its frame across the call.
The side that is called returns to hand over each item, and its position goes with its frame.
On the next call it starts from the top and must work out where it was from data it saved for that purpose: a switch, a set of flags, a state field, or a list that stands in for the stack of a recursion.

Call and return offers three arrangements, and each gives something up.
The producer can call the consumer as a callback.
The consumer then saves its position in data.
The consumer can call the producer for one item at a time.
The producer then saves its position in data.
Or the producer can run to completion and store every item before the consumer starts.
That third arrangement keeps both loops, needs room for the whole sequence, and makes the consumer wait for the last item before it sees the first.
A fourth arrangement goes outside call and return and gives each side a stack, as a thread, a process, or a full coroutine does.

| Arrangement | Producer | Consumer | Consequence | Instances in the sections below |
|---|---|---|---|---|
| The producer calls a callback | Keeps its loop | Rebuilds its position on every call | The consumer's locals move into globals, static variables, or an object, and the consumer follows one producer at a time | IPL-V's subprocess (1960), Smalltalk's `do:`, the `tokeneater` callback in `tabnanny.py` |
| The consumer calls a "next item" operation | Rebuilds its position on every call | Keeps its loop | The producer's loops and recursion become fields, flags, and a stored path | Conway's switch (1963), Alphard's generator, C++ cursors, a class with `__next__()` |
| The producer runs to completion first | Keeps its loop | Keeps its loop | The whole sequence is stored, and the consumer sees the first item after the producer computes the last | Conway's tape, Jackson's intermediate file, a list |
| Each side has a stack | Keeps its loop | Keeps its loop | Each routine needs a stack and machine-specific code to switch stacks, or an operating-system thread or process | Simula, Unix pipes, threads, Stackless Python |
| A generator | Keeps its loop in a frame that outlives the return | Keeps its loop | The generator suspends in its own body, and control returns to the code that resumed it | CLU, Icon, Sather, Python |

A generator is a function whose frame survives its return to the caller.
At a `yield`, the function hands out a value and stops, and its locals and its position stay in the frame.
The next resumption continues at the statement after the `yield`.
The position stays where the language keeps it for every function, in the frame's instruction pointer, so the programmer writes a loop as a loop and a recursion as a recursion.

The problem appears when the two loops run at different rates: two inputs for one output, one input for many outputs, or groups whose boundaries differ.
When each call turns one input into one output, an ordinary function is enough.
Conway stated that condition in 1963 ("when its modules do not communicate with each other synchronously"), and Michael Jackson later called the mismatch a boundary clash ([Conway 1963](https://www.melconway.com/Home/pdf/compiler.pdf); [Jackson 2001](https://studfile.net/preview/429617/)).

The general construct is the coroutine, in which any routine can resume any other and each routine needs a stack of its own.
A generator is the restricted form.
It suspends in its own body, and control returns to the code that resumed it.
The restriction lets a language with one call stack implement the construct.
The restriction also creates the driver.
A generator cannot say who runs next, so some other code must resume it.

The items exchanged can be requests and answers as well as the values of a sequence.
A computation that needs a line of input, the time, or a network reply can yield a request in the middle of its body and keep its position while other code produces the answer.
Under call and return, that computation is split into callbacks, one for each point where an answer arrives.
Chapter 45's driver and the Effect system built on it use the generator for that purpose.
Conway's first description of a coroutine has that shape, since his routine B "runs for a while until it encounters a read command, which means it needs something from A" ([Conway 1963](https://www.melconway.com/Home/pdf/compiler.pdf)).

## 1960 to 1973: the problem is stated before the generator has its modern form

Every quotation in this report was read in the source its citation names, according to the researchers' notes of 2026-11-05, unless a label says otherwise.
*Secondary* marks words taken from another author's quotation of the source.
*Unverified* marks a statement the researchers were unable to confirm, and a later section collects those statements.

### IPL-V, 1960: two contexts must coexist, and the subroutine hierarchy holds one

The programming sense of the word "generator" starts in IPL-V, the list-processing language of Newell, Shaw, and Simon.
Newell and Tonge described it in Communications of the ACM in April 1960 ([Newell and Tonge 1960](https://iiif.library.cmu.edu/file/Newell_box00004_fld00298_doc0001/Newell_box00004_fld00298_doc0001.pdf)):

> A generator is a process that produces a sequence of outputs and applies to each output a specified process. The process that the generator applies is an input to the generator and is called the subprocess.

The stated purpose is a separation of the two halves of a loop:

> Thus, the generator, just like the "iteration" statements of algebraic compilers, accomplishes a separation of the "production of elements" part of a loop from the "processing" part.

The designers saw what the separation requires.
Each half has a working context, and both contexts must stay alive while control alternates between the halves:

> Generators are different from all other IPL processes in that two contexts of information in working storage must coexist in the computer that of the generator and that of the superprocess and subprocess. There is an alternation of both control and context between the generator and the subprocess. To produce an element of the sequence, the generator must be in control and its context should occupy the W's; to process the element, the subprocess must be in control and its context (the context of the super-routine) should occupy the W's. Hence the strict hierarchy of routines and subroutines is violated, and special pains have to be taken to see that information remains safe and that each process works in its appropriate context.

The text extracted from the scan shows no punctuation between "computer" and "that of the generator", where the printed page probably carries a dash.
The notes record other characters lost in that scan, so check the page before you quote the sentence.

IPL-V's answer was a set of routines that the author of a generator calls:

> To handle this special housekeeping, the GENERATOR HOUSEKEEPING processes are provided. These processes insure that the generator's context is hidden away before the subprocess is executed, and returned to the W's after the subprocess is completed.

The IPL-V generator therefore stays in control of the loop and calls the consumer, the arrangement later called internal iteration.
The programmer saves and restores the generator's context around each call.
The subprocess can stop the generator early through a signal cell, so early exit is part of the design from the start.
Twenty-one years later the Icon designers traced the term to this language: "An early language that has generators is IPL-V [31], in which a generator is a subroutine that calls a processing routine to operate on each object in a data structure" ([Griswold, Hanson, Korb 1981](https://drh.github.io/documents/generators-in-icon.pdf)).

### Conway, 1963: a subroutine needs a switch to record "the situation at the last call"

Melvin Conway's "Design of a Separable Transition-Diagram Compiler" appeared in Communications of the ACM in July 1963 ([Conway 1963](https://www.melconway.com/Home/pdf/compiler.pdf)).
Its example is a routine that reads cards and replaces each pair of adjacent asterisks with one exponentiation character.
Two characters in can mean one character out, so the input loop and the output loop run at different rates.
Written as a subroutine that its caller invokes for each output character, the routine needs a variable that records where it stopped:

> Notice that the simple requirement of compressing asterisks requires the introduction of a switch which bifurcates the subroutine and selects the part to be used at each call depending on the situation at the last call. The reason for the switch is that each call of the subroutine must result in output of exactly one character. A programmer well versed at inventing counterexamples could dream up a requirement for a subroutine which would necessitate an absurd arrangement of switches in order to preserve the one-output-for-each-call relationship required of the subroutine.

Conway's coroutine removes the switch by keeping the routine's position in the calling sequence:

> The coroutine approach to the same problem accomplishes the switching job implicitly by use of the subroutine calling sequence. When coroutines A and B are connected so that A sends items to B, B runs for a while until it encounters a read command, which means it needs something from A. Then control is transferred to A until it wants to "write," whereupon control is returned to B at the point where it left off.

On the Burroughs 220, each coroutine gets one extra jump instruction, its "router", which holds the address at which the coroutine resumes.
Conway calls the router "a generalization of the switch of Figure 1".
The saved position moves from a data switch that the programmer tests into a jump address that the linkage maintains.

The paper's definition says what the linkage gives the programmer:

> Under these conditions each module may be made into a coroutine; that is, it may be coded as an autonomous program which communicates with adjacent modules as if they were input or output subroutines. Thus, coroutines are subroutines all at the same level, each acting as if it were the master program when in fact there is no master program.

Conway states the condition under which a coroutine helps: "The coroutine notion can greatly simplify the conception of a program when its modules do not communicate with each other synchronously."
He describes the third arrangement of the table as well.
With no change to either module, A can "write all its items on a tape", rewind the tape, and let B read it, so one pair of modules runs as one pass or as two.
His practical motive was memory.
The abstract offers "a collection of space-saving techniques", and the coroutine linkage replaces the tape between two passes.

Two details of the common account differ from the paper.
The paper dates the compiler work to 1961, at Case Institute of Technology, and a footnote says Conway and Joel Erdwinn developed the idea concurrently.
The year 1958 and the "assembly program" in which Conway is said to have first used a coroutine come from Knuth's history note in The Art of Computer Programming.
The researchers reached that note through Wikipedia and did not read Knuth's wording ([Wikipedia, "Coroutine"](https://en.wikipedia.org/wiki/Coroutine)).
The often-repeated definition "subroutines who act as the master program" is a paraphrase by de Moura and Ierusalimschy, and the printed sentence is the one quoted above ([de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)).

### Simula, Conniver, Jackson, and Unix pipes give the saved position four more forms

Simula made the saved position a named part of the language.
Nygaard and Dahl describe SIMULA I of 1964 ([Nygaard and Dahl 1978](https://hannemyr.com/cache/knojd_acm78.pdf)):

> Each temporarily inactive process had a "reactivation point" (represented by a system variable local to the process) which identified the program point where control should resume operations next time it entered the process.

Simula also met the implementation problem that shapes every later design.
Processes that suspend inside nested procedure calls need data stacks that "grow and shrink independently" ([Nygaard and Dahl 1978](https://hannemyr.com/cache/knojd_acm78.pdf)).
Dahl recalled that "it would be necessary to break out of the strict LIFO regime of block instances in Algol", so Simula replaced the stack with "a list structured free store" ([Dahl 2001](https://www.mn.uio.no/ifi/english/about/ole-johan-dahl/bibliography/the-birth-of-object-orientation-the-simula-languages.pdf)).

The restricted form got its name in this period.
An asymmetric coroutine is invoked by a caller and suspends back to that caller.
De Moura and Ierusalimschy credit the name *semi-coroutine* to Dahl and Hoare's 1972 chapter "Hierarchical Program Structures": "Asymmetric coroutine mechanisms (more commonly denoted as semi-symmetric or semi coroutines [Dahl et al. 1972]) provide two control-transfer operations: one for invoking a coroutine and one for suspending it, the latter returning control to the coroutine invoker" ([de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)).
The researchers did not read the 1972 chapter, so the attribution rests on that citation and on a search summary of a 1985 paper by Samet ([Samet 1985](https://www.cs.umd.edu/users/hjs/pubs/SametIPL85.pdf)).
Tim Peters wrote in 1999 that Knuth "describes generator behavior as "semi-coroutine"", and that attribution is unchecked against Knuth's text ([python-dev, 5 July 1999](https://mail.python.org/pipermail/python-dev/1999-July/000467.html)).

Conniver (McDermott and Sussman, MIT, 1972) is the first design in the notes whose generator returns values, stays alive, and resumes later.
Its manual states the need ([Conniver Reference Manual](<https://www.saildart.org/CNVR.RPO[UP,DOC]>)):

> What is needed is a way of returning some of the possibilities while maintaining the generator in existence for further duty if required.

The manual gives three reasons.
Generating each possibility may be "much more expensive" than trying it, and "the generator has no idea how many possibilities its superior wants".
Those two reasons return in PEP 255 in 2001.
The third reason is that "the generation of successive possibilities may depend on what the calling function did with the previous ones", and it returns in PEP 342 in 2005.
Conniver's primitive AU-REVOIR returns values together with "a pointer to the generator's activation", and TRY-NEXT resumes that activation, "including its bindings and context".
A message can travel the other way, through "an optional message argument to TRY-NEXT that it sends to the generator, which is returned, in the generator's activation, as the value of AU-REVOIR".
That channel has the shape of Python's `send()`.
No source in the notes connects Conniver to Python, so treat both resemblances as readings and not as a lineage.

Michael Jackson's program inversion is the coroutine written as a design method for a language that lacks coroutines.
When two data structures group the same items differently, his method writes two simple programs joined by an intermediate stream and then converts one program into a subroutine that the other calls for each record.
The quotations here come from an unofficial copy of his 2001 paper, because the author's own copy failed to load ([Jackson 2001](https://studfile.net/preview/429617/)).
The result is that "procedures with internal state can be designed as if they were main programs processing sequential message streams".
Jackson ties the technique to the restricted coroutine: "The idea of program inversion is closely related to the Simula [Dahl 70] concept of semi-coroutines, and, of course, to the later Unix notion of pipes as a flexible implementation of sequential files."
Daniel Jackson's 2009 introduction to Hoare's 1977 report gives the reason the transformation existed: "COBOL, of course, did not provide coroutines, so JSP offered a program transformation (automated by the JSP-COBOL tool) that converted stream reads and writes into calls, and let the programmer choose whether the reader or writer had initiative without changing to the code" ([Hoare 1977, edited by D. Jackson 2009](https://groups.csail.mit.edu/sdg/pubs/2009/hoare-jsp-3-29-09.pdf)).
The introduction describes the practice that inversion replaced as "the use of flags and complex control flow, resulting in a bug-ridden program with little semblance of structure".

Unix pipes supply the table's fourth arrangement at the level of the operating system.
McIlroy said in 2016 that "Pipes came out of an interest in coroutines", because "Coroutine connections look very much like I/O" ([McIlroy 2016](https://www.usenix.net/system/files/login/articles/login_spring16_05_mcilroy.pdf)).
Ritchie wrote that "the pipeline is merely a specific form of coroutine" ([Ritchie 1979/1984](https://courses.cs.washington.edu/courses/cse550/20au/papers/CSE550.ritchie84evolution.pdf)).
McIlroy's talking calculator shows what the intermediate file loses:

> You can replace an intermediate file with a pipe, but not always vice versa. An interactive session, such as dc|speak (a talking desk calculator), won't work if it has to treasure up all the output of dc before running speak.

These sources add two refinements to the core idea.
Which side loses its position is a choice.
Jackson's method inverts either program, and the JSP-COBOL tool let the programmer pick "whether the reader or writer had initiative".
The usual workaround of the period was the intermediate tape.
The rewritten routine was the exception, and the term "state machine" for it is later vocabulary.
Conway writes "switch" and "router", and Jackson's commentators write "flags".
Among the notes' sources, "state machine" first appears in the python-dev posts of 1999 and then in PEP 255.

## CLU, Icon, and Sather answer three different problems with one construct

### CLU, 1975 to 1979: reach the elements of a hidden collection one at a time, on one stack

CLU's iterator came from data abstraction.
In the summer of 1975 the CLU group visited the Alphard group at Carnegie Mellon and saw Alphard's generator, a form with a group of operations that a `for` statement calls.
Liskov's history records the reaction ([Liskov 1992](https://publications.csail.mit.edu/lcs/pubs/pdf/MIT-LCS-TR-561.pdf)):

> We were intrigued by generators since they solved some problems with data abstractions, but we thought they were too complicated. Russ Atkinson designed iterators on the airplane going back to Boston after this meeting and described them in a design note in September 1975 [Atkinson, 1975].

The researchers did not read the Alphard papers, so the description of Alphard here is Liskov's.
She states the problem that both constructs solve:

> The problem is that for some types there is no obvious way to get to the elements. For arrays, you can use indexes; for lists, you can follow links. But for sets it's not clear what to do. What you would like is an operation of the type to provide the elements. Such an operation could be a procedure that returns an array containing the elements, but that is expensive if the collection is large. Instead, it would be nice to get at the elements one at a time.

A CLU iterator is one procedure-like operation that contains `yield` statements, and a `for` statement is the one construct that can invoke it.
The 1977 paper calls the result "a complete decomposition of the two activities", which are selecting the next object and acting on it, and adds that "the entire collection need not physically exist" ([Liskov et al. 1977](https://web.eecs.umich.edu/~weimerw/2008-615/reading/liskov-clu-abstraction.pdf)).
After each `yield`, "the iterator is resumed at the statement following the yield statement, in the same environment as when the objects were yielded".

CLU keeps both contexts alive on one stack by turning the call around.
The iterator's frame stays on the stack, and each `yield` runs the loop body as a nested call.
Liskov gives the reason and says what the design gives up ([Liskov 1992](https://publications.csail.mit.edu/lcs/pubs/pdf/MIT-LCS-TR-561.pdf)):

> Iterators are related to coroutines; the iterator and the body of the for loop pass control back and forth. However, their use is limited so that CLU programs can make do with a single stack. They are inexpensive: a yield effectively calls the loop body, which returns to the iterator when it is finished. (Calls are very cheap in CLU.) Imposing the limitations on iterators was done to get the efficient, single stack implementation, albeit at the expense of some expressive power. For example, iterators cannot be used to compute whether two lists have the same elements, since to do this you need to iterate through the two lists side-by-side, and CLU only allows iterators to be nested.

The comparison that CLU rules out recurs through the rest of this history: two collections walked side by side.
Among the designs in the notes, CLU is where the keyword `yield` enters the lineage.

### Icon, 1978 to 1981: take backtracking out of the pattern sublanguage

Icon's generators came from string processing and search.
The Icon designers state the fault of earlier string languages, with SNOBOL4 as their example ([Griswold, Hanson, Korb 1981](https://drh.github.io/documents/generators-in-icon.pdf)):

> Briefly stated, the major issue is that, in most languages, string manipulation facilities constitute a separate sublanguage, and interaction between the sublanguage and the language proper is awkward at best. In addition, if the facilities include a search and backtrack mechanism, its use is usually restricted to the sublanguage, and the programmer typically has little control over its operation.

Icon makes the search mechanism part of ordinary expression evaluation.
"A generator is an expression that is capable of producing a sequence of values", any expression can be one, and the failure of an operation resumes a dormant generator for its next value.
A procedure becomes a generator through `suspend`:

> The expression `suspend e` is similar to `return e`, except that the procedure activation is left in suspension so that it may be resumed for additional computation. Execution of the procedure body is resumed at the point of suspension if the context in which the procedure invocation occurs requires another alternative.

The Icon book describes a suspended expression in words that fit a Python generator ([Griswold and Griswold, The Icon Programming Language, 3rd ed.](https://www2.cs.arizona.edu/icon/ftp/doc/lb1up.pdf)):

> An expression that produces a value and may be capable of producing another one suspends. Instead of just producing a value and "going away", it keeps track of what it was doing and remains "in the background" in case it is needed again.

Icon's generators can appear in any expression, and the 1981 paper holds CLU and Alphard to that standard.
In those languages, it says, "generators are only accessible in a specific context: a particular type of for statement".
An Icon generator is still tied to the expression that contains it.
The book says that in normal evaluation "there is no mechanism for explicitly resuming an expression to get a result", and it introduces a construct that removes the tie: "A co-expression "captures" an expression so that it can be explicitly resumed at any time and place."
It adds that co-expressions "also can be used as coroutines".

### Sather, 1993 to 1996: write the iterator "in an active style" and walk two structures at once

Sather's designers started from the cursor objects of C++ and of the first Sather, which are the table's second arrangement.
Their paper states the goal in one sentence ([Murer et al. 1995](https://steveomohundro.com/wp-content/uploads/2009/03/murer_omohundro95_iteration_abstraction_in_sather.pdf)):

> Another goal for the iterator design was to allow iterators to be programmed in an active style, without having to explicitly encode the control structure as state, as is required for cursors and most other iteration constructs.

The paper says what cursors require: a second class hierarchy beside the containers, objects to create and collect, and storage that "is explicit", so that "it is inconvenient to use them to describe nested or recursive control structures".
Sather takes CLU's iterator and removes three limits, which the paper lists as "One iterator per loop", "No way to modify elements", and "Iterator arguments are loop invariant".
A Sather iterator call can appear anywhere in a loop, so one loop can step through two structures.
A "hot" argument is "reevaluated each time the control is passed back to the iterator", which passes a new value in at each resumption.

A Sather iterator stays bound to one call point in one loop.
The paper calls iterators "structured coroutines" and separates them from generators on that ground:

> Coroutines with this added restriction of always returning to their caller are sometimes called generators, semicoroutines, or hierarchical coroutines [8]. Iterators share this property. However, just as for streams, a generator's activation state is not bound to a single call point within a single loop. Instead, a generator may be left in a half-consumed state at one point and picked up at another.

By that definition Python's construct is a generator, and the constructs of CLU and Sather are iterators.

### The test that separates the designs: two traversals in step

One problem sorts these designs.
The *samefringe* problem asks whether two trees have the same leaves in the same order.
Each tree walk is a recursion in progress, and the comparison needs both recursions suspended at once.
Liskov's example of what a CLU iterator cannot compute, whether two lists have the same elements, is the problem in its simplest form.
The Sather paper solves samefringe with two iterators in one loop and says why a callback design fails: "it is not possible to pass the body of the routine to one of the trees for execution" ([Murer et al. 1995](https://steveomohundro.com/wp-content/uploads/2009/03/murer_omohundro95_iteration_abstraction_in_sather.pdf)).
The Icon book runs two generators in step with co-expressions.
Tim Peters brought the problem to python-dev in May 1999, with solutions in Icon, Python, and Scheme ([python-dev, 20 May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095254.html)).
He returned to it in January 2001 as the case that shows why a generator object must work "divorced from "for"" ([python-dev, 31 January 2001](https://mail.python.org/pipermail/python-dev/2001-January/012402.html)).

The designs differ in where the suspended producer lives, and that location decides the result of the test.
IPL-V saves the generator's context with housekeeping routines.
CLU nests the loop body on the iterator's stack, so one producer runs at a time.
Icon and Sather keep several suspended producers alive inside one expression or one loop.
Conniver, Icon's co-expressions, and Python make the suspended producer a value that a program can store, pass, and resume from any point.

## Python, 1999 to 2001: PEP 255 picks the form that one frame object can implement

### The debate starts from callbacks and stalls on the C stack

The python-dev discussion that led to generators began with callbacks.
On 13 May 1999 Sam Rushing asked for a "stackless" interpreter that would let his Medusa server use coroutines or continuations.
He described the alternative as "the need to program in continuation-passing-style (callbacks, callbacks to callbacks, state machines, etc...)" ([python-dev, 13 May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095192.html)).
The next day he called his server code "a horrible, complicated mess" with "three levels of callback state" ([python-dev, 14 May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095199.html)).

Tim Peters answered over the following weeks with one position.
Python needs the restricted form, and the restricted form is easy to build.
His criterion is the direction of return ([python-dev, 15 May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095208.html)):

> The thing that makes generators so much easier is that they always return directly to their caller, at the point of call; so no C frame can get stuck in the middle even under today's implementation; it just requires not deleting the generator's frame object, and adding an opcode to *resume* the frame's execution the next time the generator is called.

A full coroutine names the routine that runs next, so control stops following the stack.
In Peters's words, "each coroutine needs its own stack (a generator only has one stack *frame*-- its own --to worry about), and C-calling-Python can get into the act" ([python-dev, 22 May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095277.html)).
In CPython a C function can sit between two Python frames, and a suspended coroutine must preserve that stretch of the C stack.

Peters wrote the chapter's two phrases in those weeks.
On 22 May 1999 he wrote: "Generators are really "half a coroutine", so this doesn't show the full power (other examples in the post do). co.detach is a special way to deal with this asymmetry" ([python-dev, 22 May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095276.html)).
The quotation marks around "half a coroutine" are his, which suggests a stock phrase, and the researchers found no earlier source for it.
On 8 July 1999 he described "the simplest possible version of generators ("resumable function")" and hoped that "someday somebody will remember they don't need to turn Python inside out to get just that much" ([python-dev, 8 July 1999](https://mail.python.org/pipermail/python-dev/1999-July/000485.html)).

His statement of the motive, from 5 July 1999, is the strongest in the Python record ([python-dev, 5 July 1999](https://mail.python.org/pipermail/python-dev/1999-July/000467.html)):

> Because a generator remembers where it is and what its locals are, its state and "what to do next" don't have to be encoded in global data structures then decoded from scratch upon entry. That is, whenever you build a little (or large!) state machine to figure out "what to do next" from a collection of persistent flags and state vrbls, chances are good there's a simple algorithm dying to break free of that clutter <wink>.

That message gives the mechanism in two sentences: "When a generator suspends, it's exactly like a return today except we simply decline to decref the frame. That's it!"

Guido van Rossum's recorded objections concern the general forms.
He refused anything that "assumes knowledge about how the C compiler and/or the CPU and OS lay out the stack" ([python-dev, 14 May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095200.html)).
He wrote that "continuations are too complicated for most programmers. (This comes from the realization that they are too complicated for me!)" ([python-dev, May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095197.html)).
For two years the simple form waited behind the general one.
Peters wrote in August 2000 that generators "keep getting hijacked by continuations" ([python-dev, 6 August 2000](https://mail.python.org/pipermail/python-dev/2000-August/007975.html)).
The notes hold no 2001 message in which Van Rossum says why generators were accepted and Stackless was set aside.
His reasons are assembled from the 1999 posts, PEP 255's paragraph on Stackless, and a 2004 retrospective ([python-dev, 1 June 2004](https://mail.python.org/pipermail/python-dev/2004-June/045089.html)).

The patch came out of a question about Jython.
On 16 March 2001, in a thread about the Stackless proposal, Peters asked a Jython developer whether Jython has "an explicit object akin to CPython's execution frame" and added: "If so, 96.3% of what's needed for generators is already there" ([python-dev, 16 March 2001](https://mail.python.org/pipermail/python-dev/2001-March/013631.html)).
Neil Schemenauer replied within hours that he almost had generators working.
He posted an implementation the same day, built on the design that Peters and Van Rossum had worked out in July 1999 ([python-dev, 16 March 2001](https://mail.python.org/pipermail/python-dev/2001-March/013636.html)).
Samuele Pedroni confirmed the limit from the Jython side two days later: "Freezing more than a frame is not directly possible in jython, frames are pushed and popped on java stack" ([python-dev, 18 March 2001](https://mail.python.org/pipermail/python-dev/2001-March/013663.html)).
PEP 255 was created on 18 May 2001, and Van Rossum checked the patch into a branch on 15 June 2001 ([python-dev, 15 June 2001](https://mail.python.org/pipermail/python-dev/2001-June/015440.html)).

### PEP 255 judges each alternative by which side it leaves natural

PEP 255's Motivation opens with the problem in one sentence ([PEP 255](https://peps.python.org/pep-0255/)):

> When a producer function has a hard enough job that it requires maintaining state between values produced, most programming languages offer no pleasant and efficient solution beyond adding a callback function to the producer's argument list, to be called with each value produced.

The PEP then takes five alternatives in turn and judges each by which side it leaves in its natural form.
The callback, as in `tokenize()` with its `tokeneater` argument, "allows tokenize to be coded in a natural way", while its callers are "convoluted by the need to remember between callbacks which token(s) were seen last".
The PEP's example of such a caller is `tabnanny.py`, "maintaining a state machine in global variables".
A complete list lets clients use "local variables and local control flow (such as loops and nested if statements) to keep track of their state".
The PEP rejects the list because "no a priori bound can be placed on the memory" and because a client that needs an early token waits for the whole parse.
An iterator object pleases the caller and "shifts the burden on tokenize to remember *its* state between ``.next()`` invocations".
For a recursive producer, the iterator form "requires removing the recursion manually and maintaining the state of the traversal by hand".
Threads allow "both to maintain their states in natural ways", but they are missing on some platforms and "very slow" on the rest.
Stackless coroutines give the benefit of threads with more efficiency, and the PEP sets them aside in one sentence: "However, Stackless is a controversial rethinking of the Python core, and it may not be possible for Jython to implement the same semantics."

The PEP then says what the earlier languages share:

> Some other high-level languages provide pleasant solutions, notably iterators in Sather, which were inspired by iterators in CLU; and generators in Icon, a novel language where every expression *is a generator*. There are differences among these, but the basic idea is the same: provide a kind of function that can return an intermediate result ("the next value") to its caller, but maintaining the function's local state so that the function can be resumed again right where it left off.

Its two references for that sentence are the Sather paper and the Icon home page.
The PEP mentions no person in connection with Icon, and its word for the three languages' constructs is "solutions".
The conclusion is stated against the thread option: "As in the thread approach, this allows both sides to be coded in the most natural ways; but unlike the thread approach, this can be done efficiently and on all platforms."
The specification says what a suspended generator retains: "all local state is retained, including the current bindings of local variables, the instruction pointer, and the internal evaluation stack".

### What Python adds to Icon, and what the one-way design leaves out

Python's generator differs from Icon's in a way that matters for chapter 45.
Kuchling's "What's New in Python 2.2" states the difference ([What's New in Python 2.2](https://docs.python.org/3/whatsnew/2.2.html)):

> One novel feature of Python's interface as compared to Icon's is that a generator's state is represented as a concrete object (the iterator) that can be passed around to other functions or stored in a data structure.

Peters made the point in April 2001, when the iterator protocol of PEP 234 entered the 2.2 source tree, a month before PEP 255 was created.
He wrote that "having an explicit iterator object "should" make it possible to go beyond Icon's notion of generators (which can only be driven implicitly by control context)" ([python-dev, 21 April 2001](https://mail.python.org/pipermail/python-dev/2001-April/014412.html)).
A suspended function that any code can hold and resume is the precondition for a driver that you write.

The 2001 design sends values one way, and two of its rules follow from that direction.
A `yield` was illegal inside the `try` of a `try`/`finally`, because "there's no guarantee the generator will ever be resumed, hence no guarantee that the finally block will ever get executed".
A generator ended with a bare `return`, because "it's simply cleaner to use ``yield`` exclusively for delivering values".
The caller had no way to tell an abandoned generator to clean up, and the generator had no channel for a final result.
PEP 342 and PEP 380 lifted both rules.

Kuchling's summary supplies the term in the chapter's epigraph: "What if you could later resume the function where it left off? This is what generators provide; they can be thought of as resumable functions."

## 2005 to 2015: three PEPs add channels to the generator and keep the one-frame rule

### PEP 342: values and exceptions travel in, for two separate reasons

PEP 342 (Guido van Rossum and Phillip J. Eby, created 10 May 2005, Python 2.5) starts from what a PEP 255 generator lacks ([PEP 342](https://peps.python.org/pep-0342/#motivation)):

> Python's generator functions are almost coroutines -- but not quite -- in that they allow pausing execution to produce a value, but do not provide for values or exceptions to be passed in when execution resumes. They also do not allow execution to be paused within the `try` portion of `try/finally` blocks, and therefore make it difficult for an aborted coroutine to clean up after itself.

The Motivation adds a third limit: generators "cannot yield control while other functions are executing, unless those functions are themselves expressed as generators".
The uses it lists are "simulations, games, asynchronous I/O, and other forms of event-driven programming or co-operative multitasking".
The two alternatives it rejects are "the entire application as a series of callbacks" and "resource-intensive threads".
Rushing's 1999 complaint about callbacks got its answer here, six years later, from the construct that Peters had advocated.

`yield` became an expression so that a value can arrive at the point of suspension.
The PEP describes the result in a phrase that fits a request to a driver ([PEP 342](https://peps.python.org/pep-0342/#new-syntax-yield-expressions)):

> In effect, a yield-expression is like an inverted function call; the argument to yield is in fact returned (yielded) from the currently executing function, and the *return value* of yield is the argument passed in via `send()`.

The three new methods have two origins.
`send()` and the yield expression come from the coroutine motive and from the data-passing half of Raymond Hettinger's PEP 288 of 2002.
`throw()` and `close()` come from cleanup, which Samuele Pedroni's PEP 325 of 2003 proposed, and from the `with` statement.
A generator that stands behind a `with` block must see the block's exception at its `yield`, and PEP 343 derives the rest from that need as a chain of small steps ([PEP 343](https://peps.python.org/pep-0343/#motivation-and-summary)):

> To enable this, a new `throw()` method for generators is proposed, which takes one to three arguments representing an exception in the usual fashion (type, value, traceback) and raises it at the point where the generator is suspended. Once we have this, it is a small step to proposing another generator method, `close()`, which calls `throw()` with a special exception, `GeneratorExit`. This tells the generator to exit, and from there it's another small step to proposing that `close()` be called automatically when the generator is garbage-collected. Then, finally, we can allow a yield-statement inside a try-finally statement, since we can now guarantee that the finally-clause will (eventually) be executed.

The generator as the code that drives other code appears in the proposal that PEP 343 replaced.
PEP 340 says "the key idea is using a generator to drive a block statement" ([PEP 340](https://peps.python.org/pep-0340/#introduction)).
PEP 342's third example reverses the roles, and a scheduler drives the generators: "A simple co-routine scheduler or *trampoline* that lets coroutines *call* other coroutines by yielding the coroutine they wish to invoke" ([PEP 342](https://peps.python.org/pep-0342/#examples)).
The trampoline's loop answers each yielded value.
A yielded generator is a call, any other yielded value is a result for the caller, and an exception returns to the caller through `throw()`.
The trampoline keeps the chain of callers in a stack that it builds as data, because each generator suspends one frame.

### PEP 380: code that contains `yield` can move into a helper

PEP 380 (Greg Ewing, created 13 February 2009, accepted in June 2011, Python 3.3) addresses the one-frame rule directly ([PEP 380](https://peps.python.org/pep-0380/#motivation)):

> A Python generator is a form of coroutine, but has the limitation that it can only yield to its immediate caller. This means that a piece of code containing a `yield` cannot be factored out and put into a separate function in the same way as other code.

A `for` loop that re-yields a helper's values forwards the values and drops `send()`, `throw()`, `close()`, and the helper's result.
`yield from` forwards all of them, and the PEP's expansion of one `yield from` expression runs to about 40 lines of Python.
A generator's `return` gained a value so that a helper behaves like a function: "One can reason about the behaviour of the resulting code by thinking of g as an ordinary function that can be suspended using a `yield` statement" ([PEP 380](https://peps.python.org/pep-0380/#generators-as-threads)).
Peters had described the chain in July 1999.
Under the one-frame rule a recursive generator re-yields at each level, "crawling up the stack each time there's a result" ([python-dev, 8 July 1999](https://mail.python.org/pipermail/python-dev/1999-July/000485.html)).
`yield from` automates that chain and keeps the rule.
Each function between the innermost `yield` and the driver is a generator.

### PEP 492: a separate type on the generator machinery

asyncio (PEP 3156, created in December 2012) built its scheduler on `yield from`: "A coroutine is a generator that follows certain conventions" ([PEP 3156](https://peps.python.org/pep-3156/#coroutines)).
Van Rossum gave his reason in a parenthesis: the scheduler is "For users (like myself) who don't like using callbacks".
PEP 492 (Yury Selivanov, created 9 April 2015, Python 3.5) keeps the machinery and separates the type.
It lists three shortcomings of generator-based coroutines ([PEP 492](https://peps.python.org/pep-0492/#rationale-and-goals)).
They are easy to confuse with generators.
A function becomes a coroutine, or stops being one, when a `yield` appears in its body or leaves it.
A suspension can occur only where `yield` is legal, which excludes the entry and exit of a `with` block and the step of a `for` loop.

The implementation is shared: "Coroutines are based on generators internally, thus they share the implementation. Similarly to generator objects, *coroutines* have `throw()`, `send()` and `close()` methods" ([PEP 492](https://peps.python.org/pep-0492/#coroutine-object-methods)).
The stated design goal is visibility: "to make it easy for users to see where the code might be suspended".
Glyph Lefkowitz makes that argument at length in "Unyielding" and reports that Van Rossum gave the same kind of example ([Lefkowitz 2014](https://blog.glyph.im/2014/02/unyielding.html)).
A sentence in Van Rossum's own words saying that a visible `yield from` marks each switch point remains unverified.

Two later PEPs complete the account.
PEP 479 turns a `StopIteration` that escapes a generator's body into a `RuntimeError`.
PEP 380 stores a generator's return value in `StopIteration`, and PEP 479 says a stray one "breaks the abstraction that a subgenerator may be factored out of a generator" ([PEP 479](https://peps.python.org/pep-0479/#rationale)).
PEP 525 gives `async for` a generator form and says that "the goals and rationale for PEP 255, applied to the asynchronous execution case, hold true for this proposal as well" ([PEP 525](https://peps.python.org/pep-0525/#rationale-and-goals)).

David Beazley's tutorials gave the request-and-answer reading its best-known form.
His 2009 course separates three uses of `yield`, which are iteration, receiving messages, and "A trap (cooperative multitasking)", and it builds a scheduler on the third: "In our code, the scheduler is the operating system and the yield statement is a trap" ([Beazley 2009, Wayback copy](https://web.archive.org/web/2016id_/http://www.dabeaz.com/coroutines/Coroutines.pdf)).
A later slide reads "Tasks do not see the scheduler • Tasks do not see other tasks • yield is the only external interface".
The deck's closing slide warns: "Do NOT write generator functions that try to do more than one of these at once".
The warning bears on a chapter whose generators yield requests and receive answers.
In Beazley's terms such a generator is a user of the trap, and its yielded values are requests to a scheduler, separate from the output of an iteration.

Across the three PEPs one pattern holds.
Each PEP supplies something the 2001 design left out: a way in for values and exceptions, a cleanup that is guaranteed to run, and a way to call a helper that yields.
Each keeps the rule that a generator suspends its own frame and returns control to the code that resumed it.

## The theory's principle: control state belongs in the program counter

### A generator is an asymmetric, first-class, stackless coroutine

De Moura and Ierusalimschy classify coroutines on three axes: symmetric or asymmetric transfer of control, first-class or constrained, and stackful or not ([de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)).
A *stackful* coroutine can suspend from inside nested calls.
Python's generator is asymmetric and first-class, and the paper places it on the other side of the third axis:

> Despite constituting a first-class object, a Python generator is not a stackful construct; it can only suspend its execution when its control stack is at the same level that it was at creation time. In other words, only the main body of a generator can suspend.

The two restrictions differ in effect.
The paper shows that symmetric and asymmetric coroutines can express each other, and it calls the opposite belief "the common misconception that symmetric and asymmetric coroutines have no equivalent power".
It finds asymmetric coroutines easier to follow, because "control is always transfered back to their invokers".
Stackfulness is the axis that changes what a construct can express.
The paper proves its equivalence between coroutines and one-shot continuations for *full* coroutines, which are first-class and stackful, and it judges the non-stackful generator "not powerful enough to implement user-level multitasking".

That 2004 judgment describes the PEP 255 generator, before `send()` and `yield from`.
Python later built multitasking on generators by making every function between a task and its scheduler a generator.
The paper describes that structure as "an hierarchy of auxiliary generators that yield in succession", and `yield from` automates it.
A 2025 paper by Kobayashi and Kameyama qualifies the equivalence for full coroutines as well: one-shot effect handlers and one-shot delimited-control operators "can be macro-expressed by asymmetric coroutines, but not vice versa" ([Kobayashi and Kameyama 2025](https://arxiv.org/abs/2509.11901)).

### In continuation terms, a suspended generator is the rest of one frame, resumable once

A continuation is "the remainder of a computation from a given point in the computation" ([Bruggeman, Waddell, Dybvig 1996](https://stanleymiracle.github.io/blogs/compiler/docs/chez-pub/22-call1cc.pdf)).
A delimited continuation is that remainder up to a boundary.
The Project Loom design document gives a working definition, "sequential code that may suspend (itself) and resume (be resumed by a caller)", and draws the line that places a Python generator: "stackless continuations may only suspend in the same subroutine as the entry point" ([Project Loom proposal](https://cr.openjdk.org/~rpressler/loom/Loom-Proposal.html)).
A suspended generator is therefore the remainder of one frame's body.
Its boundary is that frame, and the caller's stack lies outside it.

A generator resumes once because the generator object is its own continuation, and each resumption changes the object in place.
Loom's words for such a continuation are "non-reentrant" and "stateful".
Dolan and colleagues give the reason a one-shot rule protects correctness as well as speed: "operations that are begun once do not complete twice", so a `finally` block or the exit of a `with` block runs one time ([Dolan et al. 2017](https://kcsrk.info/papers/system_effects_feb_18.pdf)).
James and Sabry's 2011 paper says the `yield` operators of mainstream languages are "one-shot or linearly used restrictions" of delimited continuations.
The researchers read fragments of its abstract through a repost on a mailing list and did not read the paper ([es-discuss repost](https://esdiscuss.org/topic/fyi-yield-mainstream-delimited-continuations-in-tpdc2011)).

### A compiler turns a generator into the state machine the programmer would otherwise write

The C# compiler, Rust's coroutine design, and C++20's stackless coroutines each turn a generator into a state machine: an object whose state field is the old instruction pointer and whose other fields are the live locals.
Raymond Chen describes the C# case, where iterators "take a function with yield return statements (and possible some yield break statements) and convert it into a state machine", inside a generated class that has "a member for each local variable" ([Chen 2008](https://devblogs.microsoft.com/oldnewthing/20080812-00/?p=21273)).

The sources agree about the version a programmer writes when the compiler offers no such transformation.
Simon Tatham states the problem as a question: "if you have a piece of code producing data, and another piece of code consuming it, which should be the caller and which should be the callee?"
His verdict on the two rewritten forms is that "Both of the processes taking place here are easier to read when written as a caller, not as a callee" ([Tatham 2000](https://www.chiark.greenend.org.uk/~sgtatham/coroutines.html)).
His later essay says where the state lives in the direct form ([Tatham 2023](https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/coroutines-philosophy/)):

> So there’s still a piece of data in the program tracking which of those ‘states’ we’re in – but it’s the program counter, and doesn’t need to be a named variable with a set of explicit named or numbered state values.

The Protothreads paper measured the difference in embedded C.
Event-driven code "enforces a state machine programming style", and a suspension mechanism of two bytes per thread removed most of the state machines in the programs examined and a third of their lines ([Dunkels et al. 2006](https://dunkels.com/adam/dunkels06protothreads.pdf)).

CPython takes another route to the same model.
It keeps the frame object on the heap and resumes it, so the frame's instruction offset plays the part of the state field.
That description is the theory researcher's inference from CPython's design, and it matches Peters's 1999 account of declining to release the frame.

### Internal and external iterators: Design Patterns states the dilemma, and a generator removes it

Design Patterns (Gamma, Helm, Johnson, Vlissides, 1994) states the two-sided problem as a choice inside the *Iterator* pattern.
The three passages below were read on 2026-11-05 in the author's local copy, `C:\git\DesignPatternsCD\markdown\patterns\iterator.md`, Implementation section, items 1 and 7, lines 110 to 117 and 171 to 174.
They close the gap that the theory notes mark as unread.

> When the client controls the iteration, the iterator is called an **external iterator**, and when the iterator controls it, the iterator is an **internal iterator**. Clients that use an external iterator must advance the traversal and request the next element explicitly from the iterator. In contrast, the client hands an internal iterator an operation to perform, and the iterator applies that operation to every element in the aggregate.

> External iterators are more flexible than internal iterators. It's easy to compare two collections for equality with an external iterator, for example, but it's practically impossible with internal iterators. Internal iterators are especially weak in a language like C++ that does not provide anonymous functions, closures, or continuations like Smalltalk and CLOS. But on the other hand, internal iterators are easier to use, because they define the iteration logic for you.

> External iterators can be difficult to implement over recursive aggregate structures like those in the Composite (163) pattern, because a position in the structure may span many levels of nested aggregates. Therefore an external iterator has to store a path through the Composite to keep track of the current object. Sometimes it's easier just to use an internal iterator. It can record the current position simply by calling itself recursively, thereby storing the path implicitly in the call stack.

These passages are the first two rows of the table in pattern vocabulary.
An internal iterator keeps the producer's position on the call stack, "storing the path implicitly in the call stack", and the consumer becomes an operation that the client hands in.
An external iterator keeps the consumer's loop, and the producer "has to store a path".
The book's test of the internal iterator, comparing two collections for equality, is Liskov's test of CLU and the samefringe problem in its simplest form.

That file holds two more links to this history.
Line 108 says of the pattern that "Some languages (CLU [LG86], for example) even support this pattern directly."
The sample code for an internal iterator in C++ meets the consumer's half of the problem at line 429: "Often you want to accumulate state during the iteration, and functions aren't well-suited to that; we would have to use static variables to remember the state."
That sentence describes the `tokeneater` of PEP 255, which keeps "a state machine in global variables".

A generator removes the choice.
You write the producer as an internal iterator, with its loops and its recursion in place, and the consumer uses it as an external iterator, through `next()`, an early `break`, or `zip()` over two generators.
A recursive generator stores the path through a *Composite* in a chain of suspended frames, one for each level, which `yield from` links.
Bob Nystrom gives the reason both sides cannot have the stack: "It’s a question of who gets to control the callstack", and "Whoever gets put on top of the stack is in the weaker position, because it must return all the way to the other one between each generated value" ([Nystrom 2013, part 1](https://journal.stuffwithstuff.com/2013/01/13/iteration-inside-and-out/)).
His account of the generator's limit agrees with PEP 380: "Iterators/generators reify a stack frame for you, but they only reify one" ([Nystrom 2013, part 2](https://journal.stuffwithstuff.com/2013/02/24/iteration-inside-and-out-part-2/)).
Oleg Kiselyov states the direction of the conversion.
Every pull generator converts to a push generator, and "The other way around is tricky: one generally needs some sort of suspension (coroutine, delimited control, which requires a run-time support)" ([Kiselyov](https://okmij.org/ftp/continuations/generators.html)).

### Lazy evaluation makes the same argument for modularity

Hughes's "Why Functional Programming Matters" describes lazy evaluation in operational terms that fit a pipeline of generators ([Hughes](https://www.cse.chalmers.se/~rjmh/Papers/whyfp.pdf)):

> The two programs f and g are run together in strict synchronisation. F is only started once g tries to read some input, and only runs for long enough to deliver the output g is trying to read. Then f is suspended and g is run until it tries to read another input.

The conventional alternative in his paragraph is the tape again: "storing the output from f in a temporary file".
His claim for the mechanism is modularity.
It "allows termination conditions to be separated from loop bodies", and it lets you write "a generator which constructs a large number of possible answers, and a selector which chooses the appropriate one".
SICP states the efficiency side: "With streams we can achieve the best of both worlds: We can formulate programs elegantly as sequence manipulations, while attaining the efficiency of incremental computation" ([SICP, section 3.5](https://sarabander.github.io/sicp/html/3_002e5.xhtml)).
SICP's history footnote credits Landin (1965) with the first description of streams built on delayed evaluation, and the researchers read the footnote, not Landin's paper.
"Generators are lazy evaluation for a strict language" is a fair inference from Hughes for sequences, and no source in the notes says it in those words.

### `yield` is an effect operation, and the driver is its handler

The effects literature gives chapter 45's driver its formal name.
Plotkin and Pretnar describe operations and handlers as duals: operations are "effect constructors as they give rise to the effects", and handlers are "effect deconstructors" ([Plotkin and Pretnar 2013](https://arxiv.org/abs/1312.1399)).
Leijen defines `yield` as an effect with one operation and writes the consumer as its handler.
He presents effect handlers as the generalization of "exception handling, state, iterators and async-await" ([Leijen 2016](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/algeff-tr-2016-v2.pdf)).

The mapping onto the chapter is direct.
The generator is the handled computation, a yielded request is an operation, the driver is the handler, and `send()` is the handler's `resume`.
`throw()` is a handler that raises an exception inside the computation, and `close()` is a handler that declines to resume.
This mapping is the theory researcher's inference, since no academic source in the notes implements handlers on Python generators.

Two limits of an Effect system built on generators follow from the classification.
A generator resumes once, so a handler that resumes one computation twice, for a backtracking search, has no generator form.
Dolan and colleagues name backtracking as the case that their linear continuations exclude ([Dolan et al. 2017](https://kcsrk.info/papers/system_effects_feb_18.pdf)).
A generator is stackless, so a request made three calls deep reaches the driver when each function on the way is a generator that delegates with `yield from`.
Dan Abramov says the same of JavaScript: "if you’re working with generators, things in the middle also have to be aware of generators" ([Abramov 2019](https://overreacted.io/algebraic-effects-for-the-rest-of-us/)).
Nystrom's "function color" is that requirement seen from the caller's side, and he names what removes it: "multiple independent callstacks that can be switched between" ([Nystrom 2015](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)).

Designers who choose the stackless form give three reasons, and all three follow from one fact: the saved state is a frame the compiler can see.
A stackless coroutine stores "locals that are live across suspend point" and uses the stack of the thread that runs it ([Nishanov 2018](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1364r0.pdf)).
It stays on that thread's stack at the boundary with C, where for a stackful design "Switching code from executing on a green thread to running on the OS thread stack can be prohibitively expensive for FFI" ([withoutboats 2023](https://without.boats/blog/why-async-rust/)).
It compiles to an ordinary state machine, which the language's existing runtime executes ([Rust RFC 2033](https://github.com/rust-lang/rfcs/blob/master/text/2033-experimental-coroutines.md)).
The second reason is the one Van Rossum gave in 2004 for keeping Python's state on the C stack: Python "wants to be friendly to extensions written in C or C++, including those that frequently call back into Python" ([python-dev, 1 June 2004](https://mail.python.org/pipermail/python-dev/2004-June/045089.html)).

### Which formulations the sources support

The best-supported statement of the idea has three parts: a problem, a principle, and a mechanism.
The problem is that two pieces of code each have a loop and must exchange items one at a time, and one call stack lets one of them be the caller.
Conway, PEP 255, Tatham, Nystrom, and Design Patterns all state it.
The principle is that a function's position in its control flow is state, and a generator keeps that state in the program counter and the frame's locals, in place of variables the programmer maintains.
Conway's switch, Sather's "encode the control structure as state", Peters's "persistent flags and state vrbls", Tatham, Chen, the Protothreads paper, the Rust RFC, and Kotlin's design document all say so.
The mechanism is that the generator's frame outlives the call that suspended it, which Peters, Kuchling, Nystrom, and Nishanov each describe.

Three common formulations need a qualifier.
"A generator is a coroutine" is true of an asymmetric, first-class, stackless coroutine.
"A generator is a one-shot continuation" is true of a one-shot delimited continuation that captures one frame.
"Symmetric coroutines are more powerful than asymmetric ones" is the belief that de Moura and Ierusalimschy call a misconception.

## Six corrections to the common account, and what stays unverified

The researchers corrected six points that secondary accounts repeat.
They also marked a longer set of statements as unconfirmed, and the second table lists the ones a chapter on generators is most likely to use.
Check each of those against its original before it goes into the book.

| Common account | What the sources show | Sources |
|---|---|---|
| Conway coined "coroutine" in 1958 for an assembly program, and his 1963 paper is the record of it | The 1963 paper dates the compiler work to 1961 at Case Institute of Technology, and its footnote says Conway and Joel Erdwinn developed the idea concurrently. Wikipedia attributes the 1958 date and the assembly program to Knuth, The Art of Computer Programming, volume 1, section 1.4.5. Knuth's wording was not read. | [Conway 1963](https://www.melconway.com/Home/pdf/compiler.pdf); [Wikipedia, "Coroutine"](https://en.wikipedia.org/wiki/Coroutine) |
| Conway described coroutines as "subroutines who act as the master program" | That wording is de Moura and Ierusalimschy's report of Conway. The printed sentence is "coroutines are subroutines all at the same level, each acting as if it were the master program when in fact there is no master program". | [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf); [Conway 1963](https://www.melconway.com/Home/pdf/compiler.pdf) |
| Knuth named the semi-coroutine | Tim Peters said so in 1999. De Moura and Ierusalimschy cite Dahl and Hoare's "Hierarchical Program Structures" (1972) for "semi coroutines", a search summary of Samet 1985 agrees, and Jackson cites Simula ("[Dahl 70]") for the concept. The 1972 chapter and Knuth's text were not read. | [de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf); [Samet 1985](https://www.cs.umd.edu/users/hjs/pubs/SametIPL85.pdf); [python-dev, 5 July 1999](https://mail.python.org/pipermail/python-dev/1999-July/000467.html) |
| PEP 255 credits Griswold and takes Icon, CLU, and Sather as its models | The PEP cites the Sather paper and the Icon home page, mentions CLU as the inspiration for Sather's iterators, and calls the three constructs "pleasant solutions" that share "the basic idea". Griswold's name is absent from it. | [PEP 255 source](https://github.com/python/peps/blob/main/peps/pep-0255.rst) |
| Generators arrived in Python 2.3 | Kuchling's "What's New in Python 2.5" and Beazley's 2014 slides say 2.3. PEP 255 says "Python-Version: 2.2", where a module enabled generators with `from __future__ import generators`, and "What's New in Python 2.2" says the statement becomes unnecessary in 2.3. | [PEP 255](https://peps.python.org/pep-0255/); [What's New in Python 2.2](https://docs.python.org/3/whatsnew/2.2.html); [What's New in Python 2.5](https://docs.python.org/3/whatsnew/2.5.html) |
| The rewritten routine was called a state machine from the start | Conway writes "switch" and "router", and Jackson's commentators write "flags". Among the notes' sources, "state machine" appears first in the python-dev posts of 1999 and then in PEP 255. | [Conway 1963](https://www.melconway.com/Home/pdf/compiler.pdf); [python-dev, 13 May 1999](https://mail.python.org/pipermail/python-dev/1999-May/095192.html) |

| Statement | Status, and the route by which it reached the notes |
|---|---|
| Knuth, section 1.4.2: "Subroutines are special cases of more general program components, called coroutines. In contrast to the unsymmetric relationship between a main routine and a subroutine, there is complete symmetry between coroutines, which call on each other." | Secondary, from a 2015 post in a Google Group ([post](https://groups.google.com/g/flow-based-programming/c/hmeZYztfaQg)). The book was not read. Knuth's remarks on multipass algorithms, on Erdwinn and Merner, on a paper titled "Bilateral Linkage", and on an early UNIVAC programming tip are unverified. |
| Dahl and Hoare 1972: "a single coroutine may profitably be regarded as a complete self-contained program whose input and output instructions have been replaced by calls upon those coroutines to produce and consume the data" | Secondary, from Adrian Colyer's 2016 summary ([The Morning Paper](https://blog.acolyer.org/2016/10/18/hierarchical-program-structures/)). |
| Marlin 1980: "the values of data local to a coroutine persist between successive calls", and "the execution of a coroutine is suspended as control leaves it, only to carry on where it left off when control re-enters the coroutine at some later stage" | Secondary, quoted by de Moura and Ierusalimschy ([technical report](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)). |
| Alphard's generator has operations named `&init` and `&next` | From a reading-list summary of Shaw, Wulf, and London 1977 ([summary](https://research.cs.queensu.ca/home/cordy/cisc860/Biblio/drb/CS/shaw77.pdf)). The paper was not read. |
| Jackson's 2001 wording on inversion | Read in an unofficial copy ([studfile.net](https://studfile.net/preview/429617/)). The mechanics of inversion in his 1975 book are unverified. |
| IPL had generators before IPL-V | Unverified. The April 1960 article is the earliest text read. |
| Pipes entered Unix in 1973 | Ritchie's paper says 1972, and the conflict is unresolved. A 1968 McIlroy paper titled "Coroutines: semantics in search of a syntax" turned up in no search. |
| Landin 1965, Friedman and Wise 1976, Hewitt 1977, and the 1977 SIGART exchange on samefringe | Not read. Known through SICP's footnote, the Sather paper, and Gabriel's account, which the fetch returned in fragments. |
| Ruby's `yield` takes its name from CLU | A search summary of a ruby-talk post by Matsumoto. The post was not opened. |
| Van Rossum said in his own words that a visible `yield from` marks each switch point | Unverified. A search snippet of a python-tulip message carried such a sentence, and the fetched page did not. |
| James and Sabry 2011, "Yield: Mainstream Delimited Continuations" | Three fragments of the abstract, read through a repost. The paper was not read. |
| Bruggeman, Waddell, and Dybvig 1996 | Read in a copy on a personal site whose provenance is unverified. The text matches the ACM citation. |
| de Moura and Ierusalimschy, "Revisiting Coroutines" | The 2004 technical report was read. The 2009 TOPLAS article was not compared, so wording and section numbers there can differ. |
| The scanned sources: Newell and Tonge 1960, the Conniver manual, the CLU Reference Manual | Read as text extracted from scans. The researchers corrected OCR errors in the CLU and Conniver quotations and noted lost characters in the IPL-V article. |
| `GeneratorExit` inherits from `Exception` | PEP 342 says so. The later move under `BaseException` is unverified in the notes. |
| PEP 380 was accepted on 26 June 2011 | The PEP says the 26th. The message it links is dated 25 June 2011 in the archive. |
| Schemenauer answered Peters "1h35m later" on 16 March 2001 | The notes say so. The timestamps they quote, 02:02:08 -0500 and 03:37:33 -0800, are 4 hours 35 minutes apart. |
| `os.path.walk()` callbacks were a motive for generators | No python-dev message of 1999 to 2001 that the researchers read mentions it. |
| Python 2.2 was released in December 2001 | Not checked against a primary source. |

## Claims in chapter 45 checked on 2026-11-05

The researchers checked 13 sentences from the chapter's last section, "Half a Coroutine by Design", and the theory notes add precision points on two of its terms.
The first two columns give the chapter's wording as it stood on 2026-11-05 and its line number in `Chapters/45_Effects--Generators.md` on that date.
Five claims are confirmed as written, five hold with a precision note, two are partly confirmed, and one is wrong as worded.

Status after the check: commits `01456978` and `3c8d9a76` corrected the chapter the same day, so the wording and line numbers in these tables describe the text before those commits.
The commits rewrite the section's opening around the principle and Conway's switch (line 1811), and they reword five sentences:
the PEP's "pleasant solutions" replace "the models" (line 1975),
`suspend` loses "statement" (line 1977),
Stackless keeps Python's state off the C stack, per Tismer's 2000 paper and PEP 219, where the chapter had it saving and restoring that stack (lines 1985 to 1986),
Peters's "half" is the asymmetry, which PEP 342 kept (line 1997),
and `close()` has its own reason (line 1999).
The four Conway quotations in the new opening were compared with the page images of the 1963 paper, pages 396 and 397, and match.
The IPL-V passage was compared the same way with page 209 of the April 1960 article and matches; the mark lost in extraction is a dash after "must coexist in the computer", before "that of the generator and that of the superprocess and subprocess".
Three items stood as they were after those commits: the PEP 492 sentence (line 2008), the two "one-shot continuation" sentences, which match chapter 44's definition of a continuation, and the stackless half of "half a coroutine".

On 2026-11-06 the chapter closed the third item and gained Conway's example.
"Half a Coroutine by Design" now shows the asterisk squasher as two listings, `squasher_switch.py` (an iterator class whose `__next__()` tests a stored character on every call, the switch of Conway's Figure 1) and `squasher_generator.py` (the same logic with two `yield`s in a row, the two writes of his Figure 2).
Both listings were compared with the flowcharts on page 397 of the paper.
Their `case ""` is an addition: Conway's flowcharts read cards without end, and a Python iterator ends.
"The Restriction Behind the Driver" now has a paragraph on the second restriction: a `yield` suspends one frame, so a helper that makes a request must be a generator too, with the sentence from PEP 380's Motivation quoted from the PEP's source text.
The PEP 492 sentence and the "one-shot continuation" sentences stand as they were.

An independent read of the new passages that day confirmed the six quotations and both listings, and it corrected two older sentences that the 13 claims below do not cover.
"A delegating generator passes all three channels through to the innermost generator" was wrong: `yield from` relays the yield and send channels to the driver, and the helper's return value stops at the delegating generator, as the value of the `yield from` expression.
"The third way, older than PEP 255's generators" was imprecise: PEP 255 requires PEP 234 and names the iterator as "another alternative", so the chapter no longer dates the iterator class before generators.

Three follow-ups went in later that day.
The chapter opens with the reason a generator exists, and "Half a Coroutine by Design" begins by recalling that opening (`f4669e3e`).
The second restriction is tied to `async` through PEP 492's statement that `await` "uses the `yield from` implementation" (`d6c22177`).
Exercise 10 asks for PEP 255's tree walk as an iterator class, and its solution prints the class's stack beside the generator's `gi_yieldfrom` chain (`861f8516`).
A second independent read found nothing wrong and five statements imprecise, corrected in `861f8516` and `c58392df`.
A generator keeps its state across each `next()` or `send()`, where the new opening had said "between calls".
An `await` suspends the `async` function that contains it, and each awaiting caller suspends at an `await` of its own, where the text had said "one frame" and "every caller".

### PEP 255 and the 1999 debate (verdicts from `python_pep_255_decision.md`)

| Line | Chapter's wording | Verdict | Evidence |
|---|---|---|---|
| 1811 | "PEP 255 added generators to Python 2.2 in 2001 so that a function can produce values one at a time." | **Confirmed** | The PEP's header reads "Created: 18-May-2001" and "Python-Version: 2.2" ([PEP 255](https://peps.python.org/pep-0255/)). "What's New in Python 2.2" has the section "PEP 255: Simple Generators" ([What's New in Python 2.2](https://docs.python.org/3/whatsnew/2.2.html)). The release date of Python 2.2 was not checked against a primary source. |
| 1816 | "The PEP's example, the standard library's `tokenize()`, keeps its place in the source text." | **Confirmed, with a precision note** | `tokenize()` and its *tokeneater* callback are the PEP's motivating example in prose: "the caller must pass a *tokeneater* function to ``tokenize()``". The PEP's code listings are `fib()` and a binary-tree `inorder()` ([PEP 255](https://peps.python.org/pep-0255/)). |
| 1965 | "The PEP's authors wanted the useful part of a coroutine without the whole mechanism." | **Supported as a paraphrase** | The PEP: "generators provide a useful subset of Stackless functionality in a way that fits easily into the current CPython implementation" ([PEP 255](https://peps.python.org/pep-0255/)). Peters, 8 July 1999: "they don't need to turn Python inside out to get just that much" ([python-dev](https://mail.python.org/pipermail/python-dev/1999-July/000485.html)). Peters, 31 January 2001: "once you go beyond "simple" (Icon) generators, a whole world of other stuff gets pulled in" ([python-dev](https://mail.python.org/pipermail/python-dev/2001-January/012402.html)). The PEP's phrase "useful subset of Stackless functionality" is close enough to quote in place of the paraphrase. |
| 1975 | "The PEP names Ralph Griswold's Icon language, with CLU and Sather, as the models." | **Wrong as worded** | The PEP's sentence is "Some other high-level languages provide pleasant solutions, notably iterators in Sather, which were inspired by iterators in CLU; and generators in Icon, a novel language where every expression *is a generator*." Griswold's name is absent from the PEP, whose Icon reference is the address of the Icon home page. CLU appears as the inspiration for Sather. The PEP's words are "pleasant solutions" and "the basic idea", and "models" is the chapter's ([PEP 255 source](https://github.com/python/peps/blob/main/peps/pep-0255.rst)). |
| 1987 | "Stackless Python's coroutines do that, and the PEP calls Stackless "a controversial rethinking of the Python core."" | **Confirmed, exact wording** | "However, Stackless is a controversial rethinking of the Python core, and it may not be possible for Jython to implement the same semantics." ([PEP 255](https://peps.python.org/pep-0255/)) |
| 1995 | "In May 1999, two years before the PEP, Tim Peters called generators "half a coroutine" on python-dev." | **Confirmed** | Tim Peters, "[Python-Dev] Coroutines", archive timestamp Sat May 22 06:22:50 CEST 1999: "Generators are really "half a coroutine", so this doesn't show the full power (other examples in the post do)." ([python-dev](https://mail.python.org/pipermail/python-dev/1999-May/095276.html)). PEP 255 was created on 18 May 2001, so "two years" is right to within a week. |

### The languages PEP 255 cites (verdicts from `generator_languages_before_python.md`)

| Line | Chapter's wording | Verdict | Evidence |
|---|---|---|---|
| 1977 | "Icon's `suspend` statement produces a value and leaves the procedure ready to produce another." | **Supported, with precision notes** | "The expression `suspend e` is similar to `return e`, except that the procedure activation is left in suspension so that it may be resumed for additional computation." ([Griswold, Hanson, Korb 1981](https://drh.github.io/documents/generators-in-icon.pdf)). Both Icon sources call `suspend` an expression, since Icon is an expression-oriented language. One `suspend` produces several values when its operand is a generator: "Like every, suspend e produces all alternatives of e as required." |
| 1978 | "CLU and Sather use the word `yield` for the same step inside an iterator, which hands one element at a time to a loop." | **Supported, with precision notes** | CLU: "Yield statements may occur only in the body of an iterator ... It has the effect of suspending operation of the iterator, and returning control to the invoking for statement." ([CLU Reference Manual 1979](https://ftp.mirrorservice.org/sites/www.bitsavers.org/pdf/mit/lcs/tr/MIT-LCS-TR-0225.pdf)). Sather: "If it yields, any return value is returned to the loop ... The execution state of the iterator is maintained, however." ([Murer et al. 1995](https://steveomohundro.com/wp-content/uploads/2009/03/murer_omohundro95_iteration_abstraction_in_sather.pdf)). A CLU `yield` hands over an "item" that "consists of zero or more objects", and Sather's `while!` "yields without returning a value", so "one element" describes the collection case that both papers lead with. |

### PEP 342, PEP 380, and PEP 492 (verdicts from `python_generators_to_coroutines.md`)

| Line | Chapter's wording | Verdict | Evidence |
|---|---|---|---|
| 1997 | "The other half came with PEP 342, written in 2005, which added the send channel to Python 2.5 in 2006." | **Confirmed** for the dates and the channel | PEP 342's header reads "Created: 10-May-2005" and "Python-Version: 2.5" ([PEP 342](https://peps.python.org/pep-0342/)). "Python 2.5 was released on September 19, 2006." ([What's New in Python 2.5](https://docs.python.org/3/whatsnew/2.5.html)). The researchers checked the clause from "PEP 342" on. The phrase "the other half" is taken up under the precision points. |
| 1999 | "Simulations, games, and asynchronous I/O need to pass a value or an exception into a generator at its suspension point, so `send()`, `throw()`, and `close()` arrived together." | **Partly confirmed** | The uses are the PEP's: "simulations, games, asynchronous I/O, and other forms of event-driven programming or co-operative multitasking", and the three methods did arrive together in Python 2.5 ([PEP 342](https://peps.python.org/pep-0342/#motivation)). The cause is too narrow for `close()`. The Motivation gives cleanup as a separate reason: generators "do not allow execution to be paused within the `try` portion of `try/finally` blocks, and therefore make it difficult for an aborted coroutine to clean up after itself". PEP 343 derives `throw()` and then `close()` from the `with` statement ([PEP 343](https://peps.python.org/pep-0343/#motivation-and-summary)). The PEP says coroutines express these programs naturally, which is weaker than "need". |
| 2001 | "The PEP describes a scheduler that runs many generators as a "trampoline," the shape of `task_runner_send.py`." | **Confirmed, with a nuance** | The PEP uses the word twice: "a simple co-routine scheduler or *trampoline function* would let coroutines *call* each other without blocking", and "A simple co-routine scheduler or *trampoline* that lets coroutines *call* other coroutines by yielding the coroutine they wish to invoke" ([PEP 342](https://peps.python.org/pep-0342/#examples)). The defining feature in the PEP is coroutines that call one another. Its fourth example runs many on one trampoline, with `trampoline.add( handler(connected_socket) )`. The comparison with `task_runner_send.py` was outside the check. |
| 2003 | "`yield from` (PEP 380, Python 3.3, 2012) completes the set." | **Confirmed** | "Python-Version: 3.3" ([PEP 380](https://peps.python.org/pep-0380/)). "Python 3.3 was released on September 29, 2012." ([What's New in Python 3.3](https://docs.python.org/3/whatsnew/3.3.html)). The PEP was created in 2009 and accepted in June 2011. |
| 2008 | "`async`/`await` (PEP 492, Python 3.5, 2015) is the same machinery with a syntax that marks a function as one the event loop resumes." | **Partly confirmed** | Version and year: "Python-Version: 3.5", and "Python 3.5 was released on September 13, 2015." ([What's New in Python 3.5](https://docs.python.org/3/whatsnew/3.5.html)). Same machinery: "Coroutines are based on generators internally, thus they share the implementation." ([PEP 492](https://peps.python.org/pep-0492/#coroutine-object-methods)). Two qualifications apply. The PEP "clearly separates them from generators", and native coroutine objects "do not implement `__iter__` and `__next__` methods", so the syntax marks a distinct type as well as a role. The PEP "is not tied to any specific Event Loop implementation", so "a scheduler" or "a driver" is more exact than "the event loop" ([PEP 492](https://peps.python.org/pep-0492/#abstract)). |

### Precision points on two terms (from `generator_theory.md`)

| Line | Chapter's wording | Assessment | Evidence |
|---|---|---|---|
| 194, 1988 | "A generator is therefore a *one-shot continuation*." and "The suspended generator is the one-shot continuation that [What a Suspended Generator Holds] describes." | **Accurate in a restricted sense** | A suspended generator is a one-shot delimited continuation whose boundary is the generator's frame. It holds one frame and no part of the caller's stack. Loom: "stackless continuations may only suspend in the same subroutine as the entry point" ([Project Loom proposal](https://cr.openjdk.org/~rpressler/loom/Loom-Proposal.html)). The equivalence between coroutines and one-shot continuations is proved for full, stackful coroutines, and for a Python generator "only the main body of a generator can suspend" ([de Moura and Ierusalimschy 2004](https://www.inf.puc-rio.br/~roberto/docs/MCC15-04.pdf)). James and Sabry call mainstream `yield` operators "one-shot or linearly used restrictions" of delimited continuations (a fragment, read through a repost). The point reaches line 184 as well, where "the rest of the computation from the `yield` forward" is the rest of the generator's body. |
| 1809, 1983 | The title "Half a Coroutine by Design" and "PEP 255 kept the suspended frame and dropped a coroutine's ability to hand control to any other coroutine." | **Fits the literature's vocabulary, with one restriction unnamed** | "Half a coroutine" covers two restrictions. A generator is asymmetric, since control returns to the resumer, and de Moura and Ierusalimschy show that asymmetry loses no expressive power. A generator is also stackless, since it suspends in its own frame, and that restriction does lose power. The chapter states the first. Peters stated both in 1999: "each coroutine needs its own stack (a generator only has one stack *frame*-- its own --to worry about)" ([python-dev](https://mail.python.org/pipermail/python-dev/1999-May/095277.html)). |
| 1997 | "The other half came with PEP 342" | **This report's reading, outside the researchers' checks** | Peters's "half" is the asymmetry: "co.detach is a special way to deal with this asymmetry" ([python-dev](https://mail.python.org/pipermail/python-dev/1999-May/095276.html)), and in June 2001, "They're formally semi-coroutines; it's not symmetric" ([python-dev](https://mail.python.org/pipermail/python-dev/2001-June/015607.html)). PEP 342 supplied a different missing part, the inbound channel of its own Motivation ("almost coroutines -- but not quite"). The asymmetry and the one-frame rule stayed: PEP 380 says in 2009 that a generator "can only yield to its immediate caller" ([PEP 380](https://peps.python.org/pep-0380/#motivation)). |

Three sentences need new wording, and the sources support these versions.
For line 1975: PEP 255 points to iterators in Sather, which CLU's iterators inspired, and to generators in Icon, as earlier solutions with the same basic idea.
For line 1999: PEP 342 gives two reasons.
A coroutine, the natural form for a simulation, a game, or asynchronous I/O, receives a value or an exception at the point where it paused, through `send()` and `throw()`.
A coroutine abandoned partway cleans up, through `close()` and a `yield` that became legal inside `try`/`finally`.
For line 2008: `async`/`await` runs on the generator machinery of `send()`, `throw()`, and `close()`, while `async def` creates a separate coroutine type that a `for` loop rejects, and `await` marks each point where a scheduler can suspend the coroutine.

## Conclusion: what the findings suggest for chapter 45

The chapter's two central sentences are the best-supported statements in it.
"A generator lets the producer and the consumer each keep their own loop" (line 1952) is PEP 255's argument that a generator "allows both sides to be coded in the most natural ways".
The chapter's list of what each workaround turns "inside out" is Tatham's diagnosis of the callback and the class.
The principle with the widest support sits one level below those sentences: a function's position in its control flow is state, and a generator keeps that state in the frame.
The section "What a Suspended Generator Holds" states the principle ("The position and the locals together are the generator's state"), and the history section can add that this state is the reason generators exist, with Conway's switch as the earliest example and Peters's "persistent flags and state vrbls" as Python's.
The order the sources support is problem, principle, mechanism: two loops on one stack, position as state, and a frame that outlives the call.

The history also supports the chapter's framing of a generator as a conversation.
A routine that suspends until its input arrives is as old as the coroutine.
Conway's routine B stops at a read command in 1963, and Conniver's consumer sends a message into a suspended generator in 1972.
PEP 255 kept the routine that suspends after an output, the form that fits one stack and one direction, and PEP 342 added the other direction.
"Producing values is half of what a generator does" (line 11) is accurate as history.

The one-frame rule connects the 2001 decision to the Effect chapters.
It is the reason a driver exists, which the chapter states at lines 1990 to 1993.
It is the reason `yield from` exists, and the reason every function between a request and its driver is a generator.
Stating the stackless limit beside the asymmetry lets "half a coroutine" carry both restrictions, in the terms of de Moura and Ierusalimschy and of Peters's 1999 message.
The phrase "one-shot continuation" matches the theory when it carries one qualifier: the continuation is the rest of the generator's own frame.

Nine statements of the problem are the clearest candidates for quotation, listed by date.

| Source | Exact wording | What it states |
|---|---|---|
| Newell and Tonge, "An Introduction to Information Processing Language V", Communications of the ACM, April 1960 ([PDF](https://iiif.library.cmu.edu/file/Newell_box00004_fld00298_doc0001/Newell_box00004_fld00298_doc0001.pdf)) | "Hence the strict hierarchy of routines and subroutines is violated, and special pains have to be taken to see that information remains safe and that each process works in its appropriate context." | The earliest statement that a generator and its consumer both need a live context |
| Conway, "Design of a Separable Transition-Diagram Compiler", Communications of the ACM, July 1963 ([PDF](https://www.melconway.com/Home/pdf/compiler.pdf)) | "Notice that the simple requirement of compressing asterisks requires the introduction of a switch which bifurcates the subroutine and selects the part to be used at each call depending on the situation at the last call. The reason for the switch is that each call of the subroutine must result in output of exactly one character." | Position stored as data, because the routine returns after each output |
| Conway 1963, the same paper | "Thus, coroutines are subroutines all at the same level, each acting as if it were the master program when in fact there is no master program." | Each side written as the main program |
| McDermott and Sussman, The Conniver Reference Manual, MIT AI Memo 259, 1972 ([text](<https://www.saildart.org/CNVR.RPO[UP,DOC]>)) | "What is needed is a way of returning some of the possibilities while maintaining the generator in existence for further duty if required." | The generator that stays alive between values |
| Liskov, "A History of CLU", MIT/LCS/TR-561, 1992, on the design of 1975 ([PDF](https://publications.csail.mit.edu/lcs/pubs/pdf/MIT-LCS-TR-561.pdf)) | "However, their use is limited so that CLU programs can make do with a single stack." | The restriction and its reason in one sentence |
| Gamma, Helm, Johnson, Vlissides, Design Patterns, 1994, Iterator, Implementation, item 7 (local copy, `C:\git\DesignPatternsCD\markdown\patterns\iterator.md`, lines 171 to 174) | "Therefore an external iterator has to store a path through the Composite to keep track of the current object. Sometimes it's easier just to use an internal iterator. It can record the current position simply by calling itself recursively, thereby storing the path implicitly in the call stack." | The dilemma in pattern vocabulary: which side keeps its position on the call stack |
| Murer, Omohundro, Stoutamire, Szyperski, "Iteration Abstraction in Sather", NECI TR 95-153, 1995 ([PDF](https://steveomohundro.com/wp-content/uploads/2009/03/murer_omohundro95_iteration_abstraction_in_sather.pdf)) | "Another goal for the iterator design was to allow iterators to be programmed in an active style, without having to explicitly encode the control structure as state, as is required for cursors and most other iteration constructs." | The purpose of the construct in one sentence |
| Tim Peters, python-dev, 5 July 1999 ([message](https://mail.python.org/pipermail/python-dev/1999-July/000467.html)) | "Because a generator remembers where it is and what its locals are, its state and "what to do next" don't have to be encoded in global data structures then decoded from scratch upon entry." | Python's statement of the motive, two years before the PEP |
| PEP 255, "Simple Generators", 2001 ([PEP](https://peps.python.org/pep-0255/)) | "As in the thread approach, this allows both sides to be coded in the most natural ways; but unlike the thread approach, this can be done efficiently and on all platforms." | Both sides keep their natural form, and the reason Python chose the restricted construct |

The strongest pair for a book on design patterns is Conway's switch and the Design Patterns passage on *Composite*.
Conway's sentence is the earliest statement of the fault in a subroutine, and the Design Patterns passage states the same fault in your reader's vocabulary.
Four of the nine come from three scanned sources (Newell and Tonge, Conway, and the Conniver manual), so compare them with a printed page before they go into the book.
Knuth's sentence about subroutines as special cases of coroutines stays out until someone reads it in The Art of Computer Programming.

