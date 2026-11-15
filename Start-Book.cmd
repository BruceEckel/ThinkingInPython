@echo off
rem Double-click this file. It opens a PowerShell window that starts the
rem preview server in the background and Claude Code in the window.
rem Start-Book.ps1 beside this file does the work and explains it.
rem
rem The 64-bit pwsh is named by its path, because the 32-bit build can
rem come first on PATH. ProgramW6432 is the 64-bit Program Files folder
rem in a 32-bit and a 64-bit cmd alike. Without that file, use PATH.
set "BOOK_PWSH=%ProgramW6432%\PowerShell\7\pwsh.exe"
if not exist "%BOOK_PWSH%" set "BOOK_PWSH=pwsh"
"%BOOK_PWSH%" -NoLogo -NoExit -ExecutionPolicy Bypass -File "%~dp0Start-Book.ps1"
