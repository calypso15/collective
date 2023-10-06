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

netdom renamecomputer 192.168.192.20 /newname:Enterprise-ABCD /userd:"starfleet.corp\jeanluc" /passwordd:"Sentinelone!" /force /reboot 0
netdom renamecomputer 192.168.192.21 /newname:Melbourne-ABCD /userd:"starfleet.corp\jeanluc" /passwordd:"Sentinelone!" /force /reboot 0
netdom renamecomputer 192.168.192.22 /newname:Saratoga-ABCD /userd:"starfleet.corp\jeanluc" /passwordd:"Sentinelone!" /force /reboot 0