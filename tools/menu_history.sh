# Puts the command the `make` menu ran into this shell's history, so
# Up-arrow repeats it without going through the menu again. bash and
# zsh.
#
# Source this from ~/.bashrc or ~/.zshrc (one line):
#     . /c/git/ThinkingInPython/tools/menu_history.sh
#
# Why a wrapper: the menu (tools/help_picker.py) runs inside make, and a
# child process cannot add to the shell's live history. Without this it
# appends the command to the history file, which bash reads only at
# startup and zsh only with SHARE_HISTORY or INC_APPEND_HISTORY. This
# function names a scratch file in MAKE_MENU_RECORD, runs the real
# make, and feeds whatever the menu wrote there to `history -s` (bash)
# or `print -s` (zsh), which is immediate. With the variable set, the
# menu leaves the history file alone, so nothing is recorded twice.
make() {
    local record status line
    record="$(mktemp "${TMPDIR:-/tmp}/make-menu.XXXXXX")" || {
        command make "$@"
        return
    }
    MAKE_MENU_RECORD="$record" command make "$@"
    status=$?
    if [ -s "$record" ]; then
        while IFS= read -r line || [ -n "$line" ]; do
            [ -n "$line" ] || continue
            if [ -n "${ZSH_VERSION-}" ]; then
                print -s -- "$line"
            else
                history -s -- "$line"
            fi
        done < "$record"
    fi
    rm -f "$record"
    return "$status"
}
