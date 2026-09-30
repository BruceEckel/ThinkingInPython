# Jev

## Prose Quality

Five public tools use Jev to judge prose quality.
Only one of them, Sniff Test, is a Claude Code skill.
Two others overlap with it:
claude-x-jev uses Jev as a gate on Claude's drafts,
and Clarity Judge runs a similar set of checks as a web app.
The curated list at [awesome-jev-tools](https://github.com/v-modal/awesome-jev-tools)
is the place to watch for new ones.

### Claude Code skills

- [Sniff Test](https://github.com/DanRWilloughby/snifftest):
  a prose linter that runs as a CLI, a pre-commit hook, a GitHub Action,
  or a Claude Code skill (`/snifftest draft.md`).
  It asks Jev one yes/no question per rule per paragraph.
  The five default rules are "not X but Y" turns, three-item cadences,
  stacked hedges, rhetorical openers,
  and closing sentences that restate the paragraph.
  It flags at 0.7 confidence and reports readings between 0.4 and 0.6
  as "no judgment" rather than guessing.
  By default it runs only the rules it can check locally by counting,
  and it sends text to Jev only when asked to.
  Its own measurement on 166 paragraphs:
  it caught 63 of 80 planted faults,
  flagged 1 of 54 clean paragraphs wrongly,
  and cost about $0.013 per 100 paragraphs.
- [claude-x-jev](https://github.com/charlesdove977/claude-x-jev):
  its `/jev-verify` preset checks a draft Claude wrote against three things:
  whether it is supported by its source, whether it follows the given rules,
  and whether the tone is right.
  One failed check sends the draft back to Claude.
  It reports no accuracy figures for this use.

### Other tools

- [Clarity Judge](https://github.com/TypeSafeAI/clarity-judge):
  a Next.js web app,
  a community project despite sitting in the TypeSafeAI GitHub organization.
  It asks seven questions: hedging, em-dash overuse,
  whether the main point comes first, filler, tone, passive voice,
  and actionability.
  It flags at 0.7 and reports no accuracy figures.
- [JevSlop](https://github.com/TKY-27/JevSlop):
  scores an article on eight axes in one request
  and combines them into a 0–100 "Slop Score".
- [slop-grader](https://github.com/lukstei/slop-grader):
  a CLI that grades files against custom rulesets and flags individual lines.
- [pagegrade](https://github.com/kitze/pagegrade):
  grades page sections for clarity, writing quality, and SEO.

### Fit with this repo

These tools ask Jev fixed yes/no or pick-one questions about each paragraph,
so none of them rewrites anything.
That suits the style rules that a regex or Vale cannot settle
but a yes/no question can,
such as imperative-plus-consequence sentences,
a preposition stranded at the end of a sentence,
or a "that" whose referent is ambiguous.
Sniff Test's rules for stacked hedges and restating closers
overlap with the book's own list.

### Sniff Test on this book (2026-09-30)

Sniff Test 0.1.0, installed from npm, ran twice.
Neither run found a fault worth fixing.

- **Chapter 30, all default rules:**
  it flagged 10 paragraphs, and `tip prose CH=30` flagged none,
  so the two tools share no flags.
  Eight flags came from `sentence_rhythm`,
  which fired on paragraphs whose sentences run 10 to 28 words,
  the varied length the book's style asks for.
  One came from `colon_heavy`: a dense paragraph
  whose colons each introduce a list or a code span.
  The one judgment flag, `not_x_but_y`,
  fell on "declares an attribute rather than creating one,"
  where the contrast is the claim.
  The run cost $0.007.
- **The whole book, `tricolon` and `stacked_hedging` only:**
  49 chapters, 3,263 paragraphs, $0.12, 8 minutes.
  Two flags, both false positives.
  `stacked_hedging` fired on "Other examples:",
  a lead-in line with no hedge in it.
  Sniff Test splits paragraphs at blank lines with no minimum length,
  so all five of this rule's highest readings in the book were fragments like that one.
  `tricolon` fired on three distinct events in chapter 38.
  Of the six readings between 0.6 and 0.7,
  none was a fault on a second read.

Generic prose rules do not fit this book.
The faults Sniff Test hunts are ones the book's prose passes clear,
and the constructions it matches are mostly deliberate.
A Jev question earns its place when it asks about a fault this book commits,
which is how `tools/edit_patterns.py` works:
each of its questions comes from a sentence Bruce rewrote,
and the ones he has labeled carry a floor calibrated against those labels.
Asking Jev about the global writing rules follows the same approach:

```
Using the typesafe:typesafe-ai skill, prototype a report-only tool in tools/ that asks Jev one Boolean per sentence for three of my style rules (imperative-plus-consequence, stranded preposition, ambiguous sentence-opening "This"), threshold 0.7 with a 0.4-0.6 no-judgment band like Sniff Test. Run it on chapter 30 and show me the hits before wiring it into anything.
```

### Checking prose claims against listings (2026-09-30)

A prototype, `tools/listing_claims.py`,
paired each sentence that names a listing,
or a name a listing uses,
with that listing,
and asked Jev whether the listing supports, contradicts, or says nothing about the sentence.
The test set was the correctness sweep of 2026-09-02,
which fixed 30 false claims in chapters 29-47.
Three versions ran:

| Version | Sweep errors reached / flagged | Flags in chapters 30-47 | Real among flags checked |
|---|---|---|---|
| Listings in the sentence's section | 11 / 2 | 36 | 0 of 16 |
| Plus the listing that defines each name | 15 / 2 | 45 | not checked; the same false alarms returned |
| Location and named-file claims only | 4 / 1 | 12 | 1 of 12 |

Half the sweep's errors are claims about runtime or type-checker behavior, or about another chapter,
so no reading of a listing can settle them.
The false alarms were true sentences that take one or two steps of reasoning about code:
an inherited method, a loop that never runs, a library class the listing subclasses.
Jev reads each pair in one pass and does not take those steps.
The one real find was a wording slip in chapter 42,
and the tool was deleted.
An Opus agent per chapter, which found all 30 of the sweep's errors,
stays the way to check claims.
Jev fits this book where the question is local and needs no reasoning about code,
as in `grounding_triage` and `link_support`.

## Routing with Jev

Two personal skills route each prompt through Jev before Claude acts on it:
`/jev` picks the model, and `/jev-skills` picks the skill.
Both live outside this repo, in `~/.claude/skills/`,
so they apply to every project on this machine.

### Where it lives

- `~/.claude/skills/jev/jev.py`: the one script behind both.
  It toggles each mode, lists the skills Jev chooses among,
  and runs as the hook.
  It uses the standard library alone
  and reads the key from `TYPESAFE_API_KEY`,
  falling back to the Windows registry (`HKCU\Environment`).
- `~/.claude/skills/jev/SKILL.md` and `~/.claude/skills/jev-skills/SKILL.md`:
  the two commands, plus the rules Claude follows when a pick arrives.
- `~/.claude/settings.json`: a `UserPromptSubmit` hook
  runs `python "$HOME/.claude/skills/jev/jev.py" hook` on each prompt,
  with a 12-second timeout.

### On and off

Each mode is a flag file beside `jev.py`
(`routing_on` and `skills_on`),
so a switch holds for every session on the machine, not only the current one.

| Command | Effect |
|---|---|
| `/jev` or `/jev on` | turn model routing on |
| `/jev off` | turn it off |
| `/jev status` | report whether it is on and whether the key is set |
| `/jev-skills` or `/jev-skills on` | turn skill selection on |
| `/jev-skills off` | turn it off |
| `/jev-skills status` | report it |

The script runs directly too:
`python ~/.claude/skills/jev/jev.py route "task"` or `skill "task"`
prints Jev's answer for one task,
and `skills list` prints the skills Jev chooses among for the current project.

### What the hook does

For each prompt that does not start with `/`,
the hook sends the prompt to Jev with a `choice` question for each mode that is on.
With both on, one request asks both questions.
The answers come back as context lines on the prompt,
with the pick, its confidence, and the top four probabilities:
`Jev routing: Jev picked **haiku** (confidence 0.89; ...)`.
If the call fails, the context line says so,
and Claude handles the prompt normally.

Model routing chooses among Haiku, Sonnet, Opus, and Fable,
each described in `MODELS` in `jev.py` by what it is for and what it is not for.
The question tells Jev to prefer the cheaper model when two would both succeed.
When the pick differs from the session's model,
Claude delegates the whole task to one `Agent` call on the picked model.
It overrides the pick only when the task depends on conversation context
that no prompt could carry,
or when a project's `CLAUDE.md` routing table pins that work to a model,
and says why in one line.

Skill selection offers Jev every skill Claude could load for the project,
plus `none`, with each description cut to 600 characters.
Skills marked `disable-model-invocation` or switched off in `skillOverrides`
are left out.
Claude Code's built-in skills have no file on disk, so Jev never picks one.
Claude loads the picked skill before any other step,
except when the user named a skill,
or when the skill's description limits it to explicit requests.

### The prompts that built it

These two prompts, pasted into Claude Code, produced the skills this section describes.

Model routing (`/jev`):

```
Create a skill command called /jev on to enable automated model routing. /jev turns it on, '/jev off' turns it off.

When active, do not use the default model immediately. Instead, process every user task in two steps:

1. System 1 Routing (Jev): Send the user's prompt to Jev. Ask Jev to evaluate the task's complexity and select the most efficient model from this menu of options:

- Haiku: For simple tasks, quick file path searches, basic local file manipulations, or executing standard uv package manager commands.

- Sonnet: For standard Python development, intermediate coding tasks, and moderate reasoning.

- Opus: Only for highly complex tasks, deep reasoning, or major architectural decisions.

- Fable: For the most difficult tasks

2. System 2 Execution: Once Jev outputs its selection, automatically route the user's original task to that specific model to execute the work and provide the final output.
```

Skill selection (`/jev-skills`):

```
Create a command called /jev-skills on to enable automated skill selection for this session.

When I assign a task that requires an external skill or tool, do not search through the workspace or skill library yourself. Instead, use the following two-step process:

1. System 1 Skill Classification (Jev): Send my task description and the complete list of available skills in my workspace to Jev. Instruct Jev to evaluate the task and output only the exact name of the single most relevant skill required to complete the task.

2. System 2 Execution (Claude): Once Jev outputs the skill name, immediately load that specific skill and proceed to execute my original task.
```
