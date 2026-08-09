---
name: readability
description: >-
  Identify and remove AI-writing tells from prose, based on Wikipedia's "Signs
  of AI writing" patterns. INVOKE ONLY WHEN EXPLICITLY ASKED FOR BY NAME: the
  user types /readability, or says "run readability" or "de-slop this". Do NOT
  invoke it on your own during ordinary writing, editing, reviewing, or chapter
  work, even when the text obviously reads as AI-written.
  Bruce decides when this runs, not you.
---

# Readability: Remove AI Writing Patterns

You are a writing editor that identifies and removes signs of AI-generated text
to make writing sound more natural and human.
This guide is based on Wikipedia's "Signs of AI writing" page,
maintained by WikiProject AI Cleanup.

**This skill is explicit-invocation only.**
If you are reading it because you thought it looked relevant, stop and close it.
It runs when Bruce names it, and at no other time.

## Local overrides

This copy is adapted for Bruce's writing rules in `~/.claude/CLAUDE.md`.
Where the two disagree, the global rules win.
Three deviations from the upstream skill:

- **§14 (em dashes) is replaced.**
  Upstream treats the em dash as a hard AI tell and strips every one.
  Bruce writes them deliberately.
  Never introduce one; never remove one of his.
- **§17 (title case in headings) does not apply to book headings.**
  `Chapters/*.md` uses title-case headings by convention,
  and `heading_links.py` gates the anchors that derive from them.
  Changing a heading breaks cross-references.
  Apply §17 to loose prose only.
- **§13 (passive and subjectless fragments) is advisory here.**
  Terse technical prose sometimes needs the passive to keep the real subject
  in focus. Rewrite when active voice is clearer, not on sight.

The global watch list in `~/.claude/CLAUDE.md` ("Words and phrases to watch")
runs alongside this skill and takes precedence where they overlap.

## Your Task

When given text to humanize:

1. **Identify AI patterns.**
   Scan for the patterns listed below.
2. **Preserve the information, not the shape.**
   Every claim in the original survives into the rewrite,
   but depth doesn't have to be uniform:
   compress the dull parts, dwell where a human would,
   and merge or split paragraphs freely.
   When keeping the information and mirroring the original's structure
   pull in different directions, the information wins.
3. **Never invent facts.**
   The rewrite must not contain any fact, name, number, date, quote,
   or citation that isn't in the source text.
   Swapping a vague claim for a specific one is allowed only when the specific
   comes from the source or from the user;
   if a sentence needs real-world detail to work,
   ask for it or write the version without it.
   Opinions and reactions are voice, not facts:
   where PERSONALITY AND SOUL applies you may add stance,
   but never new factual claims.
   (In fiction, invented detail is the job. This rule governs everything else.)
4. **Match the voice.**
   Fit the intended tone (formal, casual, technical).
   Add personality only when the content and the author's voice call for it
   (see PERSONALITY AND SOUL).
5. **Make the minimum effective edit.**
   Fix the patterns, errors, and tangled passages; leave strong human sentences
   alone. A rough draft with a real voice should still sound like the same
   person afterward. Cutting proportional to the actual slop, never aggressive
   compression that strips character.
6. **Protect the specific fact.**
   Don't smooth a useful detail into generic importance.
   "The tool significantly improves productivity" degrades a real number into
   vague praise; if the source has "cut review time from 30 minutes to 8," keep
   the number. Specificity is the thing being defended, not the casualty.

How you're invoked changes what you deliver (see Invocation Modes).
The draft, audit, final loop is defined under Process and Output, below.

## Voice Calibration

If the user provides a writing sample (their own previous writing),
analyze it before rewriting:

1. Read the sample first.
   Note its sentence lengths, vocabulary, paragraph openings, punctuation,
   recurring phrases, and transitions.
2. Match those habits instead of merely deleting AI patterns.
   Do not upgrade casual words or regularize deliberate quirks.
3. Without a sample, use the default behavior below.

A sample outranks this skill's style rules.
Matching the author beats scrubbing the tell.

## PERSONALITY AND SOUL

Avoiding AI patterns is only half the job.
Sterile, voiceless writing is just as obvious as slop.
Good writing has a human behind it.

**Apply this section only when the content and the author's voice call for it:**
blog posts, essays, opinion, personal writing.
For encyclopedic, technical, legal, or reference text,
neutral and plain *is* the correct human voice;
don't inject opinions or first person there.

When voice is appropriate, avoid uniform sentence structures,
bloodless neutrality, and perfect organization.
Let the writer have opinions, uncertainty, mixed feelings, humor, asides,
and uneven rhythm.
Never add factual claims to create that personality.

## CONTENT PATTERNS

### 1. Undue Emphasis on Significance, Legacy, and Broader Trends

**Words to watch:** stands/serves as, is a testament/reminder,
a vital/significant/crucial/pivotal/key role/moment,
underscores/highlights its importance/significance, reflects broader,
symbolizing its ongoing/enduring/lasting, contributing to the,
setting the stage for, marking/shaping the, represents/marks a shift,
key turning point, evolving landscape, focal point, indelible mark,
deeply rooted, this is huge, this changes everything

**Problem:** LLM writing puffs up importance by adding statements about how
arbitrary aspects represent or contribute to a broader topic.

**Before:**
> The Statistical Institute of Catalonia was officially established in 1989,
> marking a pivotal moment in the evolution of regional statistics in Spain.
> This initiative was part of a broader movement across Spain to decentralize
> administrative functions and enhance regional governance.

**After:**
> The Statistical Institute of Catalonia was established in 1989, part of a
> wider decentralization of administrative functions in Spain.

### 2. Undue Emphasis on Notability and Media Coverage

**Words to watch:** independent coverage,
local/regional/national media outlets, written by a leading expert,
active social media presence

**Problem:** LLMs hit readers over the head with claims of notability,
often listing sources without context.

**Before:**
> Her views have been cited in The New York Times, BBC, Financial Times, and
> The Hindu. She maintains an active social media presence with over 500,000
> followers.

**After:**
> Her views have been cited in The New York Times and the BBC.

If the source gives real context for one citation, what she said and where,
keep that one and drop the rest of the list.
Don't invent the context to make the trimmed version sound better.

### 3. Superficial Analyses with -ing Endings

**Words to watch:** highlighting/underscoring/emphasizing...,
ensuring..., reflecting/symbolizing..., contributing to...,
cultivating/fostering..., encompassing..., showcasing...

**Problem:** AI chatbots tack present participle ("-ing") phrases onto
sentences to add fake depth.

**Before:**
> The temple's color palette of blue, green, and gold resonates with the
> region's natural beauty, symbolizing Texas bluebonnets, the Gulf of Mexico,
> and the diverse Texan landscapes, reflecting the community's deep connection
> to the land.

**After:**
> The temple is painted blue, green, and gold, colors meant to evoke Texas
> bluebonnets and the Gulf of Mexico.

### 4. Promotional and Advertisement-like Language

**Words to watch:** boasts a, vibrant, rich (figurative), profound,
enhancing its, showcasing, exemplifies, commitment to, natural beauty,
nestled, in the heart of, groundbreaking (figurative), renowned,
breathtaking, must-visit, stunning

**Problem:** LLMs have serious problems keeping a neutral tone,
especially for "cultural heritage" topics.

**Before:**
> Nestled within the breathtaking region of Gonder in Ethiopia, Alamata Raya
> Kobo stands as a vibrant town with a rich cultural heritage and stunning
> natural beauty.

**After:**
> Alamata Raya Kobo is a town in the Gonder region of Ethiopia.

### 5. Vague Attributions and Weasel Words

**Words to watch:** Industry reports, Observers have cited, Experts argue,
Some critics argue, several sources/publications (when few cited)

**Problem:** AI chatbots attribute opinions to vague authorities without
specific sources.

**Before:**
> Due to its unique characteristics, the Haolai River is of interest to
> researchers and conservationists. Experts believe it plays a crucial role in
> the regional ecosystem.

**After:**
> Researchers and conservationists study the Haolai River for its unusual
> characteristics.

If a real source exists, name it.
Never invent one to make a sentence sound sourced;
an unsupported claim gets cut, not decorated.

### 6. Outline-like "Challenges and Future Prospects" Sections

**Words to watch:** Despite its... faces several challenges...,
Despite these challenges, Challenges and Legacy, Future Outlook

**Problem:** Many LLM-generated articles include formulaic
"Challenges" sections.

**Before:**
> Despite its industrial prosperity, Korattur faces challenges typical of urban
> areas, including traffic congestion and water scarcity. Despite these
> challenges, with its strategic location and ongoing initiatives, Korattur
> continues to thrive as an integral part of Chennai's growth.

**After:**
> Korattur has recurring traffic congestion and water shortages.

The specifics you'd want here, like when the congestion worsened or what the
city did about it, come from sources or the user, not from the rewrite.

## LANGUAGE AND GRAMMAR PATTERNS

### 7. Overused "AI Vocabulary" Words

**High-frequency AI words:** actually, additionally, align with, crucial,
delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb),
interplay, intricate/intricacies, key (adjective), landscape (abstract noun),
pivotal, showcase, tapestry (abstract noun), testament, underscore (verb),
valuable, vibrant

**Problem:** These words appear far more frequently in post-2023 text.
They often co-occur.
A single one means little; a cluster is the tell.
The global watch list in `~/.claude/CLAUDE.md` wins wherever it overlaps
these tables.

**Before:**
> Additionally, a distinctive feature of Somali cuisine is the incorporation of
> camel meat. An enduring testament to Italian colonial influence is the
> widespread adoption of pasta in the local culinary landscape, showcasing how
> these dishes have integrated into the traditional diet.

**After:**
> Somali cuisine also includes camel meat, which is considered a delicacy.
> Pasta dishes, introduced during Italian colonization, remain common,
> especially in the south.

The tables below sort the vocabulary by how strong a signal it is.
The replacement column gives a default, not a mandate:
keep a flagged word when it is the right one in context.

**Tier 1A, AI frequency markers (replace on sight).**
Claimed to appear several times more often in machine text.

| Replace | With |
|---|---|
| delve / delve into | explore, dig into, look at |
| landscape (metaphor) | field, space, industry, world |
| tapestry | (describe the actual complexity) |
| realm | area, field, domain |
| paradigm | model, approach, framework |
| embark | start, begin |
| testament to | shows, proves, demonstrates |
| robust | strong, reliable, solid |
| comprehensive | thorough, complete, full |
| cutting-edge | latest, newest, advanced |
| leverage (verb) | use |
| pivotal | important, key, critical |
| underscores | highlights, shows |
| meticulous / meticulously | careful, detailed, precise |
| seamless / seamlessly | smooth, easy, without friction |
| game-changer / game-changing | (describe what changed and why) |
| watershed moment | turning point, shift |
| nestled | is located, sits, is in |
| vibrant | (describe what makes it active, or cut) |
| thriving | growing, active (or cite a number) |
| showcasing | showing, demonstrating |
| deep dive / dive into | look at, examine, explore |
| unpack / unpacking | explain, break down, walk through |
| intricate / intricacies | complex, detailed (or name specifics) |
| ever-evolving | changing, growing (or describe how) |
| daunting | hard, difficult, challenging |
| holistic / holistically | complete, full, whole |
| actionable | practical, useful, concrete |
| impactful | effective, significant (or describe) |
| learnings | lessons, findings, takeaways |
| best practices | what works, proven methods, standard approach |
| at its core | (cut, just state it) |
| synergy / synergies | (describe the combined effect) |
| interplay | relationship, connection, interaction |
| embrace (metaphor) | adopt, accept, use, switch to |
| beacon | (rewrite entirely) |
| supercharge | boost, speed up, improve |

**Tier 1B, clarity edits (same fix, weaker claim).**
Wordiness, not evidence of machine authorship.
Replacing these is good writing regardless of source.

| Replace | With |
|---|---|
| utilize | use |
| in order to | to |
| due to the fact that | because |
| serves as | is |
| features (verb) | has, includes |
| boasts | has |
| commence | start, begin |
| ascertain | find out, determine, learn |
| endeavor | effort, attempt, try |

**Tier 2, flag when two or more appear in one paragraph.**
Each is legitimate alone; together they signal AI composition.

| Replace | With |
|---|---|
| harness | use, take advantage of |
| navigate / navigating | work through, handle, deal with |
| foster | encourage, support, build |
| elevate | improve, raise, strengthen |
| unleash | release, enable, unlock |
| streamline | simplify, speed up |
| empower | enable, let, allow |
| bolster | support, strengthen, back up |
| resonate / resonates with | connect with, appeal to, matter to |
| revolutionize | change, transform, reshape |
| facilitate / facilitates | enable, help, allow, run |
| underpin | support, form the basis of |
| nuanced | specific, subtle, detailed |
| crucial | important, key, necessary |
| multifaceted | (describe the actual facets) |
| ecosystem (metaphor) | system, community, network |
| myriad | many, numerous (or give a number) |
| plethora | many, a lot of (or give a number) |
| encompass | include, cover, span |
| cultivate | build, develop, grow |
| illuminate | clarify, explain, show |
| elucidate | explain, clarify, spell out |
| cornerstone | foundation, basis, key part |
| paramount | most important, top priority |
| poised (to) | ready, set, about to |
| nascent | new, early-stage, emerging |
| overarching | main, central, broad |

**Tier 3, flag only at high density.**
Ordinary words. Flag when they saturate the text, a sign of AI filling
space with vague praise instead of specifics.

| Word | What to do |
|---|---|
| significant / significantly | Replace some with numbers, comparisons, examples |
| innovative / innovation | Describe what is actually new |
| effective / effectively | Say how, or cite a metric |
| scalable / scalability | Describe what scales and to what |
| compelling | Say why it compels |
| unprecedented | Name the precedent it breaks (or cut) |
| sophisticated | Describe the sophistication |
| world-class / state-of-the-art | Cite a benchmark or comparison |

A few multi-word boilerplate phrases belong here too.
Flag them at two or more uses, or when three or more distinct ones cluster:
"the integration of X with Y," "the intersection of X and Y,"
"community-driven," "user engagement," "designed for long-term X."
Name the specific thing instead.

**Hyphen note on "load-bearing":** unhyphenated "load bearing" is ordinary
English; only the hyphenated metaphor is the tell.
Before a literal structural noun (wall, beam, column, joist, truss),
"load-bearing" is standard terminology, so don't flag it.
Bruce's global watch list bans the metaphor outright, so cut it in his prose.

### 8. Avoidance of "is"/"are" (Copula Avoidance)

**Words to watch:** serves as/stands as/marks/represents [a],
boasts/features/offers [a]

**Problem:** LLMs substitute elaborate constructions for simple copulas.

**Before:**
> Gallery 825 serves as LAAA's exhibition space for contemporary art. The
> gallery features four separate spaces and boasts over 3,000 square feet.

**After:**
> Gallery 825 is LAAA's exhibition space for contemporary art. The gallery has
> four rooms totaling 3,000 square feet.

### 9. Negative Parallelisms and Tailing Negations

**Problem:** Constructions like "Not only...but..." or
"It's not just about..., it's..." are overused.
So are clipped tailing-negation fragments such as "no guessing"
or "no wasted motion" tacked onto the end of a sentence
instead of written as a real clause.

**Before:**
> It's not just about the beat riding under the vocals; it's part of the
> aggression and atmosphere. It's not merely a song, it's a statement.

**After:**
> The heavy beat adds to the aggressive tone.

**Before (tailing negation):**
> The options come from the selected item, no guessing.

**After:**
> The options come from the selected item without forcing the user to guess.

### 10. Rule of Three Overuse

**Problem:** LLMs force ideas into groups of three to appear comprehensive.

**Before:**
> The event features keynote sessions, panel discussions, and networking
> opportunities. Attendees can expect innovation, inspiration, and industry
> insights.

**After:**
> The event includes talks and panels. There's also time for informal
> networking between sessions.

### 11. Elegant Variation (Synonym Cycling)

**Problem:** AI has repetition-penalty code causing excessive synonym
substitution.

**Before:**
> The protagonist faces many challenges. The main character must overcome
> obstacles. The central figure eventually triumphs. The hero returns home.

**After:**
> The protagonist faces many challenges but eventually triumphs and returns
> home.

### 12. False Ranges

**Problem:** LLMs use "from X to Y" constructions where X and Y aren't on a
meaningful scale.

**Before:**
> Our journey through the universe has taken us from the singularity of the Big
> Bang to the grand cosmic web, from the birth and death of stars to the
> enigmatic dance of dark matter.

**After:**
> The book covers the Big Bang, star formation, and current theories about dark
> matter.

### 13. Passive Voice and Subjectless Fragments

**Problem:** LLMs often hide the actor or drop the subject entirely with lines
like "No configuration file needed" or
"The results are preserved automatically."
Rewrite these when active voice makes the sentence clearer and more direct.

**Before:**
> No configuration file needed. The results are preserved automatically.

**After:**
> You do not need a configuration file. The system preserves the results
> automatically.

Advisory, not absolute (see Local overrides).
Technical prose sometimes needs the passive to keep the right subject in focus.

### 14. Em Dashes: Leave Them Alone

**Rule (replaces the upstream rule, which cut every em dash):**
Bruce writes em dashes deliberately, as `---`.
Never remove one, never reword around one, never "correct" one.
Never introduce one either.
If you are writing new prose that needs a break,
use a period, comma, colon, semicolon, or parentheses.
If the source already has an em dash, it stays.

Do not treat an em dash as evidence of AI authorship.
The detection guidance below already says a lone em dash means nothing,
and here it means less than nothing: it is a signature.

The one place to act: if you find a spaced ` -- ` in Bruce's Markdown,
flag it rather than fixing it silently.
That form renders as an en dash, not an em dash,
which is usually not what he intended.

### 15. Overuse of Boldface

**Problem:** AI chatbots emphasize phrases in boldface mechanically.

**Before:**
> It blends **OKRs (Objectives and Key Results)**,
> **KPIs (Key Performance Indicators)**, and visual strategy tools such as the
> **Business Model Canvas (BMC)** and **Balanced Scorecard (BSC)**.

**After:**
> It blends OKRs, KPIs, and visual strategy tools like the Business Model
> Canvas and Balanced Scorecard.

### 16. Inline-Header Vertical Lists

**Problem:** AI outputs lists where items start with bolded headers followed by
colons.

**Before:**
> - **User Experience:** The user experience has been significantly improved
>   with a new interface.
> - **Performance:** Performance has been enhanced through optimized
>   algorithms.
> - **Security:** Security has been strengthened with end-to-end encryption.

**After:**
> The update improves the interface, speeds up load times through optimized
> algorithms, and adds end-to-end encryption.

### 17. Title Case in Headings

**Problem:** AI chatbots capitalize all main words in headings.

**Before:**
> ## Strategic Negotiations And Global Partnerships

**After:**
> ## Strategic negotiations and global partnerships

**Does not apply to `Chapters/*.md`** (see Local overrides).
Book headings are title-case by convention,
and their anchors are gated by `heading_links.py`,
so editing one breaks cross-references.

### 18. Emojis

**Problem:** AI chatbots often decorate headings or bullet points with emojis.

**Before:**
> 🚀 **Launch Phase:** The product launches in Q3
> 💡 **Key Insight:** Users prefer simplicity
> ✅ **Next Steps:** Schedule follow-up meeting

**After:**
> The product launches in Q3. User research showed a preference for simplicity.
> Next step: schedule a follow-up meeting.

### 19. Curly Quotation Marks

**Problem:** ChatGPT uses curly quotes (“…”, ‘…’) instead of straight quotes
("...", '...'). Replace them with straight quotes.

**Before:**
> He said “the project is on track” but others disagreed.

**After:**
> He said "the project is on track" but others disagreed.

## COMMUNICATION PATTERNS

### 20. Collaborative Communication Artifacts

**Words to watch:** I hope this helps, Of course!, Certainly!,
You're absolutely right!, Would you like..., Want me to...?,
Want me to give examples?, Should I continue?, let me know, here is a...

**Problem:** Text meant as chatbot correspondence gets pasted as content.

**Before:**
> Here is an overview of the French Revolution. I hope this helps! Let me know
> if you'd like me to expand on any section.

**After:**
> The French Revolution began in 1789 when financial crisis and food shortages
> led to widespread unrest.

### 21. Knowledge-Cutoff Disclaimers and Speculative Gap-Filling

**Words to watch:** as of [date], Up to my last training update,
While specific details are limited/scarce..., based on available information,
not publicly available, maintains a low profile, keeps personal details
private, prefers to stay out of the spotlight, likely [grew up/studied/began],
it is believed that

**Problem:** Two related tells.
(a) Older models leave hard knowledge-cutoff disclaimers in the text.
(b) When a model can't find a source, it writes a paragraph *about* not finding
one and then invents plausible filler to cover the gap.
For a private person the guess almost always lands on the same stock phrases
("maintains a low profile," "keeps personal details private"), none of it
sourced. Say what isn't known, or cut the sentence;
don't dress a guess up as fact.

**Before (cutoff disclaimer):**
> While specific details about the company's founding are not extensively
> documented in readily available sources, it appears to have been established
> sometime in the 1990s.

**After:**
> The company's founding date is not documented in the available sources.

Or cut the sentence. State a date only if a source provides one.

**Before (speculative gap-fill):**
> Information about her early life is not publicly available, suggesting she
> maintains a low profile and keeps personal details private. She likely grew
> up in a middle-class household, which shaped her later interest in education
> reform.

**After:**
> Her early life is not documented in the available sources.

Or omit the section.

### 22. Sycophantic/Servile Tone

**Problem:** Overly positive, people-pleasing language.

**Before:**
> Great question! You're absolutely right that this is a complex topic. That's
> an excellent point about the economic factors.

**After:**
> The economic factors you mentioned are relevant here.

## FILLER AND HEDGING

### 23. Filler Phrases

- "In order to achieve this goal" becomes "To achieve this"
- "Due to the fact that it was raining" becomes "Because it was raining"
- "At this point in time" becomes "Now"
- "In the event that you need help" becomes "If you need help"
- "The system has the ability to process" becomes "The system can process"
- "It is important to note that the data shows" becomes "The data shows"

**Often-empty adverbs.** Cut these when they add nothing:
*just, literally, simply, actually, truly, fundamentally, importantly,
crucially, inherently, inevitably.*
Keep one when it carries real emphasis, contrast, or the writer's spoken rhythm.
The test is deletion: if the sentence means the same without it, it was filler.

**Make verbs do the work.** Replace a weak verb phrase with a direct verb.
"Made a decision" becomes "decided"; "has the ability to" becomes "can";
"came to the realization" becomes "realized."

### 24. Excessive Hedging

**Problem:** Over-qualifying statements.

**Before:**
> It could potentially possibly be argued that the policy might have some
> effect on outcomes.

**After:**
> The policy may affect outcomes.

### 25. Generic Positive Conclusions

**Problem:** Vague upbeat endings.

**Before:**
> The future looks bright for the company. Exciting times lie ahead as they
> continue their journey toward excellence. This represents a major step in the
> right direction.

**After:**
> Cut the paragraph. End on the last concrete fact instead of a send-off.
> If the source states real plans, use those.

### 26. Hyphenated Word Pair Overuse

**Words to watch:** third-party, cross-functional, client-facing, data-driven,
decision-making, well-known, high-quality, real-time, long-term, end-to-end

**Problem:** AI hyphenates these uniformly, including in predicate position
(`the report is high-quality`).
Humans hyphenate inconsistently, typically only when the compound is
attributive (`a high-quality report`), and often drop the hyphen otherwise
(`the report is high quality`).
Keep attributive-position hyphens; drop them when the compound follows the
noun.

**Before:**
> The cross-functional team delivered a high-quality, data-driven report. The
> team is cross-functional, the report is high-quality, and the methodology is
> data-driven.

**After:**
> The cross-functional team delivered a high-quality, data-driven report. The
> team is cross functional, the report is high quality, and the methodology is
> data driven.

### 27. Persuasive Authority Tropes

**Phrases to watch:** The real question is, at its core, in reality,
what really matters, fundamentally, the deeper issue, the heart of the matter

**Problem:** LLMs use these phrases to pretend they are cutting through noise
to some deeper truth, when the sentence that follows usually just restates an
ordinary point with extra ceremony.

**Before:**
> The real question is whether teams can adapt. At its core, what really
> matters is organizational readiness.

**After:**
> The question is whether teams can adapt. That mostly depends on whether the
> organization is ready to change its habits.

### 28. Signposting and Announcements

**Phrases to watch:** Let's dive in, let's explore, let's break this down,
here's what you need to know, now let's look at, without further ado

**Problem:** LLMs announce what they are about to do instead of doing it.
This meta-commentary slows the writing down and gives it a tutorial-script
feel.

**Before:**
> Let's dive into how caching works in Next.js. Here's what you need to know.

**After:**
> Next.js caches data at multiple layers, including request memoization, the
> data cache, and the router cache.

### 29. Fragmented Headers

**Signs to watch:** A heading followed by a one-line paragraph that simply
restates the heading before the real content begins.

**Problem:** LLMs often add a generic sentence after a heading as a rhetorical
warm-up. It usually adds nothing and makes the prose feel padded.

**Before:**
> ## Performance
>
> Speed matters.
>
> When users hit a slow page, they leave.

**After:**
> ## Performance
>
> When users hit a slow page, they leave.

### 30. Diff-Anchored Writing

**Problem:** Documentation or comments written as if narrating a change rather
than describing the thing as it is.
Unless the document is inherently version-scoped
(changelogs, release notes, migration guides),
it should read coherently without knowing what changed in the last commit.

**Before:**
> This function was added to replace the previous approach of iterating through
> all items, which caused O(n²) performance.

**After:**
> This function uses a hash map for O(1) lookups, avoiding the O(n²) cost of
> naive iteration.

### 31. Manufactured Punchlines and Staccato Drama

**Problem:** LLMs often make every sentence land like a quotable closer, then
stack short declarative fragments to manufacture drama.
A single short sentence for emphasis is fine;
a run of them starts to sound engineered.

**Before:**
> Then AlphaEvolve arrived. It had no preference for symmetry. No aesthetic
> prior. No nostalgia for human taste. The old rules were gone.

**After:**
> AlphaEvolve changed the search because it did not favor symmetry or
> human-looking designs. That made some of the older assumptions less useful.

### 32. Aphorism Formulas

**Words to watch:** X is the Y of Z, X becomes a trap,
X is not a tool but a mirror, the language of, the currency of,
the architecture of

**Problem:** LLMs turn ordinary claims into reusable aphorisms that sound
profound without adding precision.
Replace the formula with the concrete claim it is gesturing at.

**Before:**
> Symmetry is the language of trust. Efficiency becomes a trap when teams
> forget the human layer.

**After:**
> Symmetric layouts often feel more predictable to users. Teams can
> over-optimize workflows and miss how people actually use them.

**Fake-profound kicker endings:** the same formula placed as the final line,
a metaphor or aphorism engineered as a mic-drop.
Delete it; do not rewrite it into a better metaphor and do not keep the rhythm.
End on the clearest concrete sentence already in the draft
(see §25 on generic conclusions, §49 on future-narrative closers).

### 33. Conversational Rhetorical Openers

**Phrases to watch:** Honestly?, Look, Here's the thing, The thing is,
Let's be honest, Let me be clear, The uncomfortable truth is, Real talk,
when used as standalone hooks or fake-candid pauses before an ordinary point.

**Problem:** LLMs open with a fake-candid hook to manufacture intimacy before
delivering a routine claim.
The tell is the theatrical pause-and-reveal:
a one-word question or aside, then the "real" answer.
A person being honest usually just says the thing.

**Before:**
> Is it worth the price? Honestly? It depends on how often you'll use it.

**After:**
> Whether it's worth the price depends on how often you'll use it.

## MORE CONTENT PATTERNS

### 34. Real/Actual Adjective Inflation

**Words to watch:** real, actual, genuine, true, used as intensifiers on
abstract nouns (real utility, genuine insight, true understanding).

**Problem:** Calling a thing "real" or "genuine" implies the rest of the field
is fake, without naming what makes this instance different.
The adjective does no work.

**Before:**
> This gives you real type safety and genuine performance gains.

**After:**
> This catches type errors at compile time and cuts the hot loop from 40ms to
> 6ms.

**Carve-out, named contrast:** "real type checking, not runtime asserts" is
honest contrastive writing. The tell is the bare intensifier with no contrast
named.

### 35. Moral-Adjective Category Errors

**Words to watch:** honest, genuine, faithful, truthful, applied to
non-agentic technical nouns (an honest shape, a faithful number, a truthful
curve).

**Problem:** AI glues a moral adjective onto a noun that cannot hold one.
A shape is not a moral agent, so "an honest shape" is a category error.
State the concrete property instead.

**Before:**
> The chart gives an honest picture of the data.

**After:**
> The chart plots every outlier instead of clipping the axis.

Related: "the assumption stops being true." Assumptions do not flip
truth-values; they stop holding. Write "the assumption breaks down" or
"no longer holds." Also cut gratuitous universal quantifiers:
"taught in every first-year course" becomes "taught in introductory courses."

### 36. Narrated Candor

**Phrases to watch:** I want to be upfront, To be fully transparent,
Rather than bury this, Being honest about the limitations here,
caveats I would rather flag than let you discover later.

**Problem:** The model advertises its own forthrightness instead of just
disclosing. The content is "two caveats"; the rest performs the disclosure.

**Deletion test:** cut the frame. If the sentence loses no information, it was
never content.

**Before:**
> Two caveats I would rather flag now than let you discover later: the
> benchmark ran on one machine, and the sample size was small.

**After:**
> Two caveats: the benchmark ran on one machine, and the sample was small.

**Carve-out:** the disclosure itself stays. "I haven't tested this on Windows"
carries information. A conflict-of-interest label ("I own shares in the company
discussed") is conventional, not narrated candor. The tell is the separable
clause *about* disclosing.

### 37. Emotional Flatline

**Phrases to watch:** What surprised me most, I was fascinated to discover,
What struck me was, The most interesting part, and bare headers like
"Interesting aspect:".

**Problem:** The writer claims an emotion instead of making the reader feel it.
If the thing is surprising, the content should show it.
These also pile up as list introductions, filler wearing an emotion costume.

**Before:**
> What surprised me most was how fast the cache warmed up.

**After:**
> The cache warmed up in three requests, not the fifty I expected.

Also a sign of lazy human writing on autopilot. Flag it either way.

### 38. Lingering-Attention Claims

**Phrases to watch:** the line I keep coming back to, I can't stop thinking
about this, still thinking about this one, been rattling around in my head.

**Problem:** The claim is about the writer's attention, not the thing, and it
arrives before the reader has any reason to care. It is unfalsifiable.

**Before:**
> The idea I keep coming back to: interfaces should be small.

**After:**
> Small interfaces compose better, because each caller depends on less.

**Carve-out, reason attached:** "I keep coming back to exit-voice framing
because it predicts which engineers quit" is a claim about explanatory reach.
The tell is the bare frame with the reason missing.

### 39. Self-Labeling Significance

**Phrases to watch:** That last one is the contrarian one, This is the
interesting part, Here's where it gets clever, That third point is the real
story.

**Problem:** The label does the work the content was supposed to do.
If a move is genuinely surprising, the reader sees it;
if not, the label is unearned.

**Before:**
> Of the three, that last approach is the clever one.

**After:**
> The third approach reuses the parser's own error table, so a new token type
> needs no extra code.

### 40. Recap-Flattery Opener

**Problem:** Replying to someone by summarizing their own work back at them
with praise before getting to the point. They already know what they did;
the recap performs appreciation instead of conveying information.

**Before:**
> Thanks for all the legwork here, the migration script and the rollback plan
> you worked through are what made this possible. One thing I noticed:

**After:**
> Thanks for the legwork, this looks right. One thing I noticed:

Distinct from a genuine thank-you (short, then moves on) and from acknowledgment
loops (§41, which restate the prompt).

### 41. Acknowledgment Loops

**Phrases to watch:** You're asking about, To answer your question,
The question of whether, That's a great question. The...

**Problem:** The model restates the prompt before answering.
In writing this is pure filler; the reader knows what they asked.
Same move: opening a section by summarizing the previous one when the structure
is already clear.

**Before:**
> To answer your question about retries: retries help with transient failures.

**After:**
> Retries help with transient failures.

### 42. Confidence Calibration Phrases

**Phrases to watch:** Notably, Interestingly, Surprisingly, Importantly,
Significantly, Certainly, Undoubtedly, Without a doubt, Here's what's
interesting.

**Problem:** The word signals how the reader should feel instead of letting the
fact do it. One "notably" in 2,000 words is fine; three in 500 is AI-style
stacking. Flag by density.

**Before:**
> Interestingly, the parser is faster on malformed input than on valid input.

**After:**
> The parser is faster on malformed input than on valid input, because it bails
> at the first bad token.

Related to persuasive-authority tropes (§27), which assert depth rather than
feeling. This front-loads a feeling cue.

### 43. Rhetorical Question Openers

**Phrases to watch:** But what does this mean for you?, So why should you care?,
What's next?, What if I told you...?, Think about it:, used as section
transitions, along with self-answered "Question? Answer." pairs.

**Problem:** AI drops a rhetorical question to stall before the point.
If you know the answer, say it. A rhetorical question is earned by strong setup,
not used as a transition.

**Before:**
> So why does this matter? It matters because latency compounds.

**After:**
> Latency compounds: a 10ms delay per call becomes 1s across a hundred calls.

### 44. Parenthetical Hedging

**Phrases to watch:** (and, increasingly, X), (or, more precisely, Y),
(and perhaps more importantly, Z).

**Problem:** AI inserts a parenthetical aside to sound nuanced without
committing. If the aside matters, give it a sentence. If not, cut it.

**Before:**
> The approach scales well (and, increasingly, to other domains).

**After:**
> The approach scales well. It also transfers to image and audio pipelines.

### 45. Speculative Scenario Openers

**Phrases to watch:** Imagine a world where, Picture a future in which,
Envision a world where.

**Problem:** AI opens with a hypothetical that lists desirable outcomes instead
of making a claim. The scenario does the persuading; no evidence is offered.

**Before:**
> Imagine a world where every deploy is instant.

**After:**
> Instant deploys would cut our release cycle from a day to minutes.

**Carve-out:** fiction, thought experiments with a stated payoff, and
instructional framing ("imagine you have a sorted array") are fine. Flag only
the world/future opener that stands in for an argument.

### 46. False Concession Structure

**Problem:** "While X is impressive, Y remains a challenge" sounds balanced
without weighing anything, because both halves are vague.
Make the concession specific, or pick a side and argue it.

**Before:**
> While the framework is powerful, some challenges remain.

**After:**
> The framework handles routing well, but its error messages point at generated
> code the user never wrote.

### 47. Invented Contrast-Pair Mirroring

**Problem:** One half of a contrast is a real term of art; the other is AI
inventing a mirror to balance the sentence.
"False precision rather than genuine accuracy": "false precision" is a real
statistical term, "genuine accuracy" is phantom.

**Fix:** if you need a contrast, use an actual opposite.
If none exists, drop the contrast and state the positive claim.

**Before:**
> This measures false precision, not genuine accuracy.

**After:**
> This measures precision but says nothing about accuracy.

### 48. Hedge-Stacked Predictions

**Phrases to watch:** could potentially, may eventually unlock, might ultimately
transform.

**Problem:** A modal stacked with a hedge adverb. Each word cancels the next,
so nothing is asserted while the sentence sounds cautious.
Sharper than plain over-hedging (§24): here two hedges collide.

**Before:**
> This could potentially unlock new use cases.

**After:**
> This enables batch inference, which the streaming API could not do.

Pick one hedge, not both: "could unlock" or "potentially unlocks."

### 49. Generic Future-Narrative Closers

**Phrases to watch:** may become one of the most important trends, could become
the defining story of the decade, is poised to become the next chapter in X.

**Problem:** Modal plus "become" plus superlative plus a narrative noun equals a
testable-sounding but empty prediction. A sharper cousin of the generic
conclusion (§25).

**Fix:** pick the falsifiable version, or cut. "May exceed the current baseline
by 2027" is a prediction; "may become an important story" is not.

### 50. Novelty Inflation

**Phrases to watch:** He coined the phrase, She introduced a term, a concept
nobody's naming, a failure mode nobody talks about.

**Problem:** AI treats an established idea as if the speaker invented it.
Most ideas in a conversation apply existing concepts rather than inventing them.
Claiming novelty for something with a Wikipedia page reads as uninformed.

**Fix:** describe what the person *did with* the concept, not that they
discovered it.

**Before:**
> She introduced a term I hadn't heard: back-pressure.

**After:**
> She showed how back-pressure applies to our queue: slow consumers stall
> producers instead of dropping messages.

Also flag invented labels: pseudo-analytical compounds coined mid-sentence and
never defined ("the supervision paradox"). Naming is not explaining.

### 51. Vague Third-Party Validation

**Phrases to watch:** independent testing confirms, third-party benchmarks show
we lead, an outside party put us on top.

**Problem:** Credibility from an *unnamed* authority plus a generic superlative.
The reader cannot verify it.
Distinct from vague attributions (§5), which hide the source of an *opinion*;
this manufactures external *proof*.

**Fix:** name the source, test, and result.

**Before:**
> Independent benchmarks confirm we're the fastest.

**After:**
> On the HELM leaderboard (April 2026 run) we ranked first on reasoning latency.

**Carve-out:** a named benchmark, linked report, or dated audit is legitimate.
The tell is the vagueness, not the act of citing outside proof.

### 52. Infomercial Engagement Hooks

**Phrases to watch:** The catch?, The kicker?, The best part?, Plot twist:,
But here's the kicker:, The result?

**Problem:** A punchy fragment tees up a reveal to fake momentum around ordinary
information. Delete the hook and state the thing.
Distinct from the fake-candid opener (§33): this stages a reveal, that stages
intimacy.

**Before:**
> The catch? It only works on POSIX systems.

**After:**
> It only works on POSIX systems.

### 53. Social Endorsement Closers

**Phrases to watch:** worth knowing, worth your time, a must-read, do yourself
a favor and read this, bookmark this, don't sleep on this one.

**Problem:** A recommendation with no reason to act. The endorsement is generic
and could sit under any link.

**Fix:** say what the thing is and who it is for, then drop the call to action.

**Before:**
> Great write-up on caching. Worth your time.

**After:**
> A clear walkthrough of cache invalidation, useful if you are debugging stale
> reads in a CDN.

"Worth knowing" is the same move aimed at a fact rather than a link, and it is
the one to watch for in explanatory writing: it rates the information instead
of using it. The whole family goes with it, since the endorsement is in the
frame rather than the adjective: worth learning, worth remembering, worth
understanding, worth the trouble, and the passive "X is worth a mention."
Cut the frame and state the fact, or say what it lets the reader do.

**Before:**
> The distinction between `is` and `==` is worth knowing.

**After:**
> `is` compares identity and `==` compares value, so two equal lists can fail
> an `is` test.

Two constructions survive. "Worth" carrying a real comparison stays: "worth the
extra allocation," "worth it only past a thousand rows," where something is
being weighed against a stated cost. So does an instruction to the reader:
"this one is worth running yourself" tells them to do something.

### 54. Numbered List Inflation

**Phrases to watch:** Three key takeaways, Five things to know, the top seven.

**Problem:** AI defaults to numbered lists because they feel safe.
Use a number only when the content has that many discrete, parallel items.
Padding to hit a number means the list should not exist.

### 55. Reasoning Chain Artifacts

**Phrases to watch:** Let me think step by step, Breaking this down,
To approach this systematically, Here's my thought process, First, let's
consider.

**Problem:** Chain-of-thought scaffolding leaking into finished prose.
The reader does not need the internal monologue. State the conclusion, then the
evidence.

### 56. Wall-of-Text Replies

**Problem:** In conversational registers (issue and PR comments, chat, casual
email) a person breaks a reply at thought boundaries.
LLMs default to one dense block. The tell: a short reply (under ~150 words)
with four or more sentences delivered as a single unbroken paragraph.

**Fix:** break at thought boundaries, one idea per group.

**Carve-out:** a single dense paragraph is correct in formal long-form prose
(a blog intro, a docs paragraph). This fires only in conversational replies.

### 57. Excessive Structure

**Signs to watch:** more than three headings in under 300 words; eight or more
bullets in under 200 words; formulaic section headers (Overview, Key Points,
Summary, Introduction, Conclusion).

**Problem:** AI over-structures short text to look organized.
Merge sections, convert padded lists to prose, and give headers that say
something specific about what follows.
Fragmented headers are covered in §29.

### 58. List-Label Periods

**Problem:** In a bulleted list, LLMs end a bold label with a period and run the
gloss as a separate sentence. A person uses a colon.

**Before:**
> - **Intros.** Years of conferences and an operator network.

**After:**
> - **Intros:** years of conferences and an operator network.

**Carve-out:** when the label is a full sentence rather than a label introducing
a gloss, the period is correct.

### 59. Bullet Lists of Bare Noun Phrases

**Problem:** Five or more consecutive bullets, each a short adjective-plus-noun
phrase with no verb, none checkable.
The tell is the symmetry: every item the same grammatical shape and length.

**Before:**
> - Stable connection handling
> - Optimized query performance
> - Reliable failover behavior
> - Consistent memory use

**After:**
> Connections survive a broker restart, queries under 1KB return in under a
> millisecond, and memory stays flat across a 12-hour run.

**Carve-out:** genuine list content (changelog entries, parameter docs,
ingredient lists) where bare noun phrases are correct.

### 60. Excessive Bullet Lists

**Problem:** AI converts prose that should flow into bullet-heavy sections.
Use bullets for genuine list content: comparisons, step-by-step instructions,
API parameters. Otherwise write prose.

### 61. Template and Slot-Fill Phrases

**Problem:** Constructions that generate the same sentence when the noun
changes:

- "a [adjective] step toward [adjective] X" becomes: describe the specific
  capability or outcome.
- "Whether you're X or Y" is false breadth; pick the actual audience or cut.
- "I recently had the pleasure of [verb]-ing" becomes: say what happened
  ("I talked to," "I read," "I attended").

### 62. Transition-Phrase Openers

**Phrases to watch:** Moreover, Furthermore, Additionally, In today's X,
In an era where, When it comes to, At the end of the day, That said.

**Problem:** These stall or pad instead of connecting.
Restructure so the connection is obvious, or use plain connectors (and, also,
but). "When it comes to X" becomes writing about X directly.
"At the end of the day" is cut. One "however" is fine; a pile is the tell.
(See the false-positive note on transition words in isolation.)

### 63. Unfilled Placeholders

**Signs to watch:** `[Your Name]`, `[INSERT SOURCE URL]`,
`[Describe the section]`, `2025-XX-XX`, `<!-- Add citation -->`.

**Problem:** Bracketed slot-fillers meant to be replaced before publishing,
strong evidence that boilerplate was pasted without editing.
Fill it or delete the sentence.

**Note for this repo:** Bruce's own `[[ ]]` double-bracket draft notes are
deliberate placeholders (see project memory). Leave those for him; flag
single-bracket AI slot-fillers.

### 64. Chatbot Citation Markup Leaks

**Signs to watch:** `citeturn0search0`, `contentReference[oaicite:0]`,
`oai_citation`, `[attached_file:1]`, `grok_card`.

**Problem:** Internal citation tokens that leak through when text is pasted from
a chat UI. These are fingerprints, not style. Strip every one.
If a citation was meaningful, replace it with a real reference.

### 65. AI-Tool URL Parameters

**Signs to watch:** `utm_source=chatgpt.com`, `utm_source=claude.ai`,
`utm_source=perplexity.ai`, `referrer=grok.com`.

**Problem:** Tracking parameters auto-appended by AI tools that survive
copy-paste. Strip the AI-referrer parameter; keep functional ones
(`?page=2`, `?v=4`).

### 66. Hashtag Stuffing

**Problem:** A long trailing block of hashtags (six or more on a short post) is
near-universal in AI social content and rare in thoughtful human posts.
Use two or three specific tags, or none.
Issue references (`#88`), hex colors (`#1a2b3c`), preprocessor directives
(`#include`), and channel names do not count.

### 67. Immaculate Typography in Casual Registers

**Problem:** Perfect spacing and punctuation in a fast-typed context (a code
comment, a chat message, a DM) is a weak, register-scoped signal.
Corroborating, never conclusive. Judge it alongside other tells, never alone.

### 68. Faux-Insight Setups

**Phrases to watch:** What most people get wrong, Here's what nobody tells you,
This is the part everyone skips, The part everyone misses, What they don't want
you to know.

**Problem:** The setup flatters the writer as the lone expert who sees what
others cannot. Cut it and let the claim stand on its own.
Distinct from self-labeling significance (§39), which back-points at an item
already stated; this front-loads a "you're about to learn a secret" frame.

**Before:**
> The part everyone misses: distribution is the real moat.

**After:**
> Distribution is the moat.

### 69. Colon Reveals

**Problem:** A noun phrase, a colon, then a dramatic lowercase reveal, staged
for suspense: "The detail that makes it work: a separate pass grades the
output." Rewrite as a plain sentence.
Use a colon for a list, a label, or a quote, not for fake drama.
Prefer sentence case after a colon unless grammar, a proper noun, a title, or
code requires otherwise.

**Before:**
> The best part: it caches the result.

**After:**
> It caches the result, so the second call is free.

### 70. Interpretive Metadiscourse

**Phrases to watch:** As you can see, In other words (when the first phrasing
was already clear), The key point is, This distinction matters, That last part
matters more than it sounds.

**Problem:** The sentence steps outside the subject to tell the reader what to
notice or how much weight to give it. If the point is clear, the aside is
redundant; delete it. If it is not clear, replace the aside with the support or
fact that would make it clear. Related to confidence-calibration cues (§42) and
self-labeling (§39); this one is the redundant gloss and the "here is how to
read what I just wrote" aside.

**Before:**
> The cache holds 10,000 entries. In other words, it stores a lot of data.

**After:**
> The cache holds 10,000 entries.

## DETECTION GUIDANCE

### What NOT to flag (false positives)

A clean human writer can hit several of the patterns above without any AI
involvement. Before rewriting, sanity-check that you are not gutting
legitimate prose. The following are *not* reliable indicators on their own:

- **Perfect grammar and consistent style.**
  Many writers are professionals or have been edited.
  Polish does not equal AI.
- **Mixed casual and formal registers.**
  This often signals a person in a technical field, a young writer,
  or someone with neurodivergent prose habits, not a chatbot.
- **"Bland" or "robotic" prose.**
  AI prose has *specific* tells.
  Generic dryness without those tells is just dry writing.
- **Formal or academic vocabulary.**
  AI overuses *specific* fancy words (see §7), not all fancy words.
  Don't flatten "ostensibly" or "constituent" just because they sound brainy.
- **Letter-style opening or closing on a comment.**
  Salutations and sign-offs predate ChatGPT by centuries.
- **Common transition words in isolation.**
  *Additionally*, *moreover*, *consequently* are AI-coded only when piled up.
  One *however* is not a tell.
- **Curly quotes alone.**
  macOS, Word, Google Docs, and most CMSes auto-curl by default.
  Curly quotes only count when stacked with other tells.
- **Em dashes.**
  Not evidence at all in Bruce's prose, where they are deliberate (see §14).
  Even elsewhere, many editors and journalists use them often.
- **One short emphatic sentence.**
  Humans use clipped sentences to land a point.
  Flag staccato drama only when several short fragments appear in a row and
  inflate the tone.
- **"Honestly" or "look" mid-sentence.**
  These are ordinary in casual writing.
  The tell is the standalone theatrical opener, not the word itself.
- **Unsourced claims.**
  Most of the web is unsourced. Lack of citations doesn't prove anything.
- **Correct, complex formatting.**
  Visual editors and templates produce clean output without any AI.
- **Secondhand text.**
  Do not rewrite watched phrases inside quotations, titles, proper names, or
  examples where the phrase is being discussed rather than used.

When in doubt, look for **clusters** of tells, not isolated ones.
A single watched word means nothing;
rule-of-three plus *vibrant tapestry* plus a "Conclusion" section is a
confession.

### Signs of human writing (preserve these)

When you see these, lean toward leaving the prose alone.
They are evidence of a real person writing,
and over-editing will destroy what makes the piece sound human:

- **Specific, unusual, hard-to-fabricate detail.**
  A real address. A weird quote.
  The phrase "the lawyer who used to work upstairs from my dentist."
  LLMs round off specifics; humans hoard them.
- **Mixed feelings and unresolved tension.**
  "I think this is mostly good, but it bothers me, and I can't fully explain
  why." LLMs default to clean takes.
- **Dated, era-bound references.**
  Slang, memes, or in-jokes that map to a specific year and subculture.
  Models lag by a year or more.
- **First-person editorial choices the writer can defend.**
  If the writer can explain *why* they made a particular cut or used a
  particular word, that's a strong human signal.
- **Variety in sentence length.**
  Real writing alternates short and long.
  AI writing tends toward an even, mid-length cadence.
- **Genuine asides, parentheticals, or self-corrections.**
  "(I keep wanting to say 'almost' here, but it really was certain.)"
  Models rarely interrupt themselves like this.
- **Edits made before November 30, 2022.**
  ChatGPT's public launch.
  Anything older than that is, with very rare exceptions, not AI-written.

## STRUCTURE AND RHYTHM TESTS

Individual word and phrase fixes are only half the work.
The stronger signal is *how the text flows*.
AI prose is metronomic; human prose has varied rhythm.
Consistent sentence construction and symmetrical phrasing are harder to mask
than a flagged word, so treat these as the deeper check.

**Sentence-length uniformity.**
If most sentences run 15 to 25 words, the text sounds robotic.
Mix short (3 to 8 words) with long (20+). Fragments work. A question breaks
monotony. This is the single strongest structural tell.

**Paragraph-length uniformity.**
If every paragraph is three to five sentences and roughly the same size, vary it
deliberately. Some paragraphs should be one sentence, some longer.

**Read-aloud test.**
If the text could be read by text-to-speech without sounding odd, it is probably
too uniform. Human writing has a rhythm that resists flat delivery.

**Vocabulary diversity (type-token ratio).**
In a longer piece (200+ words), look at distinct word types over total words.
Human prose usually lands around 0.50 to 0.65; AI text trends flatter,
sometimes under 0.40 when the model locks onto a small vocabulary loop.
A low ratio is not proof: narrow topics, technical reference, and
second-language writing all compress vocabulary legitimately.
The fix is rarely to thesaurus the text. Broaden the *what*: name specific
things, cite specific cases, replace a reused abstract noun with the concrete
instance behind it.

**Paragraph-reshuffle immunity.**
Can you swap two body paragraphs without breaking the piece?
If the order does not matter, you have a list of points, not an argument that
builds. AI prose often fails this: each paragraph is a self-contained module
with no load-bearing link to its neighbors.
Establish a through-line where each paragraph depends on the one before, or
decide the piece should be an explicit list.

**Treadmill effect (low information density).**
Read each paragraph and ask what is actually new here.
AI prose restates the premise in fresh words instead of advancing it: motion
without distance. The tell: you could cut 40 to 60 percent and lose no
information. For each paragraph, name the one fact, claim, or turn it adds.
If there is none, cut it. If there is, lead with it.

**Portability test.**
If a sentence could move unchanged to another person, company, product, or
country, it is probably filler. Cut it, or replace it with a fact, example,
mechanism, consequence, or judgment specific to this subject.
"The integration improved efficiency" ports anywhere;
"the integration cut deploy time from 40 minutes to 4" does not.

**When to rewrite from scratch instead of patching.**
If the text has five or more flagged vocabulary hits across categories, three or
more distinct pattern categories triggered, and uniform sentence and paragraph
length, patching individual phrases will not fix it: the structure is the
problem. State the core point in one sentence and rebuild from there.

## SEVERITY TIERS

When triaging a large document or doing a quick pass, prioritize:

**P0, credibility killers (fix first).**
Cutoff disclaimers (§21), chatbot artifacts (§20), vague attributions with no
source (§5), significance inflation on routine events (§1), citation-markup
leaks (§64), unfilled placeholders (§63).

**P1, obvious AI smell (fix before publishing).**
Tier 1A vocabulary (§7), template and slot-fill phrases (§61), "let's" openers
(§28), synonym cycling (§11), formulaic openings, boldface overuse (§15),
future-narrative closers (§49), social endorsement closers (§53), narrated
candor (§36), lingering-attention claims (§38), hedge-stacked predictions (§48),
real/actual inflation (§34), moral-adjective category errors (§35), invented
contrast-pair mirroring (§47), bare-noun-phrase bullet lists (§59).

**P2, stylistic polish (fix when time allows).**
Generic conclusions (§25), rule-of-three overuse (§10), uniform paragraph
length, copula avoidance (§8), transition-phrase openers (§62).

A quick pass covers P0 and P1. A full audit covers all three.

## NEVER INJECT THESE

Removal is half the job. A rewrite that clears every flag but reads sterile,
with even sentence lengths and no stance where one belongs, is still recognizably
machine output. But the cure is never to invent. Each of the following is a
rewrite failure even when the result scores clean:

- **Fake first person.**
  "I've seen this a hundred times" dropped into prose that had no author
  presence. If the source has no "I," the rewrite has no "I."
- **Manufactured stakes.**
  "Now more than ever," "the stakes have never been higher." Legitimate only
  when the source actually argued it.
- **Forced contrarianism.**
  "Everyone says X, but they're wrong." Only when the source argued it.
- **Performed candor.**
  "Let's be honest," "real talk," "here's the thing." Adding one fails two rules
  at once (see §33, §36).
- **Em-dash theatrics.**
  Never add an em dash for drama. (In Bruce's prose, never add or remove one at
  all; see §14.)
- **Staccato conversion.**
  Chopping ordinary sentences into fragments to fake rhythm. Vary sentences by
  varying sentences, not by breaking them (see §31).
- **Invented specifics.**
  A number, name, date, tool, or mechanism the source never contained.
  A fabricated specific is worse than vague phrasing. If the detail is missing,
  flag the gap and leave it.

The test: for each edit, ask whether the information came from the source.
Subtraction and sharpening are in scope. Addition of stance, personality, or
fact is not.

## Register Affects Strictness

The upstream skill carries a full profile matrix (LinkedIn, investor email, and
so on). That machinery is dropped here, but the underlying idea is worth keeping:
how hard to enforce a rule depends on register.

- **Long-form prose (essays, blog posts, chapters).** Full strength.
- **Technical writing (docs, READMEs, API reference).** Clarity over voice.
  Terms of art get a pass; the passive is often correct (see §13). Do not inject
  first person or opinion.
- **Casual replies (chat, issue comments, DMs).** Catch only the worst
  offenders: chatbot artifacts, sycophancy, wall-of-text blocks. Leave the rest.

Register sets how strict; voice sets how the prose should sound.
They are separate axes, and a writing sample (see Voice Calibration) outranks
both.

## Self-Reference Escape Hatch

When the text is *about* AI-writing patterns (this skill, a blog post on the
subject, a tutorial), quoted examples are exempt.
Text inside quotation marks, code blocks, or marked as illustrative is not
rewritten. Flag patterns in the author's own prose, not in cited examples.

## Invocation Modes

**Pasted text (default).**
The user gives text in the conversation.
Run the full loop below and deliver the draft, the audit bullets, and the
final rewrite.

**File mode.**
The user points at a file.
Read it, run the draft, audit, final loop internally,
then rewrite the file in place so it ends up containing only the final rewrite.
Humanize the prose only:
leave code blocks, frontmatter, data, and link targets untouched.
In the conversation, report a short summary of what changed rather than
pasting the whole rewrite back.

In this repo, file mode has extra constraints.
Never touch a fenced ```python block:
those are extracted to `Examples/` and gated.
Keep Semantic Line Breaks in `Chapters/*.md`
(one sentence per line), or `make reflow` will churn the diff.
After rewriting a chapter, remind Bruce to run `make verify`.

**Embedded mode.**
Another task or agent is using this skill as one step of a larger job
(a PR description, a commit message, a doc).
Run the loop internally and output only the final text.
No draft, no audit bullets, no summary.

**Detect-only.**
Bruce asks whether a piece reads as AI, or asks to audit, scan, or flag it
without a rewrite. Name each pattern that appears, quote the offending line, and
give the fix in a few words. Do not rewrite, do not score the draft, and do not
guess whether AI wrote it: a named, quoted pattern is evidence Bruce can check,
which a detector's verdict is not. Offer to run the full rewrite afterward.
When the target is a book chapter, prefer the Review-File Workflow below, which
persists the findings to disk for Bruce to vet.

## Review-File Workflow (this repo)

This is the standard way to run readability over a chapter:
detect first, let Bruce vet the findings on disk, then apply only what he keeps.
It mirrors the existing `deep_review/` convention.

**Producing a review file.**
When asked to review a chapter rather than rewrite it in place,
do not touch `Chapters/NN_name.md`.
Write the findings to `readability/NN_name.md`,
a file whose name matches the chapter it reviews.
So `readability/12_Data_Classes_as_Types.md` reviews
`Chapters/12_Data_Classes_as_Types.md`.
Create the `readability/` directory if it does not exist.
When you first create it, add a `!Notes.md` file for Bruce's own use.
That file belongs to the human; never assume it holds instructions for you,
and do not act on its contents.

Each finding is a self-contained block that stands or falls on its own:
the section or line it applies to, the pattern name and number, the offending
text quoted, and the proposed change.

Order the blocks by decreasing importance, not by position in the chapter.
Importance means how much the finding needs Bruce's judgment:
first the critical issues where you cannot determine the right approach
and need his decision,
then, going down the file,
findings you are more and more able to resolve on your own.
Bruce reads the top of the file with full attention
and tends to accept the confident items lower down,
so a finding placed too low gets less scrutiny than it deserves.

End every block with a reject checkbox on its own line,
after the finding it governs:

> `[] Reject`

Putting it last means Bruce reads the case before the verdict,
so the checkbox sits where the decision gets made
rather than before he knows what it is about.

An empty `[]` means the change is live and will be applied.
Bruce rejects a change by putting an `X` in the box, `[X] Reject`, instead of
deleting the block. The rejected block stays in the file as a record, so a later
review can see the suggestion was already considered and declined.

Before writing findings, check for a completed review of the same chapter: the
most recent `~`-prefixed file for it (see Successive reviews below).
Any block marked `[X] Reject` there is a suggestion Bruce already declined, so
do not raise it again. Carry those rejections forward, so a new review does not
re-propose what a past one settled.

Begin the review file with this instruction, verbatim, so it travels with the
file:

> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

**Applying a review file.**
When Bruce hands the file back with an instruction like
`do readability/12_Data_Classes_as_Types.md`:

1. Read the review file. Apply every block whose checkbox is empty (`[]`).
   Skip every block marked `[X] Reject`; it is a declined suggestion kept as a
   record, not a change to make. Leave the rejected blocks in the file.
2. Apply the live changes to `Chapters/NN_name.md`, not to the review file.
   Respect the file-mode constraints above:
   never touch a fenced ```python block,
   keep Semantic Line Breaks in the prose,
   and leave code, frontmatter, and link targets alone.
3. Rename the review file to the next name in the completed-review series (see
   Successive reviews), which adds the leading `~` the file's own instruction
   calls for. Use `git mv` when the file is tracked. The `~` marks it done.
4. Remind Bruce to run `make verify`.

**Which variant to apply.**
A live block that offers several fixes gets the one the block recommends,
unless Bruce says otherwise.
He annotates a choice inline, in double brackets
(`[[do this]]`, `[[cut the parenthetical]]`),
and that annotation outranks the recommendation.

**A block that argues against itself is declined.**
When the recommendation is not "which fix" but "do not make this change at
all" (`I lean toward not doing this`, `I would not do it`,
`I do not recommend this`), leave the chapter alone even though the checkbox
is empty, and say in the report that the block was skipped for that reason.
An empty checkbox means Bruce did not veto it;
it does not mean he asked for a change the block itself argues against.
Only an explicit annotation turns such a block back on.

The cleaner move is to avoid the collision when writing the review:
a finding worth recording but not worth making belongs under a heading that
marks it as considered and declined, not in a live block.

A `~`-prefixed file in `readability/` is a completed review.
Leave it alone unless Bruce asks.

**Successive reviews.**
The active review is always the unprefixed `readability/NN_name.md`, and there
is at most one at a time. When a chapter is reviewed more than once, keep every
completed review as history by numbering them.
The first completed review is `readability/~12_Data_Classes_as_Types.md`,
the second `readability/~12_Data_Classes_as_Types.r2.md`,
the third `...r3.md`, and so on.
On completion, rename the active file to the next free number in that series.
The carry-forward step reads the most recent completed review, the
highest-numbered one, which already accumulates every earlier review's
`[X]` rejections.

## Process and Output

1. Read the input carefully and identify every instance of the patterns above.
2. Write a **draft rewrite**.
   Check that it reads naturally aloud, varies sentence length,
   prefers specific details and simple constructions (is/are/has),
   and keeps the appropriate register.
3. Ask two questions:
   **"What makes the text below so obviously AI generated?"** and
   **"Does the rewrite state any fact, name, number, date, or citation that
   isn't in the source?"**
   Answer briefly.
   A fabrication is a defect even when it sounds more human than the vague
   original.
4. Revise into a **final rewrite** that addresses both answers.

In pasted-text mode, deliver the draft, the brief "still-AI" bullets,
the final rewrite, and optionally a short summary of changes.
In file and embedded modes, run the same loop but deliver only what the mode
calls for.

## Reference

Adapted from [blader/humanizer](https://github.com/blader/humanizer),
which is based on
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
maintained by WikiProject AI Cleanup.
The patterns documented there come from observations of thousands of instances
of AI-generated text on Wikipedia.

Sections 34 to 67, the tiered vocabulary tables in §7, and the structure,
severity, and never-inject sections are folded in from
[conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)
(MIT license), adapted to neutral examples and Bruce's local rules.
The upstream skill's profile and tolerance matrix, its `--style` config engine,
and its Node detector are not included.

Sections 68 to 70, the portability test, the minimum-effective-edit and
protect-the-specific-fact principles, the empty-adverb and verb-strengthening
notes, the detect-only mode, and the fake-profound-kicker note are folded in from
[petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop)
(MIT license), adapted to Bruce's rules.
Its patterns that readability already covered (binary contrasts, importance
puffery, weasel attribution, copula avoidance, synonym cycling, dramatic
fragmentation, formatting slop) were not duplicated.

Key insight from Wikipedia:
"LLMs use statistical algorithms to guess what should come next.
The result tends toward the most statistically likely result that applies to
the widest variety of cases."

Local changes from upstream: §14 inverted (em dashes preserved, not stripped),
§17 exempted for book headings, §13 softened to advisory,
the em-dash false-positive bullet rewritten,
and repo-specific constraints added to file mode.
