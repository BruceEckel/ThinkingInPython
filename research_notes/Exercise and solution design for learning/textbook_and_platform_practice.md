# Exercise and solution practice in programming textbooks, courses, and platforms

Scope: a catalogue of the structural devices recognized programming books and learning platforms use for exercises and solutions,
with the rationale their authors give and whatever evidence of effectiveness exists.
The reader's own design (end-of-chapter exercises, a separate solutions folder, each solution revealed in three collapsible steps: hint, code skeleton, full solution) is the baseline;
the devices below are the ones that go beyond it or that justify it.

Each finding marks whether the device works in a static book (print, EPUB, a static website), needs a runtime (a checker, tests, an IDE plugin), or needs a community (mentors, voting, other people's solutions).

## Key question 1: How do the named books structure exercises and solutions?

### Takeaway

The books split into three families:
interleaved exercises with no solutions in the book (SICP, HtDP, TAOCP's answers excepted),
end-of-chapter exercises with solutions sold or distributed separately (Thinking in Java, K&R via Tondo and Gimpel, Hutton's instructor-only materials),
and books with no exercises at all that teach by worked items instead (Effective Java, Effective Python, Learn You a Haskell).
Knuth and Bentley are the two print authors with an explicit, graded reveal device (difficulty ratings; hints before solution outlines),
and Atomic Kotlin is the Eckel book whose exercises moved into a runtime with hints and full solutions.

### Cited Findings

#### TAOCP (Knuth)

- Knuth's rationale for exercises, from "Notes on the Exercises":
  "It is difficult, if not impossible, for anyone to learn a subject purely by reading about it, without applying the information to specific problems and thereby being encouraged to think about what has been read. Furthermore, we all learn best the things that we have discovered for ourselves. Therefore the exercises form a major part of this work; a definite attempt has been made to keep them as informative as possible and to select problems that are enjoyable as well as instructive."
  The same notes observe that in many books easy exercises are mixed randomly among extremely difficult ones, which the rating scheme is meant to fix — [O'Reilly, "Notes on the Exercises", TAOCP 4B (via search summary)](https://oreilly.com/library/view/the-art-of/9780137926862/pref02.xhtml); an earlier wording ("forcing himself to think") is quoted as "D. Knuth, vol. 3" — [U. Oregon CIS 610 quotes page](https://classes.cs.uoregon.edu/10W/cis610tes/quotes5.html)
- The scale: "a numerical rating varying from 0 to 50, where 0 is trivial, and 50 is an open question in contemporary research" — [Wikipedia, The Art of Computer Programming](https://en.wikipedia.org/wiki/The_Art_of_Computer_Programming)
- Level descriptions quoted in search summaries of the notes: 20 is "an average problem for a mathematically inclined reader"; 50 is "a research problem which (to the author's knowledge at the time of writing) has not been solved satisfactorily" — [O'Reilly, TAOCP answers page (search summary)](https://www.oreilly.com/library/view/the-art-of/9780321635792/ans.xhtml)
- "M indicates Mathematically oriented" and "HM indicates Higher mathematical education required"; the famous [M50] exercise was Fermat's Last Theorem, posed about two decades before it was proved — [Tal Cohen's Bookshelf (search summary)](https://tal.forum2.org/story_45)
- Every exercise rated 46 and above is a research problem; when one is solved it receives a new rating of 45 or less, so the ratings are maintained across printings — [cs.stanford.edu errata (search summary)](https://cs.stanford.edu/%7Eknuth/err1.textxt)
- Knuth still asks readers to check the hard exercises for correctness, which treats the exercise set as a maintained artifact rather than a fixed appendix — [i-programmer, "Donald Knuth At 80 Still Improving TAOCP"](https://www.i-programmer.info/news/112-theory/11495-donald-knuth-at-80-still-improving-taocp.html)
- Works in: static print. The ratings are text; the answers are an appendix.

#### SICP (Abelson and Sussman)

- The first-edition preface contains no statement about exercises (checked against the full preface text) — [SICP preface, Sarabander HTML edition](https://sarabander.github.io/sicp/html/Preface-1e.xhtml)
- The MIT Press page lists an Instructor's Manual that "contains discussions of exercises and other material in the text as well as supplementary material, additional examples and exercises, and teaching suggestions"; no public official solutions exist — [MIT Press SICP page (search summary)](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/sicp.html)
- Solutions are community-maintained: the SchemeWiki "SICP-Solutions" page, many GitHub repositories (one per exercise in Markdown or source), and a SICP study Discord for getting unstuck — [schemewiki SICP-Solutions](http://community.schemewiki.org/?SICP-Solutions); [williamgherman/sicp](https://github.com/williamgherman/sicp); [sahglie/sicp-study](https://github.com/sahglie/sicp-study)
- Works in: static print for the exercises; the solutions layer is community-supplied and lives outside the book.

#### How to Design Programs (Felleisen, Findler, Flatt, Krishnamurthi)

- The design recipe is six explicit steps: "From Problem Analysis to Data Definitions", "Signature, Purpose Statement, Header", "Functional Examples", "Function Template", "Function Definition", "Testing", and "Examples play a central role at almost every step" — [HtDP 2e preface](https://htdp.org/2024-11-6/Book/part_preface.html)
- Readers should "solve all exercises or at least know how to solve them"; the book runs "themed sequences of exercises" across parts (virtual pets, text editors); "Independent readers ought to work through the entire book, from the first page to the last" — [HtDP 2e preface](https://htdp.org/2024-11-6/Book/part_preface.html)
- The first edition published a public "Exercise Solutions for How to Design Programs" table of contents by chapter and section, with no access restriction stated on the page — [htdp.org 2003 Solutions contents](https://htdp.org/2003-09-26//Solutions/contents.html)
- Works in: static print (the recipe is a checklist the reader applies by hand).

#### Think Python 3e (Downey)

- "you can't learn to program just by reading a book – you have to practice", so the book "includes exercises at the end of every chapter where you can practice what you have learned" — [Think Python 3e preface](https://allendowney.github.io/ThinkPython/chap00.html)
- Retrospective: "the exercises in the second edition were uneven" and "moving to Jupyter notebooks helped me develop and test a more engaging and effective sequence of exercises" — [Think Python 3e preface](https://allendowney.github.io/ThinkPython/chap00.html)
- Solutions policy: "You can find notebooks with solutions to the exercises at https://allendowney.github.io/ThinkPython"; free, complete, same format as the chapters — [Think Python 3e preface](https://allendowney.github.io/ThinkPython/chap00.html)
- Each chapter is a notebook because "you can run the code, modify it, and work on the exercises, all in one place"; beginners are told to use Colab — [Think Python 3e preface](https://allendowney.github.io/ThinkPython/chap00.html)
- Works in: runtime (notebook), with a static fallback (the rendered HTML).

#### Thinking in Java, Atomic Kotlin, Atomic Scala (Eckel)

- Thinking in Java introduction: "I've discovered that simple exercises are exceptionally useful to complete a student's understanding during a seminar, so you'll find a set at the end of each chapter"; most are meant to be done in classroom time, some are harder; "Solutions to selected exercises can be found in the electronic document The Thinking in Java Annotated Solution Guide, available for a small fee from www.BruceEckel.com" — [TIJ 3e introduction, SDSU mirror](https://edoras.sdsu.edu/doc/aaa-TIJ3-distribution/TIJ302.htm)
- The 4e Annotated Solutions Guide is a $25 PDF with a compilable code tree, Ant build files, Eclipse-ready; "If printed in the same format as Thinking in Java, this guide would be almost 900 pages"; a free sample covers two chapters so the buyer can confirm installation first — [Gumroad, TIJ 4e Annotated Solutions Guide](https://bruceeckel.gumroad.com/l/mvcKV); the 2nd/3rd edition guide is $20 — [Gumroad, TIJ 3rd/2nd Solutions](https://bruceeckel.gumroad.com/l/SJMCd)
- The introduction gives no explicit reason for selling solutions separately; the fetched text has none — [TIJ 3e introduction](https://edoras.sdsu.edu/doc/aaa-TIJ3-distribution/TIJ302.htm)
- Atomic Kotlin: "Most atoms ... are accompanied by a handful of small exercises", solved "immediately after reading the atom"; "Most of the exercises are checked automatically by the JetBrains IntelliJ IDEA integrated development environment (IDE), so you can see your progress and get hints if you get stuck"; the course contains solutions for all exercises, and the authors say to use hints or peek at a solution when stuck but still recommend "implementing it yourself"; exercises and solutions are also available "in plain text form along with Gradle build files" — [Atomic Kotlin introduction (Leanpub)](https://leanpub.com/read/AtomicKotlin/introduction); [AtomicKotlin.com/exercises](https://atomickotlin.com/exercises)
- Atomic Scala: a third-party GitHub repository holds per-chapter solutions, and Lightbend published the examples as an Activator template; no official solution policy was found — [absognety/atomic-scala](https://github.com/absognety/atomic-scala); [Lightbend Activator template post](https://www.lightbend.com/blog/activator-template-of-the-month-atomic-scala-examples)
- Works in: TIJ static with a paid separate document; Atomic Kotlin runtime (IDE plugin) with a static plain-text fallback.

#### K&R and Kernighan & Pike

- The C Programming Language poses "about a hundred exercises" with no solutions; Tondo and Gimpel's The C Answer Book supplies all of them, "each solution written using only the knowledge acquired at the time the exercise is posed, following the same progression as Kernighan" — [library catalog descriptions of The C Answer Book (search summary)](https://catalogue.i2m.univ-amu.fr/bib/1088); [Dunod, Clovis Tondo](https://dunod.com/livres-clovis-tondo)
- The Practice of Programming is organized by chapter (Style, Algorithms and Data Structures, Design, Interfaces, Debugging, Testing, Performance, Portability, Notation) with a "Collected Rules" appendix; the search found no description of its exercise policy — [Pearson, The Practice of Programming](https://pearson.com/us/higher-education/program/Kernighan-Practice-of-Programming-The/PGM323407.html)
- Works in: static print; the answer book is a separate commercial volume written by other authors.

#### The Little Schemer (Friedman and Felleisen)

- Format: a programmed text, read "with a card in your hand covering up part of the page, the book asks a question, then you come up with an answer, then you move the card and check your answer"; it "does little or no explanation", giving examples as question and answer first and letting the reader build the definition — [Marc Abramowitz review](https://marc-abramowitz.com/?p=867); [Adam Tornhill review](https://www.adamtornhill.com/reviews/littleschemer.htm)
- Preface statement of rationale (quoted by a reviewer): "We believe that you can form your own definitions and will thus remember them and understand them better than if we had written each one for you" — [Al Sweigart, Invent with Python review](https://inventwithpython.com/blog/book-review-the-little-schemer.html)
- The book grew from lecture notes for a two-week introduction to Scheme for students "with no previous programming experience and an admitted dislike for anything mathematical"; the goal is to teach recursive thinking — [Marc Abramowitz review](https://marc-abramowitz.com/?p=867)
- Dissent: Sweigart calls the self-discovery belief "an utterly, completely erroneous belief", says "This book literally never explains anything directly", and lists what the format lacks: "Better titles for its chapters. It needs a glossary and explanatory paragraphs. It needs objectives and summaries in each chapter" — [Invent with Python review](https://inventwithpython.com/blog/book-review-the-little-schemer.html)
- The Ten Commandments and Five Rules are the book's named summaries of the recursion patterns — [Invent with Python review](https://inventwithpython.com/blog/book-review-the-little-schemer.html)
- Works in: static print; the device is the page layout and the reader's card.

#### Programming in Haskell (Hutton) and Learn You a Haskell

- Hutton 2e has "Appendix A. Selected solutions" in the book; instructors can request "a large collection of introductory and advanced exams and answers based on the content" from solutions@cambridge.org — [Hutton's book page](https://people.cs.nott.ac.uk/pszgmh/pih.html)
- Learn You a Haskell "doesn't have any exercises, so it doesn't force you to check what you have learned"; a reviewer names the lack of exercises the book's biggest obstacle — [Ranjit Mathew review](https://rmathew.com/2015/lyah.html); a haskell-beginners thread makes the same complaint — [haskell-beginners, "A Week in and Clueless"](https://mail.haskell.org/pipermail/beginners/2013-January/011241.html)
- Works in: static print.

#### Effective Java, Effective Python, Fluent Python

- Effective Java: each chapter "consists of several 'items', each presented in the form of a short, stand-alone essay that provides specific advice, insight into Java platform subtleties, and outstanding code examples", illuminating "what to do, what not to do, and why"; no exercises are described — [Coles Books listing (publisher text)](https://coles-books.co.uk/effective-java-addison-wesley-by-joshua-bloch)
- Effective Python: chapters hold 7 to 13 items, "smaller sections usually less than 10 pages that focus around a specific and practical recommendation"; the site's substitute for exercises is the code repository: "Run and modify the example code yourself to confirm your understanding" — [DZone review](https://dzone.com/articles/book-review-effective-python-by-brett-slatkin); [effectivepython.com](https://effectivepython.com/)
- Fluent Python: no reliable source found that describes an exercise policy either way (see Gaps).
- Works in: static print; the "item" is a device for books that teach by advice rather than by practice.

#### Rust Book and Rustlings

- The Rust Book has "two kinds of chapters ... concept chapters and project chapters. In concept chapters, you'll learn about an aspect of Rust. In project chapters, we'll build small programs together, applying what you've learned so far. Chapter 2, Chapter 12, and Chapter 21 are project chapters"; "There is no wrong way to read this book" — [Rust Book introduction](https://doc.rust-lang.org/book/ch00-00-introduction.html)
- Rustlings is "Small exercises to get you used to reading and writing Rust code!" and "Recommended in parallel to reading the official Rust book" — [rust-lang/rustlings README](https://raw.githubusercontent.com/rust-lang/rustlings/main/README.md)
- Rustlings 5.x: "Most exercises contain an error that keeps them from compiling, and it's up to you to fix it!"; `rustlings watch` verifies "every exercise in a predetermined order" and reruns on file change; `rustlings hint <name>` prints a hint; exercises "are sorted by topic" — [rustlings 5.6.1 README](https://raw.githubusercontent.com/rust-lang/rustlings/5.6.1/README.md)
- Rustlings 6.0 changes: "every exercise now contains TODO comments to highlight what the user needs to change and where"; "The comment 'I AM NOT DONE!' doesn't exist anymore. Instead of needing to remove it to go to the next exercise, you need to enter n in the terminal"; "After finishing an exercise, a solution file will be available and Rustlings will show you its path in green" so you can "compare your solution with an idiomatic solution and maybe learn about other ways to solve a problem"; "While writing the solutions, all exercises have been polished"; a list mode shows every exercise's state — [rustlings CHANGELOG](https://raw.githubusercontent.com/rust-lang/rustlings/main/CHANGELOG.md); current usage page confirms "Search for TODO and todo!()", hints via `h`, list via `l` — [rustlings usage](https://rustlings.rust-lang.org/usage/)
- Works in: runtime (compiler and tests), with the solution revealed only after the exercise passes.

#### Exercises in Programming Style (Lopes)

- One task (term frequency) written in 33 styles in nine categories; "Each chapter first presents the constraints of the style, next shows an example program, and then gives a detailed explanation of the code", with sections on use in systems design and historical context; the motivation is that students "have been trained in one, at most two, programming languages, so they understand only the styles that are encouraged by those languages" — [ISR UCI book page](https://isr.uci.edu/content/exercises-programming-style); [Lavoisier listing](https://www.lavoisier.fr/livre/informatique/exercises-in-programming-style/descriptif_4113482)
- The "constraints" list is the device: a style is defined by what the solution may not do, and the same problem is re-solved under each constraint set.
- Works in: static print.

#### 99 Problems (Prolog, Lisp, Haskell)

- L-99 is "Based on a Prolog problem list by werner.hett@hti.bfh.ch" (Berne University of Applied Sciences); problems carry (\*), (\*\*), (\*\*\*) difficulty markers from easy to hard — [L-99 Ninety-Nine Lisp Problems](https://www.ic.unicamp.br/~meidanis/courses/problemas-lisp/L-99_Ninety-Nine_Lisp_Problems.html)
- H-99 is "Haskell translations of Ninety-Nine Lisp Problems, which are themselves translations of Ninety-Nine Prolog Problems"; "Known solutions are listed at 99 questions/Solutions", a separate wiki page from the problem statements — [Haskell wiki, H-99](https://wiki.haskell.org/H-99:_Ninety-Nine_Haskell_Problems)
- Works in: static text; the solutions layer is a community wiki.

#### Programming Pearls (Bentley)

- Each column ends with problems; "At the end of the book are hints (further questions providing insightful ways of approaching a solution) corresponding to each column's problem set, and outlines of solutions in a section following the hints section" — [Linux Journal review of Programming Pearls 2e](https://www.linuxjournal.com/node/3846)
- Bentley "encourages readers to discuss their ideas with friends and colleagues before peeking at the hints and solutions", and says "most of what you learn from this book will come out the end of your pencil" — [InformIT product page (search summary)](https://www.informit.com/store/programming-pearls-9780201657883)
- Works in: static print. This is the closest print precedent for a hint-then-solution ladder: the hint is itself a question, and the solution is an outline rather than a listing.

#### Learn Python the Hard Way (Shaw)

- "You must type each of these exercises in, manually. If you copy and paste, you might as well not even do them. The point of these exercises is to train your hands, your brain, and your mind in how to read, write, and see code"; the targeted skills are "reading and writing, attention to detail, and spotting differences" — [LPTHW introduction](https://learnpythonthehardway.org/python3/intro.html)
- Each exercise carries "Study Drills" (extensions) and "Common Student Questions" sections; the series description says exercises "are thoroughly tested to verify they work with real students" — [InformIT listing](https://www.informit.com/store/learn-python-the-hard-way-a-very-simple-introduction-9780133124354); [Kinokuniya listing, 5e](https://www.kinokuniya.co.jp/f/dsg-02-9780138270575)
- Works in: static print; "Common Student Questions" is a print device for pre-empting the wrong turns a solution reveal would otherwise answer.

### Inferences

- Among print authors who state a reason, the reasons converge on Knuth's two sentences: practice is required, and self-discovered knowledge sticks.
  The Little Schemer takes the second claim to its limit (no explanations at all), and the strongest published criticism of that book attacks that claim directly, so the claim needs a hint layer to be defensible.
- Selling solutions separately (Eckel, Tondo and Gimpel) is never justified in the fetched prefaces as pedagogy; the only stated fact is price and format.
  Downey's and Rustlings' free, complete, same-format solutions are the current norm among the books and tools still being revised.
- Downey's retrospective ("uneven") and Rustlings' ("all exercises have been polished" while writing solutions) point the same way: writing the solution is how the exercise gets tested, so a book with every solution written is a book whose exercises have been checked.
- Knuth's rating scale is the only device in the set that tells the reader how much effort an exercise deserves before they start; Hett's three stars and Codewars' kyu do the same job more coarsely.

### Gaps

- Knuth's full rating table (the wording for 00, 10, 30, 40), the arrow marker for recommended exercises, and his advice on when to consult the answers could not be fetched; the O'Reilly chapter is paywalled (HTTP 403) and no mirror reproduced the table.
- SICP's own statement about exercises, if any, was not found in the first-edition preface; the second-edition preface and the "Instructor's Manual" text were not fetched.
- Software Design for Flexibility: no source describing its exercise placement or solution policy was found.
- Fluent Python: no source confirmed or denied an exercise policy; the ACCU review does not mention exercises — [ACCU review of Fluent Python 2e](https://accu.org/bookreviews/2023/wiesenhuetter_2005).
- Exercises in Programming Style: whether each chapter ends with exercises, and what they ask, was not confirmed by any fetched source.
- The Little Typer: not researched; no source fetched.
- Kernighan and Pike's exercise policy: not found.
- Atomic Scala's official solution policy: not found.

## Key question 2: What do platforms and courses do structurally?

### Takeaway

Platforms add four things a book cannot: a checker that gates the solution reveal (Rustlings, Exercism, Khan Academy, Codewars), many solutions to one problem with curation (Exercism Dig Deeper, Codewars best-practices/clever voting), a human in the loop (Exercism mentoring), and a second part that changes the problem after the first part is solved (Advent of Code).
Of these, the "compare with other approaches after you solve it" layer is the one most platforms converged on independently.

### Cited Findings

#### Exercism

- Origin: Katrina Owen built it "as an internal tool to solve the problem of her own students not receiving feedback on the coding problems they were practicing" — [opensource.com, "Improve your programming skills with Exercism"](https://opensource.com/article/17/1/exercism-learning-programming)
- Concept Exercises: each has "a clear learning goal", is language-specific, and "Stubs/boilerplate are used to avoid the student having to learn/write unnecessary code"; "A seasoned developer in Language X should be able to work through all the Concept Exercises on that track spending no more than 5-10 minutes solving each one"; they "should feel relatively trivial" to experts because they target first-time use; exercises unlock on prerequisite concepts; "Concept Exercises are not mentored", which "shifts the burden of teaching to the exercise" — [Exercism docs, Concept Exercises](https://exercism.org/docs/building/product/concept-exercises)
- Dig Deeper: a tab "to help you go beyond the solving stage and explore the nuances and tradeoffs of an exercise, without needing to ask a mentor"; it holds Approaches (idiomatic and "sometimes non-idiomatic but interesting" ways to solve, each with an article), exercise articles on tradeoffs and performance, videos, and community solutions; the motivating number: of 500 recent TwoFer solutions, "over 350 of them were unique", and "reading them all would quite literally take a lifetime"; the team's standing to curate comes from "having designed the exercises, and mentored hundreds of thousands of people through them" — [Exercism blog, Dig Deeper](https://exercism.org/blog/dig-deeper)
- v3 Approaches "automatically group similar solutions to Practice Exercises, supported with community-sourced articles discussing each approach's pros, cons, and potential usages" — [exercism/v3 README (search summary)](https://github.com/m-dango/v3)
- Mentoring mindset: mentors should avoid "giving away the (better) solution" and describe alternatives instead, with a solution "optionally available" in a collapsible section if the student is stuck; students submit iterations and may decline suggestions; praise should "express the specific things you like about their solution"; "the learning journey, not the destination. The process and enjoyment of learning is more important than absolute factual correctness" — [Exercism docs, The Mentoring Mindset](https://exercism.org/docs/mentoring/mindset)
- v3 was built to fix v2's problem of students "being blocked while waiting for a mentor" — [exercism/v3 README (search summary)](https://github.com/neiesc/v3)
- Works in: runtime plus community. The Approaches articles are static prose and could be lifted into a book; the grouping and the mentor cannot.

#### Rustlings

- See Key question 1. The structural ideas: fix-the-error exercises, a predefined order, hints on demand, TODO markers, a solution revealed only after passing, and an exercise list with state.

#### Khan Academy

- "A challenge is a series of steps that the student must complete to create a program. The steps break down the program, providing guidance to the student on how to approach each part"; "We check whether the student has completed each step, providing hints when the student goes astray"; built on StructuredJS, "the library we wrote to verify student code and give hints"; the motivation was the "enormous gap between watching the talkthroughs ... and actually drawing or animating something on your own", since talkthroughs are "mostly passive learning (similar to watching a video)" while "challenges emphasize active, participatory learning" — [Khan Academy CS blog, "Introducing programming challenges" (2013)](https://cs-blog.khanacademy.org/2013/08/introducing-programming-challenges.html?m=0)
- Works in: runtime (structural code checking).

#### Codewars

- Ranks: "two classes of ranks—Kyu and Dan—which are divided into 8 levels each", borrowed from martial arts and Go — [Codewars docs, Ranks](https://docs.codewars.com/gamification/ranks/)
- A new kata "enters a 'beta' stage where people can solve it and ensure it meets quality standards", and solvers "vote on what they think the rank should be" — [Codewars, Kata Beta Process](https://www.codewars.com/topics/kata-beta-process)
- After solving, you are "immediately taken to this page", which "can give you an Aha! moment when you realize how others have completed the same task"; a matching algorithm removes "basic syntax structures, comments, and in some cases, alias method names" and groups duplicates, with "the first submitted one is used as a representative solution"; an "Unlock Solutions" button shows answers early but you "forfeit any honor and rank progression that you could earn on the kata" — [Codewars docs, Solutions](https://docs.codewars.com/concepts/kata/solutions/)
- Solution tag voting separates "Best Practices" ("solutions you would want to see in your own project that are readable, follow best practices, and create easily maintainable code") from "Clever" ("interesting and unique approaches ... that don't have to be practical", such as code golf) — [Codewars blog, Solutions Tag Voting (2014)](https://blog.codewars.com/2014/solutions-tag-voting/)
- Works in: runtime plus community. The best-practices/clever split is a labeling idea that transfers to a static book showing two solutions.

#### Advent of Code

- "Very generally, the puzzles get more difficult over time, but your specific skillset will make each puzzle significantly easier or harder for you than someone else"; "every problem has a solution that completes in at most 15 seconds on ten-year-old hardware" — [Advent of Code, About](https://adventofcode.com/about)
- Completing part one "reveals the second one, which uses the same data but often features some kind of twist or change to the first puzzle's requirements. This is intentional; it's meant to mirror real-life software development, where such changes are painfully all too common" — [MIT Technology Review, "The puzzle challenge..." (search summary)](https://www.technologyreview.com/2021/12/17/1042483/puzzle-challenge-coding-christmas/)
- Wastl "takes great care to make the challenges not require advanced knowledge of algorithms" — [Room Escape Artist podcast with Eric Wastl (search summary)](https://roomescapeartist.com/2023/11/28/repod-s6e9-advent-of-code-25-days-of-programming-puzzles-with-creator-eric-wastl/)
- No official solutions are published; the site's About page says nothing about solutions — [Advent of Code, About](https://adventofcode.com/about)
- Works in: runtime (an answer checker) and community (reddit solution threads). The "part two changes the requirements" device is static-compatible.

#### Project Euler

- "The problems range in difficulty and for many the experience is inductive chain learning. That is, by solving one problem it will expose you to a new concept that may allow you to undertake a previously inaccessible problem" — [Project Euler, About](https://projecteuler.net/about)
- The "one-minute rule": "although it may take several hours to design a successful algorithm with more difficult problems, an efficient implementation will allow a solution to be obtained on a modestly powered computer in less than one minute"; after solving, "you will be able to access a thread relating to that problem and it is here that you may be able to pick some tips from others that have solved it" — [Project Euler About (search summary via physicsforums)](https://www.physicsforums.com/threads/difficulty-of-project-euler-problems-1-100-now-versus-then.981194/post-6268418)
- Works in: runtime (answer check) plus community (post-solve thread).

#### Brilliant

- "Every lesson is built around guided problem-solving", learners "encounter a challenge first", and the platform "doesn't teach how to do something before asking questions"; it provides "feedback that explains why an answer was wrong instead of just marking it wrong" — [Brilliant, Why Brilliant](https://brilliant.org/help/why-brilliant); [Skillscouter review (search summary)](https://skillscouter.com/brilliant-review-math-science-coding/)
- The "Why Brilliant" page cites no research — [Brilliant, Why Brilliant](https://brilliant.org/help/why-brilliant)
- Works in: runtime; "explain why the wrong answer is wrong" transfers to a static book as a "common wrong answers" paragraph.

#### Runestone (Miller, Ranum, Ericson)

- "Programming is not a 'spectator sport'. It is something you do, something you participate in"; activecode lets readers "write and execute Python code" in the text; codelens "allows you to control the flow of execution"; "We have tried to use these different presentation techniques where they are most appropriate", hoping understanding "will be enhanced because you are able to experience it in more than just one way"; the preface cites no research — [How to Think Like a Computer Scientist: Interactive Edition, preface](https://cs.roanoke.edu/Fall2019/CPSC120/thinkcshpy/FrontBackMatter/prefaceinteractive.html)
- Parsons problems "reduce the difficulty of a coding problem by providing mixed-up blocks that the learner assembles in the correct order", and may "include distractor blocks that are not needed in a correct solution, but which may help students learn to recognize and fix errors" — [Ericson et al., ITiCSE 2023 working group report](https://strathprints.strath.ac.uk/86100/1/Ericson_etal_ITiCSE_2023_Conducting_multi_institutional_studies_of_Parsons_problems.pdf)
- Works in: runtime (Runestone executes code and checks Parsons order), though a Parsons problem can be printed.

#### Stanford CS106A and MIT 6.001

- CS106A publishes section handouts and their solutions on the course site, each section numbered and its solutions carrying an "S" suffix (e.g. "Section Solutions 1"), released through the term — [CS106A handouts index](https://web.stanford.edu/class/archive/cs/cs106a/cs106a.1192/handouts/index.html)
- MIT 6.001 (1998 offerings) distribute problem sets as PostScript, HTML, PDF, and DVI plus code tarballs — [6.001 Fall 1998 Problem Set 1](https://groups.csail.mit.edu/mac/classes/6.001/FT98/psets/ps1web)
- Works in: static documents.

### Inferences

- Four platforms (Exercism, Codewars, Rustlings, Project Euler) gate the reveal of other people's solutions behind a correct submission, and two (Codewars, Exercism's mentor advice) let the learner break the gate deliberately.
  A book cannot enforce the gate, but collapsible steps are the static analogue, and Codewars' "forfeit honor" framing suggests naming the cost of peeking in the prose.
- Exercism's Concept/Practice split (small, single-concept, unmentored, 5-10 minutes vs larger, mentored) and Khan Academy's talkthrough/challenge split are the same decision: one exercise per concept to confirm first use, then a larger problem to integrate.
- The post-solve comparison page (Codewars, Exercism, Rustlings' "idiomatic solution") is the device most often added by a platform after launch (Rustlings 6, Exercism v3), which suggests authors found that a single solution left learners without a sense of the design space.

### Gaps

- Codecademy: no source fetched describing its exercise structure.
- LeetCode's official editorial format (numbered approaches with complexity analysis) was not confirmed from an official page; only community repositories mirroring that format appeared.
- MIT OCW problem-set solution style: the fetched 6.001 pages show the problem sets, not solutions.
- Exercism's "representations" and automated analyzer feedback were only named in the docs index; the detail pages were not fetched.

## Key question 3: What alternative solution formats exist?

### Takeaway

Every format on the reader's list has a working precedent:
narrative solutions (Exercism Approach articles, Eckel's "annotated" guide),
several compared solutions (Codewars best-practices vs clever, Exercism approaches, Rustlings idiomatic comparison),
common wrong answers (LPTHW's Common Student Questions, Brilliant's explain-the-wrong-answer feedback, Parsons distractors),
tests as the specification (Ruby Koans, Rustlings, Exercism, Khan's StructuredJS),
extension ladders (Advent of Code part two, LPTHW Study Drills, HtDP themed sequences, Project Euler chains),
one-concept vs capstone (Exercism concept vs practice, Rust Book concept vs project chapters),
and critique-a-solution (Rustlings fix-the-error, Parsons with distractors, Ericson's "fixing code" condition, Exercism mentoring).

### Cited Findings

- Narrative of design decisions: Exercism Approaches come with "community-sourced articles discussing each approach's pros, cons, and potential usages" — [exercism/v3 README (search summary)](https://github.com/m-dango/v3); Eckel's guide is "Annotated" and would run almost 900 pages for one book — [Gumroad TIJ 4e guide](https://bruceeckel.gumroad.com/l/mvcKV); Bentley's solutions are "outlines of solutions" rather than listings — [Linux Journal review](https://www.linuxjournal.com/node/3846)
- Two or three solutions compared: Codewars' Best Practices vs Clever tags — [Codewars blog, Solutions Tag Voting](https://blog.codewars.com/2014/solutions-tag-voting/); Rustlings shows "an idiomatic solution" after you finish so you can "learn about other ways to solve a problem" — [rustlings CHANGELOG](https://raw.githubusercontent.com/rust-lang/rustlings/main/CHANGELOG.md); Lopes solves one task 33 ways under explicit constraints — [ISR UCI](https://isr.uci.edu/content/exercises-programming-style)
- Common wrong answers: LPTHW's per-exercise "Common Student Questions" — [InformIT listing](https://www.informit.com/store/learn-python-the-hard-way-a-very-simple-introduction-9780133124354); Brilliant's "feedback that explains why an answer was wrong instead of just marking it wrong" — [Brilliant, Why Brilliant](https://brilliant.org/help/why-brilliant); Parsons distractor blocks "may help students learn to recognize and fix errors" — [Ericson et al. 2023](https://strathprints.strath.ac.uk/86100/1/Ericson_etal_ITiCSE_2023_Conducting_multi_institutional_studies_of_Parsons_problems.pdf)
- Tests as specification: Ruby Koans asks you to "run the koan and see it fail (red), make the test pass (green), then take a moment and reflect upon the test to see what it is teaching you and improve the code to better communicate its intent (refactor)", and "they teach you culture by basing the koans on tests" — [rubykoans.com](https://www.rubykoans.com); Rustlings: "Some exercises contain tests that need to pass for the exercise to be done" — [rustlings usage](https://rustlings.rust-lang.org/usage/); Khan Academy's StructuredJS checks each step's structure — [Khan Academy CS blog](https://cs-blog.khanacademy.org/2013/08/introducing-programming-challenges.html?m=0)
- Extend-this-exercise ladders: Advent of Code part two reuses the input with "some kind of twist or change to the first puzzle's requirements" — [MIT Technology Review (search summary)](https://www.technologyreview.com/2021/12/17/1042483/puzzle-challenge-coding-christmas/); Project Euler's "inductive chain learning" — [Project Euler About](https://projecteuler.net/about); HtDP's "themed sequences of exercises" across parts — [HtDP 2e preface](https://htdp.org/2024-11-6/Book/part_preface.html); LPTHW's "Study Drills" — [Kinokuniya listing](https://www.kinokuniya.co.jp/f/dsg-02-9780138270575)
- One exercise per concept vs capstone: Exercism Concept Exercises target "first-time concept usage" at 5-10 minutes each, Practice Exercises are the larger mentored ones — [Exercism docs, Concept Exercises](https://exercism.org/docs/building/product/concept-exercises); the Rust Book's concept chapters vs three project chapters — [Rust Book introduction](https://doc.rust-lang.org/book/ch00-00-introduction.html); Atomic Kotlin's "handful of small exercises" per atom — [Atomic Kotlin introduction](https://leanpub.com/read/AtomicKotlin/introduction)
- Critique a given solution: Rustlings' "Most exercises contain an error that keeps them from compiling, and it's up to you to fix it!" — [rustlings 5.6.1 README](https://raw.githubusercontent.com/rust-lang/rustlings/5.6.1/README.md); Ericson's studies compare "solving Parsons problems, fixing code, and writing code from scratch" as three conditions — [Ericson PhD defense, Georgia Tech](https://hg.gatech.edu/node/603172); Exercism mentors are told to describe alternatives rather than hand over "the (better) solution" — [Exercism, Mentoring Mindset](https://exercism.org/docs/mentoring/mindset)
- Hint before solution, in print: Bentley's hints are "further questions providing insightful ways of approaching a solution", followed by solution outlines — [Linux Journal review](https://www.linuxjournal.com/node/3846); Rustlings' hint is on demand and separate from the solution — [rustlings usage](https://rustlings.rust-lang.org/usage/); Atomic Kotlin offers hints and then the solution — [Atomic Kotlin introduction](https://leanpub.com/read/AtomicKotlin/introduction)
- Difficulty labels: Knuth's 0-50 with M/HM — [Wikipedia](https://en.wikipedia.org/wiki/The_Art_of_Computer_Programming); Hett's one to three stars — [L-99](https://www.ic.unicamp.br/~meidanis/courses/problemas-lisp/L-99_Ninety-Nine_Lisp_Problems.html); Codewars kyu, voted during beta — [Kata Beta Process](https://www.codewars.com/topics/kata-beta-process)

### Inferences

- The reader's three-step ladder (hint, skeleton, solution) already combines Bentley's hint-then-outline with HtDP's template step (the skeleton is a function template with the body elided).
  The devices not yet in it are: a difficulty label per exercise; a second, labeled solution ("readable" vs "clever", or two styles under Lopes-style constraints) with a short pros/cons note; a "common wrong turns" paragraph; a part-two extension that changes the requirement; and a critique exercise that hands the reader a flawed solution.
- Static-compatible from the list: all of the above. Needing a runtime: tests as the specification (though a book can print the tests and ask the reader to make them pass, as Ruby Koans is distributed as plain files). Needing a community: solution grouping, voting, mentoring.

### Gaps

- No source was found for a book that prints "common wrong answers" for intermediate or advanced material; LPTHW's device is for beginners.
- No source was found for a published book whose solutions are written as a narrative of design decisions rather than annotated code; Exercism's Approach articles are the closest and are web-only.

## Key question 4: What evidence exists, and what did authors say did not work?

### Takeaway

The only controlled evidence in this set is Ericson's Parsons-problem research (faster than writing or fixing code, same pretest-to-posttest gain; adaptation helps more learners finish).
Everything else is author retrospective: Downey called his second-edition exercises uneven, Rustlings rewrote and polished every exercise while writing the solutions, Exercism rebuilt to stop learners being blocked on mentors, and reviewers name the absence of exercises (Learn You a Haskell) and the absence of explanations (The Little Schemer) as the failure modes at the two extremes.

### Cited Findings

- Documented evidence: across three studies, "students can complete Parsons problems significantly faster than fixing or writing code while achieving the same learning gains from pretest to posttest", and "adaptation helped more learners successfully solve Parsons problems" — [Ericson, PhD defense, Georgia Tech, 2018](https://hg.gatech.edu/node/603172); the ITiCSE 2017 paper is "Solving Parsons problems versus fixing and writing code" — [ACM DL](https://dl.acm.org/doi/10.1145/3141880.3141895) (abstract not fetched, HTTP 403)
- Documented evidence: "Students in the Parsons as Help group achieved significantly higher practice performance and problem-solving efficiency than students who wrote code without help, while achieving the same level of posttest scores" — [Hou, Ericson, Wang, ICER 2022](https://web.eecs.umich.edu/~xwanghci/papers/ICER22.pdf) (search summary)
- Documented evidence (adjacent): in a 2021 study of an interactive computing textbook, "students' active interactions ... including changing, adding, and executing code in addition to manipulating visualizations, are significantly stronger in predicting student performance than conventional reading metrics"; the textbook studied was Jupyter-based, not Runestone — [SIGCSE 2021 via Unpaywall](https://unpaywall.org/10.1145%2F3408877.3432361) (search summary)
- Platform data, not a study: 350 of 500 recent TwoFer solutions unique — [Exercism blog, Dig Deeper](https://exercism.org/blog/dig-deeper)
- Author retrospective: "the exercises in the second edition were uneven" — [Think Python 3e preface](https://allendowney.github.io/ThinkPython/chap00.html)
- Author retrospective: Rustlings 6 was "a complete rewrite", "While writing the solutions, all exercises have been polished", and the "I AM NOT DONE" marker was dropped — [rustlings CHANGELOG](https://raw.githubusercontent.com/rust-lang/rustlings/main/CHANGELOG.md)
- Author retrospective: Exercism v3 "aiming to fix issues present in v2, especially around being blocked while waiting for a mentor" — [exercism/v3 README (search summary)](https://github.com/neiesc/v3)
- Author retrospective: Knuth re-rates research exercises once solved and still asks readers to check the hard ones — [cs.stanford.edu errata (search summary)](https://cs.stanford.edu/%7Eknuth/err1.textxt); [i-programmer](https://www.i-programmer.info/news/112-theory/11495-donald-knuth-at-80-still-improving-taocp.html)
- Reader criticism, no exercises: Learn You a Haskell — [rmathew review](https://rmathew.com/2015/lyah.html)
- Reader criticism, no explanations: The Little Schemer "literally never explains anything directly" — [Invent with Python review](https://inventwithpython.com/blog/book-review-the-little-schemer.html)
- Opinion, no evidence cited: Brilliant's and Runestone's prefaces state active-learning rationale without citations — [Brilliant, Why Brilliant](https://brilliant.org/help/why-brilliant); [Runestone preface](https://cs.roanoke.edu/Fall2019/CPSC120/thinkcshpy/FrontBackMatter/prefaceinteractive.html)

### Inferences

- The Parsons evidence supports the reader's skeleton step directly: a solution with structure given and bodies elided is a Parsons-like reduction of cognitive load, and the studies found no learning loss from that reduction.
- The two reviewer complaints bracket the design space: an exercise with no solution and a solution with no explanation both fail readers. A revealed solution should carry the reasoning, not only the code.

### Gaps

- No published study of SICP's, HtDP's, or TAOCP's exercise formats was found.
- No peer-reviewed study of Exercism, Codewars, or Rustlings was found; a search for Exercism research returned only unrelated mentoring literature.
- Numeric effect sizes for the Parsons studies could not be extracted: the NSF PDF parsed as binary and the ACM page returned HTTP 403.
- No author retrospective was found from Eckel on the decision to sell Thinking in Java solutions separately, nor from Ramalho on Fluent Python's exercise policy.
