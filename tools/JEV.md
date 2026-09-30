Create a skill command called /jev on to enable automated model routing. /jev turns it on, '/jev off' turns it off.

When active, do not use the default model immediately. Instead, process every user task in two steps:

1. System 1 Routing (Jev): Send the user's prompt to Jev. Ask Jev to evaluate the task's complexity and select the most efficient model from this menu of options:

- Haiku: For simple tasks, quick file path searches, basic local file manipulations, or executing standard uv package manager commands.

- Sonnet: For standard Python development, intermediate coding tasks, and moderate reasoning.

- Opus: Only for highly complex tasks, deep reasoning, or major architectural decisions.

- Fable: For the most difficult tasks

2. System 2 Execution: Once Jev outputs its selection, automatically route the user's original task to that specific model to execute the work and provide the final output.


---

Create a command called /jev-skills on to enable automated skill selection for this session.

When I assign a task that requires an external skill or tool, do not search through the workspace or skill library yourself. Instead, use the following two-step process:

1. System 1 Skill Classification (Jev): Send my task description and the complete list of available skills in my workspace to Jev. Instruct Jev to evaluate the task and output only the exact name of the single most relevant skill required to complete the task.

2. System 2 Execution (Claude): Once Jev outputs the skill name, immediately load that specific skill and proceed to execute my original task.
