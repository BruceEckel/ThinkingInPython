# Start a working session on the book: the local preview server in the
# background, Claude Code in this window.
#
# Double-click Start-Book.cmd, which runs this file in a new PowerShell
# window. (Windows opens a double-clicked .ps1 in an editor, so the .cmd
# beside this file is the thing to click.)
#
#   1. This window is the parent.
#   2. `tip local` runs in a background job (Start-Job): it builds the
#      site, serves it at http://localhost:8000, and opens a browser tab
#      at the bookmarked place. Its output goes to build\tip-local.log.
#   3. `claude --dangerously-skip-permissions` runs in this window.
#
# Closing this window ends the server. Start-Job alone does not do that:
# `tip local` starts uv, which starts a Python supervisor, which starts
# the server, and Windows leaves those grandchildren running when the
# job's shell dies, still holding port 8000. So the job's shell joins a
# Windows job object marked kill-on-close before it starts `tip local`.
# This window holds the one handle to that object. When this process
# ends, for any reason, Windows closes the handle and ends every process
# in the object.
#
# One side effect: if no browser is running when `tip local` opens its
# tab, the browser it starts belongs to the job object too and closes
# with this window. A browser that is already running is unaffected.
#
# When Claude exits, the window stays open with the server running, so
# you can start `claude` again. `Receive-Job $BookServer` and the log
# file show what the server printed.
param(
    # The background command. `tip serve` skips the full site build.
    [string]$Background = 'tip local',
    # Start the server and stop there (for testing this script).
    [switch]$NoClaude
)

# The module-qualified name reaches the cmdlet when a profile defines a
# Set-Location function of its own, which lacks -LiteralPath.
Microsoft.PowerShell.Management\Set-Location -LiteralPath $PSScriptRoot
$Host.UI.RawUI.WindowTitle = 'Thinking in Python'

$native = @'
[DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
public static extern IntPtr CreateJobObject(IntPtr attributes, string name);
[DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
public static extern IntPtr OpenJobObject(uint access, bool inherit, string name);
[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool SetInformationJobObject(
    IntPtr job, int infoClass, IntPtr info, uint length);
[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
[DllImport("kernel32.dll")]
public static extern IntPtr GetCurrentProcess();
[DllImport("kernel32.dll", SetLastError = true)]
public static extern bool CloseHandle(IntPtr handle);
'@
$kernel = Add-Type -Namespace BookServer -Name Kernel -PassThru `
    -MemberDefinition $native

# The kill-on-close job object. JOBOBJECT_EXTENDED_LIMIT_INFORMATION is
# 144 bytes in a 64-bit process and 112 in a 32-bit one (the pwsh that
# comes first on PATH can be the x86 build), with LimitFlags at offset
# 16 in both; 0x2000 is JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, and 9 is
# the information class for that structure.
$jobName = "BookServer-$PID"
$global:BookServerHandle = $kernel::CreateJobObject([IntPtr]::Zero, $jobName)
$size = if ([IntPtr]::Size -eq 8) { 144 } else { 112 }
$info = [Runtime.InteropServices.Marshal]::AllocHGlobal($size)
try {
    [Runtime.InteropServices.Marshal]::Copy([byte[]]::new($size), 0, $info, $size)
    [Runtime.InteropServices.Marshal]::WriteInt32($info, 16, 0x2000)
    $limited = $kernel::SetInformationJobObject(
        $global:BookServerHandle, 9, $info, $size)
} finally {
    [Runtime.InteropServices.Marshal]::FreeHGlobal($info)
}
if ($global:BookServerHandle -eq [IntPtr]::Zero -or -not $limited) {
    Write-Warning ('Could not create the kill-on-close job object. ' +
        'The server will start, and may outlive this window.')
}

$log = Join-Path $PSScriptRoot 'build\tip-local.log'
New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null

$global:BookServer = Start-Job -Name BookServer `
    -WorkingDirectory $PSScriptRoot `
    -ArgumentList $native, $jobName, $Background, $log -ScriptBlock {
    param($native, $jobName, $command, $log)
    # Join the job object first, so every process started below is in it.
    # This shell then closes its own handle: the parent window's handle
    # must be the last one, or the object would outlive the window.
    $kernel = Add-Type -Namespace BookServer -Name Kernel -PassThru `
        -MemberDefinition $native
    $handle = $kernel::OpenJobObject(0x1F001F, $false, $jobName)
    if ($handle -ne [IntPtr]::Zero) {
        [void]$kernel::AssignProcessToJobObject(
            $handle, $kernel::GetCurrentProcess())
        [void]$kernel::CloseHandle($handle)
    }
    Invoke-Expression "$command *> '$log'"
}

Write-Host "Started '$Background' in the background (job BookServer)."
Write-Host "Its output: $log"
Write-Host 'Closing this window stops the server.'
Write-Host ''

if (-not $NoClaude) {
    claude --dangerously-skip-permissions
}
