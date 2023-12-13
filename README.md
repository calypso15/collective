# Setup
Open a Powershell prompt *as administrator* and run:
```
cd $env:USERPROFILE\Desktop; Invoke-WebRequest -URI https://raw.githubusercontent.com/calypso15/collective/main/join-collective.ps1 -OutFile join-collective.ps1 -Headers @{"Cache-Control"="no-cache"}; powershell -ExecutionPolicy Bypass -File join-collective.ps1
```
