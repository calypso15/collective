[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $ConfigFile,

    [Parameter()]
    [string]
    $Step
)

function Confirm-ShouldRun([string] $TargetStep) {
    if ($global:Step -eq $TargetStep -or $null -eq $global:Step) {
        $global:Running = $true
    }

    return $global:Running
}

if ('ConfigFile' -NotIn $PSBoundParameters.Keys) {
    Write-Host 'No config file specified with the -ConfigFile parameter, aborting.'
    Exit
}

$ConfigFile = Resolve-Path $ConfigFile
$Config = Get-Content $ConfigFile | ConvertFrom-Json

# NEED PS v7 for Test-Json schema validation

if ('Step' -NotIn $PSBoundParameters.Keys) {
    $Step = $null
}

$EnableAutologon = $Config.Windows.EnableAutologon
$Username = $Config.Windows.Username
$Password = $Config.Windows.Password

$Running = $false

Write-Host 'Disabling sleep...'
powercfg /x -standby-timeout-ac 0
powercfg /x -hibernate-timeout-ac 0

if (Confirm-ShouldRun "Enable-Autologon") {
    $RegistryPath = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon'
    if ((Get-ItemProperty $RegistryPath -ErrorAction SilentlyContinue | Select-Object -ErrorAction SilentlyContinue -ExpandProperty AutoAdminLogon) -ne "1") {
        if ($EnableAutologon) {
            Write-Host('Enabling autologon...')

            $Computer = $env:COMPUTERNAME

            Add-Type -AssemblyName System.DirectoryServices.AccountManagement
            $obj = New-Object System.DirectoryServices.AccountManagement.PrincipalContext('machine', $Computer)

            if ($true -eq $obj.ValidateCredentials($Username, $Password)) {
                Set-ItemProperty $RegistryPath 'AutoAdminLogon' -Value "1" -Type String
                Set-ItemProperty $RegistryPath 'DefaultUsername' -Value "$Username" -type String
                Set-ItemProperty $RegistryPath 'DefaultPassword' -Value "$Password" -type String
            }
            else {
                Write-Host 'Invalid credentials, moving on.'
            }
        }
    }
}

if (Confirm-ShouldRun "Install-Packages") {
    # Install other chocolatey packages
    Set-Location $HOME/Documents/collective/choco

    Write-Host('Installing chocolatey packages...')
    Invoke-Command -ScriptBlock {
        choco install packages.config --yes
    }

    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

    if ($LastExitCode -eq 3010) {
        Write-Host 'Restarting system...'
        Register-ScheduledTask -TaskName "Resume-Setup" -Principal (New-ScheduledTaskPrincipal -UserID $env:USERNAME -RunLevel Highest -LogonType Interactive) -Trigger (New-ScheduledTaskTrigger -AtLogon) -Action (New-ScheduledTaskAction -Execute "${Env:WinDir}\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument ("-NoExit -ExecutionPolicy Bypass -File `"$PSCommandPath`" -ConfigFile `"$ConfigFile`" -Step: Run-Python-Setup")) -Force;
        Restart-Computer
    }
}

if (Confirm-ShouldRun "Run-Python-Setup") {
    Unregister-ScheduledTask -TaskName "Resume-Setup" -Confirm:$false -ErrorAction SilentlyContinue

    # Start python script
    Set-Location $HOME/Documents/collective/python

    Write-Host('Starting Python setup...')
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python setup.py $ConfigFile
    Write-Host('')
}

if ($LastExitCode -ne 0) {
    throw 'Setup failed, aborting.'
}
