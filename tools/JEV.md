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

Two follow-ups, each a prompt to paste:

1. Compare Sniff Test's catch rate with what `tip prose` already reports on a chapter:

   ```
   Clone DanRWilloughby/snifftest into the scratchpad, run it in dry-run and full mode on Chapters/30_Patterns--Observer.md, and compare what it flags with what `tip prose CH=30` flags. Report overlap, new catches, and false positives; change nothing in the repo.
   ```

2. Build a small checker for the global writing rules,
   most of which only judgment can answer:

   ```
   Using the typesafe:typesafe-ai skill, prototype a report-only tool in tools/ that asks Jev one Boolean per sentence for three of my style rules (imperative-plus-consequence, stranded preposition, ambiguous sentence-opening "This"), threshold 0.7 with a 0.4-0.6 no-judgment band like Sniff Test. Run it on chapter 30 and show me the hits before wiring it into anything.
   ```

## Basic

### `/jev`: model routing

Create a skill command, `/jev on`, to enable automated model routing.
`/jev on` turns it on, `/jev off` turns it off.

When active, do not use the default model immediately.
Instead, process every user task in two steps:

1. System 1 Routing (Jev):
   Send the user's prompt to Jev.
   Ask Jev to evaluate the task's complexity
   and select the most efficient model from this menu of options:
   - Haiku: for simple tasks, quick file path searches,
     basic local file manipulations,
     or executing standard uv package manager commands.
   - Sonnet: for standard Python development, intermediate coding tasks,
     and moderate reasoning.
   - Opus: only for highly complex tasks, deep reasoning,
     or major architectural decisions.
   - Fable: for the most difficult tasks.
2. System 2 Execution:
   Once Jev outputs its selection,
   automatically route the user's original task to that specific model
   to execute the work and provide the final output.

### `/jev-skills`: skill selection

Create a command, `/jev-skills on`, to enable automated skill selection for this session.

When I assign a task that requires an external skill or tool,
do not search through the workspace or skill library yourself.
Instead, use the following two-step process:

1. System 1 Skill Classification (Jev):
   Send my task description and the complete list of available skills
   in my workspace to Jev.
   Instruct Jev to evaluate the task
   and output only the exact name of the single most relevant skill
   required to complete the task.
2. System 2 Execution (Claude):
   Once Jev outputs the skill name,
   immediately load that specific skill
   and proceed to execute my original task.
