# Guard the Attempt, Ground the Assistant

The ladder's largest unrealized gains sit at its two edges, before the first rung and beside the page,
and the second edge decides whether the first pays.
A 2026 meta-analysis of ten learning studies (1,069 participants) puts the pooled effect of generative-AI access on later unassisted performance at **g = 0.14 with a confidence interval across zero**,
and the one moderator that explains the spread is whether the model was present at the test: g = 0.76 with it, g = −0.06 without ([arXiv 2605.04779](https://arxiv.org/abs/2605.04779)).
The study nearest your reader, 52 junior developers learning the Trio library, scored **50% on an unassisted quiz with an assistant against 67% without** (d = 0.738) ([Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)).
The one guarded design with a measured outcome, a hint-only GPT-4 tutor that carried the teacher's solution in its prompt and refused to give it, closed a 17% exam deficit to a null ([PNAS](https://www.pnas.org/doi/10.1073/pnas.2422633122)).
So the first new device is a per-exercise tutor prompt and a reader-facing repository instructions file, both built on that prompt's three rules: show your attempt first, get the least hint that unblocks you, and the full solution stays closed until you open the ladder's own.
The second is a committed, written attempt and a specific prediction before the first rung, which the pretesting and generation literatures support at d ≈ 0.30 to g ≈ 0.54 when the guess is committed, and which has no support as a timer or a global confidence rating.
The third is a stated "done when" criterion backed by a runnable check (a test file with a documented import name, a doctest, or a named `ty` diagnostic) as a rung between the shape and the solution, because mastery learning's 0.5 to 0.7 SD comes from the criterion and the retest, while supplied tests on their own raise completion and leave understanding where it was.
The fourth is a post-reveal self-diagnosis in three categories (wrong design, wrong detail, equivalent alternative), because students handed a model solution match surface features unless something forces a judgment.
The fifth is cross-chapter placement: a review exercise one to three chapters after a skill, a cumulative exercise at each part boundary, confusable patterns set side by side in one exercise, and chained exercises that start from a published solution.
Every finding here rests on undergraduates or schoolchildren except the Trio RCT and one graduate-student field study; no study tests any of these devices on experienced programmers working a book, and that gap is the one you cannot close by reading.

## An unguarded assistant cancels the ladder's gain; a grounded prompt restores the floor

The pattern across the LLM-in-practice literature is consistent: assisted performance rises, and unassisted learning stays flat or falls.
Bastani and colleagues ran a pre-registered RCT with about 1,000 high-school students, four sessions, GPT-4, three arms.
Practice scores rose 48% with an unrestricted chat and 127% with the guarded tutor, and the unassisted closed-book exam came out **17% lower for the unrestricted arm** and indistinguishable from control for the tutor arm, point estimate −0.004 on a 0 to 1 scale ([preprint PDF](https://nmdprojects.net/teaching_resources/bastani_generative_ai_can_harm_learning.pdf)).
The mechanism matters for 2026 models.
The most common message to the unrestricted chat was "What is the answer?", the chat answered correctly 51% of the time, and the exam harm did not track its error rate, so the authors attribute the harm to copying and not to being misled.
A model that answers correctly every time removes the "errors mislead" mechanism and leaves the copying one intact, so a better model shrinks none of this.

Your reader is experienced in Python and new to each chapter's idea, and the evidence says the assistant erodes the new part.
In the Trio RCT the lowest-scoring interaction patterns were delegation, progressive reliance, and iterative AI debugging (using the model to debug and verify instead of to understand), which was slow and low-scoring at once;
the high-scoring patterns were generate-then-interrogate, code with explanations, and conceptual inquiry with errors fixed by hand, the second fastest overall ([Anthropic](https://www.anthropic.com/research/AI-assistance-coding-skills)).
Lehmann's field study of 113 graduate students in Python courses found the same split at the message level: solution requests lowered understanding (−0.312, p < 0.01) and explanation requests raised it (+0.249, p < 0.05);
solution requests were **54% of messages, 42% of them with no attempt** at the problem, and enabling copy-paste raised solution requests by about 3.1 per student ([arXiv 2409.09047](https://arxiv.org/html/2409.09047v2)).
Students above the pre-test median gained from access and those below understood less than controls, so prior knowledge protects, and the chapter's new idea is where your reader has the least of it.

Readers will not notice the loss, so a device that depends on them noticing fails.
Bastani's students rated the tutors' effect on their learning as far better than the exam measured.
METR's RCT with 16 experienced open-source maintainers found AI-assisted tasks took 19% longer while the developers predicted a 24% speedup beforehand and still believed in a 20% speedup afterwards ([METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)).
Lee and colleagues' survey of 319 knowledge workers found that confidence in the tool went with less critical thinking and self-confidence with more ([Microsoft Research](https://www.microsoft.com/en-us/research/?p=1135061)).
The earlier report recommends one early passage on the illusion of competence, on the ground that theory-based debiasing is the form that transfers ([Koriat & Bjork 2006](https://sites.lifesci.ucla.edu/psych-bjorklab/wp-content/uploads/sites/13/2016/07/Koriat_Bjork_2006_MC.pdf)).
This round extends that passage's content: it should carry the 17% and the 50-versus-67 numbers, and it should name the two patterns that preserve learning (ask for explanations, fix errors by hand) and the one that costs the most (paste the code and ask what is wrong).
Brender's AIED 2026 result says such a habit change is the durable part: 66 graduate students who used a Socratic-guidance tutor for six weeks showed higher learning gains afterward on an unconstrained LLM, and wrote more understanding-driven prompts, than students trained on prompt refinement ([arXiv 2607.03303](https://arxiv.org/abs/2607.03303)).

The prompt with evidence has three parts, and each maps onto a rung.
Bastani's tutor prompt told the model to ask the student for the work done so far and the sticking point before helping, to give "as little information as possible" first and escalate, to provide the full solution under no circumstances, to confirm a student-supplied answer and ask for an explanation of it, and it carried the teacher's correct solution, its steps, and the likely mistakes ([preprint PDF](https://nmdprojects.net/teaching_resources/bastani_generative_ai_can_harm_learning.pdf)).
The first part is the ladder's attempt-first rule.
The second is the "Where to look" rung in dialogue form.
The third part is the one a per-exercise prompt can carry and a vendor "study mode" cannot: the reference solution and the design criteria the chapter states, so the hints are correct and in the book's idiom.
Kumar's pre-registered experiment with 1,200 adults on math problems adds the ordering: LLM explanations helped most when the participant attempted the problem first, and explanations with arithmetic errors still beat seeing the answer alone ([SSRN](https://papers.ssrn.com/abstract=4641653)).
Note the ceiling: the guarded tutor produced no gain over practicing alone.
A hint-only prompt protects the floor the ladder stands on; it accelerates nothing.

The reviewer role after the reveal needs its own guards, because feedback models invent faults.
Azaiz and colleagues found that giving GPT-4 the unit-test results raised feedback quality, and that when the reference solution and the tests disagreed on a rounding detail the model "described errors in correct solutions that do not exist" ([arXiv 2403.09744](https://arxiv.org/pdf/2403.09744)).
An EDM 2024 paper found over 23% hallucinated content in two feedback systems, and a 2025 benchmark of four models on 45 student solutions found 37% of hints wrong in some way ([EDM 2024](https://educationaldatamining.org/EDM2024/proceedings/2024.EDM-short-papers.49/index.html); [arXiv 2503.14630](https://arxiv.org/abs/2503.14630v1)).
Three instructions follow.
The prompt says the reference is one correct design and asks the model to judge the reader's version against the chapter's stated criteria, so a correct alternative passes.
It asks the model to quote the line it criticizes and to run the exercise's tests before asserting a bug.
And the book tells the reader that reviewer output is a hypothesis to check, which is the attitude the Trio study's "conceptual inquiry" readers held.
Older models disobeyed "no code" instructions outright, giving model solutions "even when the LLM is prompted not to" ([arXiv 2306.05715](https://arxiv.org/abs/2306.05715v1));
2026 models follow instructions better, and no study measures compliance of a prompt the reader controls and can delete.

No published book carries a per-exercise tutor prompt or a repository tutor file, so the device is new practice with borrowed evidence.
Think Python 3e, Automate the Boring Stuff 3e, Python Crash Course 4e, and Deitel's Java 12e give chapter-level advice or prompt-writing exercises, and Think Python's chapter 1 tells readers an assistant can help with exercises without telling them to withhold the solution ([Think Python chapter 1](https://allendowney.github.io/ThinkPython/chap01.html)).
The hosted tutors hide their prompts server-side: CS50's Duck throttles with ten hearts that regenerate one per three minutes ([SIGCSE 2024 PDF](https://cs.harvard.edu/malan/publications/V1fp0567-liu.pdf)),
and Boot.dev's Boots knows the official solution, withholds it, charges XP for a question asked before the lesson is finished, and answers free afterward ([Boot.dev](https://www.boot.dev/lessons/e4fac74c-9d67-41ad-a85c-c579cb3ad76f)).
Boot.dev's shape is the one to copy: the tutor's role changes when the learner finishes.
A static book cannot detect finishing, but the ladder can: the prompt says "hint-only while the Solution rung is closed, reviewer once it is open," and the reader applies the rule.
The mechanism that needs no pasting is a repository-level instructions file that agentic tools read on their own, the form `AGENTS.md` documents as an open standard ([Addy Osmani](https://addyosmani.com/agents/15-agents-md/)).
Your repository has no such file, and its root `CLAUDE.md` addresses the author's sessions: a reader who opens the clone in Claude Code today receives gate procedures and `@record` rulings, and no instruction about the exercises.
A reader-facing file that carries the tutor rules, the book's conventions (`ty`, `@record`, the 60-column listings, the `#:` markers), and the per-exercise reference pointers is the cheapest of this report's devices to build and the one with the broadest reach.

## A committed guess before the first rung is worth d ≈ 0.3; a timer is worth nothing

The earlier report asks for an attempt-first sentence above each exercise set.
This round says what the attempt must be: written, committed, and specific.
Pan and Sana's five experiments (combined n = 1,573, expository passages) found a pretest before reading as good as or better than a posttest after it, across formats, feedback conditions, and retention intervals ([Athabasca record](https://pure.athabascau.ca/en/publications/pretesting-versus-posttesting-comparing-the-pedagogical-benefits-/)), and a citing paper reports the pretesting advantage over retrieval practice as **d = 0.30** ([Memory & Cognition 2022](https://link.springer.com/article/10.3758/s13421-022-01392-1)).
St. Hilaire, Chan, and Ahn's preregistered meta-analysis of prequestions gives the moderator that matters: the specific effect is g = 0.54 across 97 effects, **g = 0.65 when the learner must commit a guess and g = 0.22 when not**, the strongest moderator in the paper; the general effect on untested material is g = 0.04, and zero for text ([St. Hilaire et al. 2024](https://par.nsf.gov/servlets/purl/10511812)).
Kornell, Hays, and Bjork's six experiments and Metcalfe's review add the conditions: the guess needs to be informed, the correct answer needs to follow soon after, and the benefit vanishes for unrelated pairs or forced blind guesses ([PubMed](https://pubmed.ncbi.nlm.nih.gov/19586265/); [Metcalfe 2017](https://files.eric.ed.gov/fulltext/ED574569.pdf)).
Brod's review of predicting names the mechanism as surprise at a wrong prediction held with some confidence, which raises attention to the correction ([Brod 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8642250/)).

A written attempt is the commitment, and the response-mode literature says one is enough.
The programmed-instruction studies found covert responders learned as well as writers in most comparisons, including Valverde's Air Force radar trainees, who were adults ([DTIC AD0614014](https://apps.dtic.mil/sti/pdfs/AD0614014.pdf));
the exception was retention tested in the response's own mode, where overt practice won ([IIT record](https://contrails.library.iit.edu/item/160232)).
For programming the test mode is producing code, so the reader produces code at least once per exercise, and that production is the attempt before rung one.
Each later rung can be answered in the head.
No study compares a written attempt against a mental one before a reveal; this is the mechanism's requirement, not a measured difference.

The `#:` markers are a prediction target waiting for a prompt.
Crouch and colleagues' physics students who predicted a demonstration's outcome before watching learned more than students who watched alone, who learned about as much as students who saw nothing ([ComPADRE record](https://www.compadre.org/IntroPhys/items/detail.cfm?ID=2329)).
The earlier report covers the adult prediction RCT; the addition here is a placement rule.
A marker printed beside its code is a comparison target after the run and becomes a prediction task only when the page asks for the prediction first, which a `<details>` around the output enforces by convention ([research.fi record](https://research.fi/en/results/publication/0675408423)).
Keith and Frese's meta-analysis of 24 error-management-training studies, most on adults learning software, found that letting trainees err and treating errors as information beat step-by-step training, most on transfer, and more so when trainees were told to expect errors ([Metcalfe 2017](https://files.eric.ed.gov/fulltext/ED574569.pdf)).
One line at the head of each Solutions file, saying the first attempt is expected to be wrong in places and the difference is the information, is that instruction in print.

A confidence rating is a measurement with a near-zero direct effect, so it earns its place by what it enables.
Double, Birney, and Walker's meta-analysis puts the reactivity of judgments of learning at **g = 0.054**, positive for related pairs and absent for unrelated ones ([Durham record](https://durham-repository.worktribe.com/output/2253677/a-meta-analysis-and-systematic-review-of-reactivity-to-judgements-of-learning)), and Birney's 252 industry managers performed worse on hard reasoning items when asked to rate confidence ([Durham record](https://dro.dur.ac.uk/20799)).
Hypercorrection is the thing it enables: high-confidence errors are corrected more than low-confidence ones, the effect holds a week later, and the high-confidence errors that escape correction are the ones most likely to return ([WUSTL record](https://profiles.wustl.edu/en/publications/the-hypercorrection-effect-persists-over-a-week-but-high-confiden/)).
The wording that fits both findings is a specific prediction after the attempt, placed above the shape rung: "Does your version raise an exception on an empty list? Write yes or no before opening this."
A global "how good is your solution" is the form that hurt the managers.
Callender's two classroom studies found calibration improves across repeated judgments with feedback ([Springer record](https://link.springer.com/doi/10.1007/s11409-015-9142-6)), and a yes-or-no prediction paired with a `#:` marker gives the reader one calibration point per exercise with no instructor.

The stop rule has evidence, and it is a progress rule, with no minutes in it.
Roll, Baker, Aleven, and Koedinger's within-student analysis of 25,337 tutor actions found that clicking through hints to the answer cut a 50% chance of learning the next step to **14%, 7%, and 19%** on high-, medium-, and low-skill steps, while on low-skill steps trying and failing raised it to 68%, above asking for help ([Roll et al. JLS](https://learninganalytics.upenn.edu/ryanbaker/Roll%20HT%20JLS%20clean.pdf)).
The group's later review reports that teaching students to seek help well changed their behavior and left their learning unchanged ([Aleven et al. 2016](https://cris.iucc.ac.il/en/publications/help-helps-but-only-so-much-research-on-help-seeking-with-intelli/)), so a written policy prevents the click-through pattern and does no more than that.
Metcalfe and Kornell's region-of-proximal-learning model gives the wording: learners stop studying an item when their judged rate of learning nears zero, and under free choice spend their time on medium-difficulty items where the curve still rises ([Metcalfe & Kornell 2005](https://psychology.columbia.edu/sites/default/files/2016-11/Metcalfe.Kornell.2005_0.pdf));
the labor-in-vain effect is the failure on the other side, extra minutes on the hardest items with almost no gain ([PMC review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11273422/)).
"Attempt for twenty minutes" has no support in any source found.
"Open Where to look after a failed attempt you can describe; open the next rung when your last few minutes changed nothing in your file" has the model behind it.
Shih, Koedinger, and Scheines' response-time result closes the loop at the bottom: reading a full answer slowly and reflecting on it is what separated learning from copying ([Shih et al. 2008](https://www.cmu.edu/dietrich/philosophy/docs/scheines/Shih_Koedinger_Scheines_2008_EDM.pdf)), so the Solution rung opens with a task that takes time, which the diagnosis section below supplies.

A collapsible solution is peekable by construction, and peeking cancels feedback's value.
Marsh and colleagues found feedback "less useful when participants can peek at feedback before answering a question" and more useful after a delay between answer and feedback ([Marsh et al. 2012](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/07/Marsh_Lozito_Umanath_Bjork_Bjork2012.pdf));
Kulhavy's review of sixty studies found that on hard material students "guess at answers and try to match answers and feedback" ([Hattie & Timperley 2007](https://www.uky.edu/~gmswan3/575/Hattie_Timperly_2007.pdf)).
Clariana's gradient says where the guard belongs: delayed feedback's advantage over immediate was −0.06 on easy items, 0.35 on midrange, and **1.17 on difficult items**, the ones where the reader does the most processing before the reveal.
The reader's own attempt is the delay, which costs the book nothing.
The Solution rung is the rung to guard with a one-line precondition ("run your version against the tests before opening this"), and the design explanation inside the rung goes after the code, which keeps a second small delay before the "why".

## A "done when" line and a runnable check make the shape rung a mastery criterion

Mastery learning's effect comes from a stated criterion and a retest, and both work without an instructor.
Across 108 controlled evaluations the Kuliks found mastery programs raised examination performance, more for weaker students, with self-paced programs cutting completion rates in college classes ([Kulik et al. 1990](https://www.academia.edu/81783373/Effectiveness_of_Mastery_Learning_Programs_A_Meta_Analysis));
across 75 PSI studies the exam advantage was 73.6 against 65.9 and grew to about 14 points on exams given months later ([Athabasca, PSI data](https://psych.athabascau.ca/open/keller/data.php)).
Hattie's database puts programmed instruction at **d = −0.04** beside mastery learning at 0.53 to 0.58 ([Hattie & Timperley 2007](https://www.uky.edu/~gmswan3/575/Hattie_Timperly_2007.pdf); [Hattie list](https://www.teacherstoolbox.co.uk/?p=6501)), which says the frame-and-confirm mechanics added nothing and the criterion-and-retest loop did the work.
Three PSI components need a person (proctor, grade contingency, pacing deadlines) and two need none (the criterion, the retest on an alternate form).
A Solutions file carries the criterion as one line above the hint, "Done when: the tests pass, `ty` reports nothing, and a disconnected responder receives no further updates," and the repository's test file certifies it without judging style, which is the proctor's job minus the person.
The retest is the earlier report's second small exercise on the same objective; this round adds the criterion in front of it.

Supplied tests raise completion and leave understanding where it was, in every study found.
Fridge's dissertation is the closest design to a test file published with an exercise: 144 introductory Java students used Web-CAT against researcher-written tests, project scores rose with usage, and the one significant survey difference was that **high-usage students reported lower understanding** ([Fridge dissertation](https://ircommons.uwf.edu/esploro/outputs/doctoral/An-Investigation-of-the-Impact-of/99380090747406600)).
Gabbay and Cohen's MOOC comparison (4,652 learners) found higher engagement and performance with test feedback and no difference in sense of learning ([EDM 2022](https://zenodo.org/record/6853125)).
Baniassad's third-year software-engineering course shows the behavior transfers past CS1: teams called the autograder 8.96 times per deliverable, 46% regressed at least once, a regression penalty cut calls by 48%, and a student wrote that with an autograder "I would just make changes and test using the autograder rather than write my own exhaustive test suite";
the authors conclude students "end up learning the grader, not learning the concepts" ([SIGCSE 2021](https://www.cs.ubc.ca/~rtholmes/papers/sigcse_2021_baniassad.pdf)).
A self-study reader has no penalty lever, so the design choices left are what a test reveals on failure and whether the test is the reader's only oracle.

Feedback that makes the reader explain beats feedback that hands over the answer, at the level of a test's failure message.
Marwan, Williams, and Price's randomized study found next-step code hints improved immediate performance and improved a later unaided task only when self-explanation prompts came with them ([Marwan et al. ICER 2019](https://isnap.csc.ncsu.edu/home/public/papers/MarwanICER2019.pdf)).
The Testing Tutor comparison found that conceptual feedback, which names the testing concept and leaves the missing case unnamed, produced higher coverage, fewer redundant tests, and higher grades than detailed coverage feedback ([arXiv 2011.13004](https://arxiv.org/abs/2011.13004)).
Keuning's review of 101 tools found most feedback stops at "knowledge about mistakes" and seldom says what to do next ([Keuning et al. 2018](https://research.ou.nl/en/publications/a-systematic-literature-review-of-automated-feedback-generation-f/)).
Marmoset's release tests show the count of failures and the names of the first two, and the course pages tell students to write a test that reproduces the failure before spending another token ([Marmoset docs](https://theory.cpe.ku.ac.th/~jittat/marmoset-docs/marmoset_introduction.html)).
So the test's failure message names the behavior in the chapter's words ("a responder disconnected during `announce()` still received this update") and leaves "expected X, got Y" to pytest's default.
Hidden tests are impossible in a cloned repository, so the Codewars sample-versus-attempt split becomes a convention: one visible smoke assertion in the exercise statement and a fuller suite in a file the hint names.
Students who paste a run's output in as the expected value get coverage with no correctness and "false confidence" ([CSEET 2017](https://conferences.computer.org/cseet/2017/papers/2536a170.pdf)), so the suite asserts hand-chosen values or a property, and Hypothesis fits the relational exercises where one input admits several valid outputs ([arXiv 2010.16305](https://arxiv.org/pdf/2010.16305)).

The type checker is a second oracle, and this repository has the machinery to keep that oracle correct across upgrades.
Rustlings' exercises "contain an error that keeps them from compiling," the first message in watch mode "is expected, since it describes the problem you're meant to solve," and the project is recommended beside the Rust Book ([Rustlings usage](https://rustlings.rust-lang.org/usage));
type-challenges counts a solution when the compiler accepts it in strict mode, with the same check running offline ([type-challenges](https://github.com/EdoTrotta/type-challenges)).
No study measures learning from a make-it-type-check exercise in any language.
Crichton's caveat is the design risk: a sound and incomplete checker produces diagnostics that mean a real bug or an analyzer limit, and learners must tell the two apart ([arXiv 2011.06171](https://arxiv.org/abs/2011.06171)).
A `ty` false positive would break a make-it-type-check exercise, so each such exercise needs the checker version pinned and the expected diagnostic re-probed on upgrade, which `check_quoted_diagnostics.py` does for quoted diagnostics today.
Two shapes follow: a file that fails `ty check` with a named diagnostic the reader clears, and an exercise that asks the reader to cause a named diagnostic (an annotation that must reject a call).
A doctest is the third oracle and the cheapest: Fluent Python's listings carry their expected output as `>>>` lines that GitHub renders and pytest runs ([example-code-2e](https://github.com/fluentpython/example-code-2e)), and a `>>>` block inside an exercise statement is at once the rendered example, the `#:` marker, and the test.

The runner matters more than the file.
Every project that publishes tests also publishes a single command with a watch mode and a hint command: Exercism's download gives instructions, a HELP file with the test command, optional hints, the test file, and a stub ([Exercism, working locally](https://exercism.org/docs/using/solving-exercises/working-locally));
Rustlings is one command with watch, `h` for the hint, and a done-or-pending list;
Python Koans is `python contemplate_koans.py` with a save watcher ([python_koans](https://github.com/gregmalcolm/python_koans)).
Chapter 30's folder carries three `test_*.py` files beside the generated solutions, and `tip hint CH=30 N=3` prints the ladder's rungs one per run, so a `tip exercise CH=30 N=3 PATH=my_attempt.py` that runs the exercise's test against a path the reader passes, with a watch option, is the Rustlings shape on existing tooling.
It needs a documented import name per exercise so one test runs against the reader's attempt and the committed solution alike.
Exercism's v3 retrospective is the caution: the v2 failures were in exercise design ("the original exercises were never designed to teach language concepts"), and the test mechanism was fine ([rationale-for-v3](https://github.com/exercism/v3/blob/master/docs/rationale-for-v3.md)).
No source reports what fraction of a book's readers run its tests; the nearest data is that students check feedback almost every time it is one click away, 64 checks per 66 submissions, and leave 28% of feedback pages unread ([arXiv 2507.14235](https://arxiv.org/html/2507.14235v1)).

## After the reveal, the reader diagnoses the difference and does not reread

The content ordering of feedback confirms the earlier report's verdict that rung three is where to invest, and this round supplies the numbers and the brake.
Van der Kleij's meta-analysis of 70 effects in computer-based environments puts elaborated feedback at **0.49, knowledge of the correct response at 0.32, and knowledge of results at 0.05**, with elaboration strongest for higher-order outcomes ([ACU record](https://acuresearchbank.acu.edu.au/item/86y84/effects-of-feedback-in-a-computer-based-learning-environment-on-students-learning-outcomes-a-meta-analysis));
Wisniewski, Zierer, and Hattie's 435 studies put high-information feedback at d = 0.99 against 0.46 for corrective ([Frontiers 2020](https://www.frontiersin.org/articles/10.3389/fpsyg.2019.03087/full)).
The brake is Kulhavy's 1985 study: readers given the correct answer alone outperformed readers given discussions of each wrong alternative, and the result "was mediated by the readers' confidence," with confident readers using any feedback well ([Hattie & Timperley 2007, p. 91](https://www.uky.edu/~gmswan3/575/Hattie_Timperly_2007.pdf)).
So the solution's explanation states the design choice and the alternative it rejects, and a note on a wrong design stays short and points at the correct construct instead of cataloguing ways to be wrong.

Crowder's branching contributes a diagnosis, and the reader does the routing.
A branching program ends each frame with a multiple-choice question whose wrong alternatives each route to a page that explains that error ([KnowledgeJump](https://knowledgejump.com/history_learning/branching.html)).
The best-documented comparison, a 1964 Air Force study with adult trainees, found branching produced more errors on the way and the same criterion-test performance as the linear program ([DTIC AD0609801](https://apps.dtic.mil/sti/pdfs/AD0609801.pdf)).
The earlier report reads that null as "avoid branching," and this round refines it: the mechanism (routing) added nothing, and the content (a named misunderstanding with its answer) is the elaborated feedback that measures 0.49.
In a static ladder the content survives as entries the reader selects by recognizing their own attempt, "If your version kept the responders in a `dict` keyed by name, the duplicate-name case fails because...", placed between the shape and the full solution.
One or two per exercise, for the predictable wrong turns, is the frame size the 1964 authors recommended.

Self-diagnosis against a model solution helps, and students handed a detailed solution match surface features instead.
Mason, Yerushalmi, Cohen, and Singh had about 200 physics students diagnose their graded quiz solutions with an oral outline and rubric, a detailed written solution, or the final answer plus notes and textbook;
on the challenging transfer problem the notes-only group scored **51% against 35%** for the written-solution group, and diagnosis quality predicted transfer in the notes-only group alone ([arXiv 1602.07253](https://arxiv.org/pdf/1602.07253)).
Safadi and Yerushalmi's 180 students found the significant differences between their work and the sample, treated the sample as an "ultimate template," and flagged surface deviations as flaws ([PER-Central](https://www.per-central.org/items/detail.cfm?ID=9497)).
That template failure is the design constraint on a diff prompt.
"Compare your solution to the reference" invites matching variable names and ordering and lets the reader declare every difference a fault.
Three categories counter it: wrong design, wrong detail, equivalent alternative.
"Equivalent alternative" is the category Safadi's students lacked, and it exists only if the solution's explanation says which choices are free (a `list` or a `dict` for the responders, a method or a `lambda`) and which choices are the point (the broadcaster holds no state about its responders).
The notes-only result also supports the ladder's order: "Where to look" is the notes-only condition, and the full solution's design explanation stays out of the shape rung.

The two reflection questions with evidence come in an order.
Heemsoth and Heinze's randomized field experiment with 174 seventh- and eighth-graders found that explaining the rationale behind one's own error produced more procedural knowledge at post and follow-up, and more conceptual knowledge at follow-up, than reflecting on the correct solution to the same errors ([Leibniz-IPN record](https://www.leibniz-ipn.de/en/research/publications/secondary-school-students-learning-from-reflections-on-the-rationale-behind-self-made-errors)).
Siegler's children learned most from "How do you think I knew that?", explaining the correct reasoning, over explaining their own ([Metcalfe 2017](https://files.eric.ed.gov/fulltext/ED574569.pdf)).
The two results are on children, agree in direction with Metcalfe's review, and give the wording: first "why did your version seem right?", then "why does the reference make this choice?".
Externally presented wrong answers can harm memory where self-generated errors help, so the wrong-design note is framed as the reader's own likely attempt and not as a list of bugs to read.

A fluent solution inflates confidence, and the counter is a task with the solution out of sight.
Mihalca and colleagues' 67 university students overestimated their performance after incomplete worked examples, while completion problems and conventional problems produced neither over- nor underestimation, and higher-prior-knowledge students did better with conventional problems ([Erasmus record](https://repub.eur.nl/pub/91167)).
The shape rung is a completion problem in those terms, which is a measured reason to keep it as a stop and not a preview, and the second finding says the attempt-from-scratch matters more than the shape for your reader.
Hörnlein and Kulgemeyer's two studies (n = 244 and 175) found a demanding task after a physics explainer video cut the illusion of understanding by **d = 0.69** against the video alone ([arXiv 2512.02824](https://arxiv.org/abs/2512.02824)).
In a `<details>` ladder the reader can collapse the solution, so the prompt says so: close the solution and rewrite one function body, or write the input that breaks it, before moving on.
Learners in the errorful-generation studies judged the better method worse ([Westminster record](https://westminsterresearch.westminster.ac.uk/item/8y95x/the-benefit-of-generating-errors-during-learning)), so a sentence saying that attempting and erring feels worse and works better addresses a measured misbelief.

Reflection prompts split by whether they demand something the page lacks.
Choi and colleagues' four-week online data-science master's course, the one adult result, found hints with reflection prompts raised delayed transfer performance over hints alone ([TUM record](https://portal.fis.tum.de/en/publications/the-benefit-of-reflection-prompts-for-encouraging-learning-with-h/));
their 2025 programming-course preprint found directed, planning-focused prompts before a hint produced the best reflections and the lowest satisfaction, with no immediate performance difference ([arXiv 2512.04630](https://arxiv.org/abs/2512.04630)).
A data-structures course coded 87% of answers to "What did you learn?" and "What was the hardest part?" at the two highest reflection levels and measured no learning ([ASEE record](https://peer.asee.org/37651)), and Dunlosky's review rates summarization and rereading lowest ([Kent State summary](https://www.kent.edu/node/230016)).
The earlier report found an appended "explain why" after a full solution hurt; the reconciling rule is generation against restatement.
A prompt earns its place when the reader must produce a failing input, a reason the wrong design looked right, or a second place the pattern fits.
"What would break this?" has no direct study and is the generative form of "how could this be wrong," which Koriat, Lichtenstein, and Fischhoff found offsets overconfidence ([Metcalfe 2017](https://files.eric.ed.gov/fulltext/ED574569.pdf)); "where else does this apply?" is plausible and unmeasured.
A directed prompt is one line, placed where the reader is stopped, just above the next rung.

## Spacing, interleaving, and chaining are the levers the ladder leaves untouched

Spaced retrieval is the best-supported technique in the literature, and textbooks rarely use it.
Cepeda's review of 839 assessments across 317 experiments found the optimal gap between study and review grows with the retention interval ([Cepeda et al. 2006](https://www.evullab.org/pdf/CepedaPashlerVulWixtedRohrer-PB-2006.pdf)),
and the 2008 study of 1,350 adults tested up to a year later put the optimal gap at **20 to 40 percent of a one-week horizon and 5 to 10 percent of a one-year horizon** ([Cepeda et al. 2008](https://www.evullab.org/pdf/CepedaVulRohrerWixtedPashler-PS-2008.pdf));
a good gap beat a poor one by up to 150 percent at six months ([Cepeda et al. 2009](https://home.cs.colorado.edu/~mozer/Research/Selected%20Publications/reprints/Cepedaetal2009.pdf)).
Dunlosky's review rates distributed practice and practice testing "high utility" and gives 15 percent of the desired retention interval as the gap ([APS summary](https://www.psychologicalscience.org/news/releases/which-study-strategies-make-the-grade.html)).
Carpenter, Cepeda, Rohrer, Kang, and Pashler note that "in most mathematics textbooks, each set of problems is devoted to the most recent lesson" and give three recommendations: a brief review of material from several weeks earlier in each lesson, questions on earlier material in homework, and cumulative exams ([Carpenter et al. 2012](https://digitalcommons.usf.edu/psy_facpub/1756));
Rohrer's analysis of six seventh-grade texts found **78 percent of practice problems blocked** ([Springer](https://link.springer.com/doi/10.1007/s10648-020-09516-2)).
Rowland's meta-analysis adds that recall tests beat recognition and that the benefit grows with feedback and with a retention interval of a day or more ([Rowland 2014](https://courseware.epfl.ch/assets/courseware/v1/fdde2f0aa590bf3b1324077a6bf1540c/asset-v1%3AEPFL%2BDEMO%2B2020%2Btype%40asset%2Bblock/Rowland2014-meta-analysis.pdf)).

A reader working Part III keeps the Part I and II skills for months, so the horizon is months and the rule puts the first return one to three chapters after a skill, with a second return a part later.
A return in every chapter is too dense by this rule, and a return at the end of the book alone is too sparse.
Carpenter's three recommendations become a "from earlier chapters" subsection in each exercise set with one or two retrieval exercises on skills from two to four chapters back, phrased recall-then-apply (write the idiom from memory, then use it), and a cumulative exercise at each part boundary that needs several chapters' skills in one program.
The ladder supplies Rowland's feedback condition: a review exercise whose hint names the earlier section and whose solution is one click away is retrieval with delayed feedback.
Forgetting before the review is expected and relearning is fast, so a hint rung that restates the earlier idiom in one line is a legitimate design.
Samani and Pan's physics students rated interleaved homework harder and believed they learned less from it while surprise tests showed the opposite ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8589969/)), so one line at the head of the review subsection saying why it is there is cheap and addresses that misjudgment.

Interleaving wins where categories look alike, which describes the Patterns part and little else in the book.
Brunmair and Richter's 59-study meta-analysis puts the pooled effect at g = 0.42, rising with between-category similarity and material complexity: **paintings g = 0.67, mathematical tasks g = 0.34, expository text nonsignificant**;
the effect held for items in immediate succession (g = 0.73) and vanished for temporally spaced items (g = 0.22, interval across zero), and the authors are "reluctant to recommend interleaving" for math tasks, text, grammar, or words ([Brunmair & Richter 2019](https://www.psychologie.uni-wuerzburg.de/fileadmin/06020400/2019/Brunmair_Richter_in_press__2019_META-ANALYSIS_OF_INTERLEAVED_LEARNING.pdf)).
Rohrer's randomized trial with 787 seventh-graders found d = 0.83 when the interleaved problems required students to classify before solving ([IES](https://ies.ed.gov/use-work/awards/interleaved-mathematics-practice)), and a year-long Nigerian trial found a 0.29 SD short-term gain and no gain on the cumulative year-end assessment ([EdWorkingPaper](https://edworkingpapers.com/ai23-876)).
Yan's review reports that complex skills and novices need blocked practice first ([Yan 2021](https://www.Gwern.net/doc/psychology/spaced-repetition/2021-yan.pdf)).
Design patterns are the low-discriminability case: a third-year course reports *Strategy* confused with *Decorator* and the structural group confused through "overlapping intent" ([arXiv 2508.16770](https://arxiv.org/pdf/2508.16770)), and State and Strategy share a class diagram.
The earlier report asks for cumulative exercises that interleave confusable patterns; the immediate-succession finding sharpens the placement.
The contrast goes inside one exercise, "here are three requirements; which needs *State*, which needs *Strategy*, which needs neither; implement the two that do," and does not rely on the other pattern being several chapters back.
A Part I or II chapter's own set stays blocked on its idiom, and the interleaved contrast lives in later review subsections and the part-boundary exercise.
No controlled study of interleaving on design patterns, on programming, or on adults past college age exists.

Attempting before instruction helps for design ideas and hurts for mechanics, so the pre-section pointer is rationed.
Sinha and Kapur's meta-analysis of 53 studies puts problem-solving-first over instruction-first at **g = 0.36** (0.37 to 0.58 at high fidelity to productive-failure principles), reversed for grades 2 to 5 and for domain-general skills ([Sinha & Kapur 2021](https://doi.org/10.3102/00346543211019105));
scaffolded and unscaffolded attempts did not differ (g = −0.08) ([ETH record](https://www.research-collection.ethz.ch/entities/publication/087241d3-ca0e-469e-a7f3-df9c122e2585)).
Loibl and colleagues found instruction-first better for procedural fluency and that delaying instruction on its own raised nothing ([Instructional Science 2020](https://link.springer.com/doi/10.1007/s11251-020-09528-z)), and a 2022 study found a worked-out inventing problem prepared future learning better than an open one ([Instructional Science 2022](https://link.springer.com/10.1007/s11251-022-09577-6)).
The one CS1 study, 20 students within-subjects, found the productive-failure session ahead on a delayed follow-up ([arXiv 2411.11227](https://arxiv.org/abs/2411.11227)).
The earlier report treats the order as settled by the textbook's own structure, citing the high-interactivity reversal; this round narrows rather than overturns that.
The placement suits a design decision (why `Protocol` over an ABC, when a *Visitor* beats a `match`) and does not suit syntax or API mechanics;
the attempt need not be open, since a skeleton with a stated goal and no guidance on the decision keeps the generation step and bounds the time;
and the section after the pointer names the typical failed attempts and shows why the canonical form resolves them, which is the consolidation that productive failure requires.
Prequestions give the ration: the specific effect is g = 0.54 and the general effect g = 0.04, and with 20-minute lectures the benefit stayed on the questioned content ([Toftness et al. 2018](https://pure.royalholloway.ac.uk/files/30437641/JARMAC_Toftness_et_al.pdf)), so one pointer per chapter, in front of the idea you most want kept, and end-of-chapter exercises for everything else.
The prior-knowledge outliers in St. Hilaire's meta-analysis were domain experts studying new material in their field, at about 80% prequestion accuracy, so the pointer belongs on the book's new material (the 3.15 features, the typing constructs) and not on general Python.

Chaining exercises across chapters supplies spacing at no authoring cost and carries a stranding cost that one rule removes.
No learning-science study of chained exercises exists; the evidence is Crafting Interpreters' practice and course data.
Nystrom keeps the main thread strictly cumulative with every line of code supplied, and keeps the challenges off it: "you should make those changes in a copy of your code. Later chapters assume your interpreter is unchanged" ([Crafting Interpreters](https://craftinginterpreters.com/introduction.html)).
Milestones in a third-year data-structures course raised on-time completion and correctness without raising withdrawals ([Codio summary](https://www.codio.com/blog/dividing-large-programming-projects-into-smaller-steps)), and Toronto's CSC108 cites week-to-week cumulation as what strands students who fall behind ([UofT](https://teaching.utoronto.ca/event/mastery-learning-in-an-introductory-computer-science-course/)).
Chaining exercises inverts Nystrom's rule, because the chain lives in the reader's code, which the book cannot see.
The full-solution rung is the fix: a chapter-N exercise that extends a chapter-M solution says "start from your own chapter M solution, or from `Solutions/M/exercise_3.py`," so a reader who skipped M or diverged has a known-good start.
The cost is that the chapter-N exercise is written against the published M solution's interface, which becomes a contract you maintain, and the gate's `check_solutions.py` would need to learn the dependency.
Chains run within a part, where the order is linear, and stop at part boundaries, where a reader who starts at Functional has no chapter-M code; one or two chains per part is the "from earlier chapters" slot's strongest occupant.

Two smaller sequencing results close the section.
Variation theory gives a vocabulary for ordering a chapter's own set (contrast against the nearest alternative, generalization across data, separation varying one parameter, fusion varying two in the stretch exercise), with a phenomenographic lineage in programming education and no controlled test ([Lam 2022](https://repository.eduhk.hk/en/publications/revisiting-variation-affordance-applying-variation-theory-in-the-/); [Eckerdal thesis](https://user.it.uu.se/~annae/FullAvh-Spikenheten.pdf));
the shape rung supports "keep everything else invariant," since a run of exercises can share one skeleton and change one line's worth of demand.
Within-set ordering is a null for rule-based material: Spiering and Ashby found easy-to-hard, hard-to-easy, and random orders equal when the category rule could be stated in words, with hard-first winning only for rules that could not ([PMC 2605282](https://pmc.ncbi.nlm.nih.gov/articles/PMC2605282)).
A chapter states its idiom in prose, so a ramp within the set is a completion and motivation choice, and the learning evidence is indifferent to it.

The table sorts this round's devices by what stands behind them and what each adds to the earlier report.

| Device | Standing | Adds to the earlier report | Verdict |
|---|---|---|---|
| Per-exercise hint-only tutor prompt carrying the reference solution and the chapter's criteria | Bastani 2025 (RCT, closed a 17% deficit to null; no gain); Kumar 2023 (attempt then explanation) | New | Build; role switches to reviewer when the Solution rung opens |
| Reader-facing repository instructions file (`AGENTS.md` or a reader `CLAUDE.md`) with tutor rules and the book's conventions | Practice; analog is CS50's grounding accuracy gain; no book found with one | New | Build first; the root `CLAUDE.md` is author-facing today |
| Reviewer prompt: reference is one correct design, quote the line, run the tests first | Azaiz 2024 (tests raise feedback quality; contradictory ground truth invents faults); 23 to 37% hallucination rates | New | Build, with "a hypothesis to check" in the prose |
| The illusion-of-competence passage carries the LLM numbers and the two preserving patterns | Shen & Tamkin 2026; Lehmann 2025; Brender 2026 (habit change persists) | Extends the one-passage recommendation | Add |
| Written, committed attempt before rung one | St. Hilaire 2024 (g = 0.65 with a committed guess vs 0.22); Pan & Sana (d ≈ 0.30); response-mode studies (code once) | Sharpens "attempt first" | Add; one written attempt, later rungs covert |
| Specific yes/no prediction above the shape rung | Hypercorrection (persists a week); JOL reactivity g = 0.05; managers hurt by global ratings | New | Add as a prediction, not a rating |
| Progress-based stop rule in the file header | Roll et al. (click-through 50% to 7 to 19%); region of proximal learning; labor in vain | New | Add; no minutes |
| "Expect errors" line in the file header | Keith & Frese (24 adult software-training studies) | New | Add |
| Guard line above the Solution rung; explanation after the code | Marsh 2012 (peekability); Clariana (1.17 on difficult items) | New | Add |
| "Done when" criterion above the hint | Mastery learning 0.52 to 0.58 SD; PI frames −0.04 | New | Add |
| Test file per exercise with a documented import name, failure messages in the chapter's words | Fridge, Gabbay (completion up, understanding flat); Testing Tutor, Marwan (explain beats hand-over) | Extends "printed test as specification" | Add; hand-chosen values or a property, no captured output |
| `tip exercise CH N PATH` runner with watch | Exercism, Rustlings, koans: runner plus hint is the universal shape | New | Build on `tip hint` |
| Doctest `>>>` block in the exercise statement | Fluent Python practice; rendered, marker, and test in one form | New | Add where the exercise is a function |
| `ty` diagnostic as oracle, pinned and re-probed | Rustlings, type-challenges practice; Crichton's false-positive caveat | Extends | Add for typing chapters; `check_quoted_diagnostics.py` is the re-probe |
| "If your version did X" entries between shape and solution | Van der Kleij (EF 0.49 > KCR 0.32 > KR 0.05); 1964 branching null on mechanism; Kulhavy 1985 brake | Refines "avoid branching" to "keep the content, drop the routing" | Add, one or two per exercise, short |
| Three-category diff (wrong design, wrong detail, equivalent alternative) | Mason 2016 (51% vs 35%); Safadi (template failure) | New | Add; the explanation names the free choices |
| Two reflection questions in order: own-error rationale, then the reference's reasoning | Heemsoth & Heinze 2016; Siegler 1995 (children) | Supplies wording for the contrast paragraph | Add |
| Close-and-regenerate task after the reveal | Mihalca 2015; Hörnlein 2025 (d = 0.69) | New | Add |
| "What did you learn?" and "hardest part?" prompts | ASEE (deep-sounding text, no gain); Dunlosky (summarization low) | Confirms the metacognitive-prompt null | Avoid |
| Review subsection one to three chapters later; part-boundary cumulative exercise | Cepeda 2006/2008; Carpenter 2012; Rowland (recall > recognition) | Extends the cumulative-exercise line with a schedule | Add |
| Confusable patterns side by side inside one exercise | Brunmair & Richter (succession g = 0.73 vs spaced 0.22) | Sharpens placement | Add in the Patterns part; keep Part I/II sets blocked |
| One attempt-first pointer per chapter, on a design idea | Sinha & Kapur (g = 0.36); Loibl 2020 (procedural reversal); prequestion general effect 0.04 | Narrows "order is settled" | Add once per chapter at most |
| Chained exercise with a published known-good start | Crafting Interpreters practice; milestone studies | New | Add one or two per part, within the part |
| Timer-based stop rule; global confidence rating; difficulty ramp for learning's sake | No support found; Birney 2017; Spiering & Ashby null | New | Avoid |

## Conclusion

The earlier report placed the ladder's marginal gains in the text of rung three.
This round moves the frame: the ladder's gains, wherever they sit, are bounded above by what the reader does with the assistant open beside the page, and the evidence says most readers ask it for the answer unless something intervenes.
The intervention with a measured outcome is a prompt that follows the ladder's own rungs, hint-only while the solution is closed and reviewer once it is open, grounded in the reference solution so its hints are right and in the book's idiom.
A static book cannot enforce that prompt, and a cloned repository can deliver it without a paste, through the one file agentic tools read unasked.
That makes the reader-facing instructions file the highest-leverage change in this report, and the one with no precedent to copy.

The second shift is that the rungs are now bracketed by two commitments the evidence requires and the page can request: a written attempt and a specific prediction before the first rung, a diagnosis in three categories and a regenerate-from-memory task after the last.
Every device in between (the criterion, the runnable check, the reader-selected wrong-design entries) exists to make the reader produce something the page does not contain, which is the one property shared by every technique here with a positive result and absent from every one with a null.
The measurement gap remains the size it was: one RCT on working developers, one graduate field study, and nothing on a book.
The repository can narrow it a little on its own, because `tip hint` and a `tip exercise` runner can log which rung a reader opens and when, locally and opt-in, and that log is the first data anyone would have on how experienced programmers climb a ladder like this one.
