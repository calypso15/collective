param($Step=$null)
$Run = $false

if($Step -eq "Install-Packages" -or $Run -eq $true -or $Step -eq $null)
{
    $Run = $true

    # Install other chocolatey packages
    Set-Location $HOME/Documents/go-nuclear/choco

    Write-Host('Installing chocolatey packages...')
    Invoke-Command -ScriptBlock {
        choco install packages.config --yes
    }

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    Register-ScheduledTask -TaskName "Resume-Setup" -Principal (New-ScheduledTaskPrincipal -UserID $env:USERNAME -RunLevel Highest -LogonType Interactive) -Trigger (New-ScheduledTaskTrigger -AtLogon) -Action (New-ScheduledTaskAction -Execute "${Env:WinDir}\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument ("-NoExit -ExecutionPolicy Bypass -File `"" + $PSCommandPath + "`" Start-Python")) -Force;
    Restart-Computer
}

if($Step -eq "Start-Python" -or $Run -eq $true)
{
    $Run = $true
    Unregister-ScheduledTask -TaskName "Resume-Setup" -Confirm:$false

    # Start python script
    Set-Location $HOME/Documents/go-nuclear/python

    Write-Host('Starting Python setup...')
    pip install -r requirements.txt
    python setup.py
    Write-Host('')
}

if($LastExitCode -ne 0) {
    throw 'Setup failed, aborting.'
}
