@echo off
set suffix=%1

:: Verify that the user has administrative rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrator user - OK
) else (
    echo This script must be run as an Administrator.
    pause
    exit /b
)

:: Rename the computer
echo Renaming the computer...

netdom computername 192.168.192.10 /add:TheBorg-%suffix%.starfleet.corp
netdom computername 192.168.192.10 /makeprimary:TheBorg-%suffix%.starfleet.corp
shutdown /r /t 0