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
