param($Step=$null)
$Running = $false

function Should-Run([string] $TargetStep)
{
    if ($global:Step -eq $TargetStep -or $global:Step -eq $null) {
        $global:Running = $true
    }

    return $global:Running
}

if(Should-Run "Enable-Autologon")
{
    $enable = Read-Host 'Enable autologin [y/n]? '
    if($enable -eq "y")
    {
        $Username = Read-Host 'Username: '
        $Password = Read-Host "Password: " -AsSecureString
        $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password);
        $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
        $RegistryPath = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
        Set-ItemProperty $RegistryPath 'AutoAdminLogon' -Value "1" -Type String
        Set-ItemProperty $RegistryPath 'DefaultUsername' -Value "$Username" -type String
        Set-ItemProperty $RegistryPath 'DefaultPassword' -Value "$Password" -type String
    }
}

if(Should-Run "Install-Packages")
{
    # Install other chocolatey packages
    Set-Location $HOME/Documents/go-nuclear/choco

    Write-Host('Installing chocolatey packages...')
    Invoke-Command -ScriptBlock {
        choco install packages.config --yes
    }

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    Register-ScheduledTask -TaskName "Resume-Setup" -Principal (New-ScheduledTaskPrincipal -UserID $env:USERNAME -RunLevel Highest -LogonType Interactive) -Trigger (New-ScheduledTaskTrigger -AtLogon) -Action (New-ScheduledTaskAction -Execute "${Env:WinDir}\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument ("-NoExit -ExecutionPolicy Bypass -File `"" + $PSCommandPath + "`" Run-Python-Setup")) -Force;
    Restart-Computer
}

if(Should-Run "Run-Python-Setup")
{
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
