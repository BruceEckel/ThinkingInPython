# Puts the command the `make` menu ran into this PowerShell session's
# history, so Up-arrow repeats it without going through the menu again.
#
# Dot-source this from $PROFILE (one line):
#     . C:\git\ThinkingInPython\tools\menu_history.ps1
#
# Why a wrapper: the menu (tools/help_picker.py) runs inside make, and a
# child process cannot add to the shell's live history. Without this it
# appends the command to PSReadLine's history file instead, which
# PSReadLine merges in only when it next writes, so the entry shows
# after your next command rather than on the next Up. This function
# names a scratch file in MAKE_MENU_RECORD, runs the real make.exe, and
# feeds whatever the menu wrote there to PSReadLine's AddToHistory,
# which is immediate. With the variable set, the menu leaves the
# history file alone, so nothing is recorded twice.
function make {
    $record = Join-Path ([IO.Path]::GetTempPath()) `
        ("make-menu-" + [IO.Path]::GetRandomFileName())
    $env:MAKE_MENU_RECORD = $record
    try {
        $exe = (Get-Command make -CommandType Application |
                Select-Object -First 1).Source
        & $exe @args
    }
    finally {
        Remove-Item Env:MAKE_MENU_RECORD -ErrorAction SilentlyContinue
        if (Test-Path $record) {
            foreach ($line in Get-Content $record) {
                if (-not $line) { continue }
                try {
                    [Microsoft.PowerShell.PSConsoleReadLine]::AddToHistory($line)
                }
                catch {
                    # No PSReadLine (a non-interactive host): nothing to add to.
                }
            }
            Remove-Item $record -ErrorAction SilentlyContinue
        }
    }
}
