@echo off
rem Double-click this file. It opens a PowerShell window that starts the
rem preview server in the background and Claude Code in the window.
rem Start-Book.ps1 beside this file does the work and explains it.
pwsh -NoLogo -NoExit -ExecutionPolicy Bypass -File "%~dp0Start-Book.ps1"
