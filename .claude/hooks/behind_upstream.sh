#!/usr/bin/env bash
# SessionStart hook: fetch, then warn when the current branch is behind
# its upstream. Prints nothing when the branch is current, when it has
# no upstream, or outside a git repository.
#
# The warning is JSON so that it reaches two readers: "systemMessage"
# shows it to the user, and "additionalContext" puts it in the model's
# context. When the fetch fails (offline), the comparison uses the
# upstream state from the last successful fetch.

GIT_TERMINAL_PROMPT=0 git fetch --quiet 2>/dev/null
upstream=$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null) || exit 0
branch=$(git rev-parse --abbrev-ref HEAD)
read -r ahead behind < <(
  git rev-list --left-right --count "HEAD...$upstream" 2>/dev/null
)
[ "${behind:-0}" -gt 0 ] || exit 0

plural=s
[ "$behind" -eq 1 ] && plural=
state="$branch is $behind commit$plural behind $upstream"
[ "${ahead:-0}" -gt 0 ] && state="$state and $ahead ahead"

printf '{"systemMessage": "%s. Pull before editing.", ' "$state"
printf '"hookSpecificOutput": {"hookEventName": "SessionStart", '
printf '"additionalContext": "%s (fetched at session start). ' "$state"
printf 'Before the first edit, tell Bruce and ask whether to pull. '
printf 'Edits made on a stale branch end in a merge."}}\n'
